# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""HLS Playlist OpenTimelineIO adapter

This adapter supports authoring of HLS playlists within OpenTimelineIO by using
clips to represent media fragments.

Status:
    - Export of Media Playlists well supported
    - Export of Master Playlists supported
    - Import of Media Playlists well supported
    - Import of Master Playlists unsupported
    - Explicit Variant Stream controls in Master Playlists unsupported

In general, you can author otio as follows:
    t = otio.schema.Timeline()
    track = otio.schema.Track("v1")
    track.metadata['HLS'] = {
        "EXT-X-INDEPENDENT-SEGMENTS": None,
        "EXT-X-PLAYLIST-TYPE": "VOD"
    }
    t.tracks.append(track)

    # Make a prototype media ref with the fragment's initialization metadata
    fragmented_media_ref = otio.schema.ExternalReference(
        target_url='video1.mp4',
        metadata={
            "streaming": {
                "init_byterange": {
                    "byte_count": 729,
                    "byte_offset": 0
                },
                "init_uri": "media-video-1.mp4"
            }
        }
    )

    # Make a copy of the media ref specifying the byte range for the fragment
    media_ref1 = fragmented_media_ref.deepcopy()
    media_ref1.available_range=otio.opentime.TimeRange(
        otio.opentime.RationalTime(0, 1),
        otio.opentime.RationalTime(2.002, 1)
    )
    media_ref1.metadata['streaming'].update(
        {
            "byte_count": 534220,
            "byte_offset": 1361
        }
    )

    # make the fragment and append it
    fragment1 = otio.schema.Clip(media_reference=media_ref1)
    track.append(fragment1)

    # (repeat to define each fragment)

The code above would yield an HLS playlist like:
    #EXTM3U
    #EXT-X-VERSION:7
    #EXT-X-TARGETDURATION:2
    #EXT-X-PLAYLIST-TYPE:VOD
    #EXT-X-INDEPENDENT-SEGMENTS
    #EXT-X-MEDIA-SEQUENCE:1
    #EXT-X-MAP:BYTERANGE="729@0",URI="media-video-1.mp4"
    #EXTINF:2.00200,
    #EXT-X-BYTERANGE:534220@1361
    video1.mp4
    #EXT-X-ENDLIST

If you add min_segment_duration and max_segment_duration to the timeline's
metadata dictionary as RationalTime objects, you can control the rule set
deciding how many fragments to accumulate into a single segment. When nothing
is specified for these metadata keys, the adapter will create one segment per
fragment.

In general, any metadata added to the track metadata dict under the HLS
namespace will be included at the top level of the exported playlist (see
``EXT-X-INDEPENDENT-SEGMENTS`` and ``EXT-X-PLAYLIST-TYPE`` in the example
above). Each segment will pass through any metadata in the HLS namespace from
the media_reference.

If you write a Timeline with more than one track specified, then the adapter
will create an HLS master playlist.

The following track metadata keys will be used to inform exported master
playlist metadata per variant stream:
    bandwidth
    codec
    language
    mimeType
    group_id (audio)
    autoselect (audio)
    default (audio)
These values are translated to EXT-X-STREAM-INF and EXT-X-MEDIA
attributes as defined in sections 4.3.4.2 and 4.3.4.1 of
draft-pantos-http-live-streaming, respectively.
"""

import re
import copy

import opentimelineio as otio

# TODO: determine output version based on features used
OUTPUT_PLAYLIST_VERSION = "7"

# TODO: make sure all strings get sanitized through encoding and decoding
PLAYLIST_STRING_ENCODING = "utf-8"

"""
Matches a single key/value pair from an HLS Attribute List.
See section 4.2 of draft-pantos-http-live-streaming for more detail.
"""
ATTRIBUTE_RE = re.compile(
    r'(?P<AttributeName>[A-Z0-9-]+)' + r'\=' +
    r'(?P<AttributeValue>(?:\"[^\r\n"]*\")|[^,]+)' + r',?'
)

"""
Matches AttributeValue of the above regex into appropriate data types.
Note that these are meant to be joined using regex "or" in this order.
"""
_ATTRIBUTE_RE_VALUE_STR_LIST = [
    r'(?P<resolution>(?P<width>[0-9]+)x(?P<height>[0-9]+))\Z',
    r'(?P<hexcidecimal>0[xX](?P<hex_value>[0-9A-F]+))\Z',
    r'(?P<floating_point>-?[0-9]+\.[0-9]+)\Z',
    r'(?P<decimal>[0-9]+)\Z',
    r'(?P<string>\"(?P<string_value>[^\r\n"]*)\")\Z',
    r'(?P<enumerated>[^",\s]+)\Z'
]
ATTRIBUTE_VALUE_RE = re.compile("|".join(_ATTRIBUTE_RE_VALUE_STR_LIST))

"""
Matches a byterange as used in various contexts.
See section 4.3.2.2 of draft-pantos-http-live-streaming for an example use of
this byterange form.
"""
BYTERANGE_RE = re.compile(r'(?P<n>\d+)(?:@(?P<o>\d+))?')

"""
Matches HLS Playlist tags or comments, respective.
See section 4.1 of draft-pantos-http-live-streaming for more detail.
"""
TAG_RE = re.compile(
    r'#(?P<tagname>EXT[^:\s]+)(?P<hasvalue>:?)(?P<tagvalue>.*)'
)
COMMENT_RE = re.compile(r'#(?!EXT)(?P<comment>.*)')


class AttributeListEnum(str):
    """ A subclass allowing us to differentiate enums in HLS attribute lists
    """


def _value_from_raw_attribute_value(raw_attribute_value):
    """
    Takes in a raw AttributeValue and returns an appopritate Python type.
    If there is a problem decoding the value, None is returned.
    """
    value_match = ATTRIBUTE_VALUE_RE.match(raw_attribute_value)
    if not value_match:
        return None

    group_dict = value_match.groupdict()
    # suss out the match
    for k, v in group_dict.items():
        # not a successful group match
        if v is None:
            continue

        # decode the string
        if k == 'resolution':
            return v
        elif k == 'enumerated':
            return AttributeListEnum(v)
        elif k == 'hexcidecimal':
            return int(group_dict['hex_value'], base=16)
        elif k == 'floating_point':
            return float(v)
        elif k == 'decimal':
            return int(v)
        elif k == 'string':
            # grab only the data within the quotes, excluding the quotes
            string_value = group_dict['string_value']
            return string_value

    return None


class AttributeList(dict):
    """
    Dictionary-like object representing an HLS AttributeList.
    See section 4.2 of draft-pantos-http-live-streaming for more detail.
    """

    def __init__(self, other=None):
        """
        contstructs an :class:`AttributeList`.

        ``Other`` can be either another dictionary-like object or a list of
        key/value pairs
        """
        if not other:
            return

        try:
            items = other.items()
        except AttributeError:
            items = other

        for k, v in items:
            self[k] = v

    def __str__(self):
        """
        Construct attribute list string as it would exist in an HLS playlist.
        """
        attr_list_entries = []
        # Use a sorted version of the dictionary to ensure consistency
        for k, v in sorted(self.items(), key=lambda i: i[0]):
            out_value = ''
            if isinstance(v, AttributeListEnum):
                out_value = v
            elif isinstance(v, str):
                out_value = f'"{v}"'
            else:
                out_value = str(v)

            attr_list_entries.append(f'{k}={out_value}')

        return ','.join(attr_list_entries)

    @classmethod
    def from_string(cls, attrlist_string):
        """
        Accepts an attribute list string and returns an :class:`AttributeList`.

        The values will be transformed to Python types.
        """
        attr_list = cls()
        match = ATTRIBUTE_RE.search(attrlist_string)
        while match:
            # unpack the values from the match
            group_dict = match.groupdict()
            name = group_dict['AttributeName']
            raw_value = group_dict['AttributeValue']

            # parse the raw value
            value = _value_from_raw_attribute_value(raw_value)
            attr_list[name] = value

            # search for the next attribute in the string
            match_end = match.span()[1]
            match = ATTRIBUTE_RE.search(attrlist_string, match_end)

        return attr_list


# some special top-levle keys that HLS metadata will be decoded into
FORMAT_METADATA_KEY = 'HLS'
"""
Some concepts are translatable between HLS and other streaming formats (DASH).
These metadata keys are used on OTIO objects outside the HLS namespace because
they are higher level concepts.
"""
STREAMING_METADATA_KEY = 'streaming'
INIT_BYTERANGE_KEY = 'init_byterange'
INIT_URI_KEY = 'init_uri'
SEQUENCE_NUM_KEY = 'sequence_num'
BYTE_OFFSET_KEY = 'byte_offset'
BYTE_COUNT_KEY = 'byte_count'


class Byterange:
    """Offers interpretation of HLS byte ranges in various forms."""

    count = None
    """(:class:`int`) Number of bytes included in the range."""

    offset = None
    """(:class:`int`) Byte offset at which the range starts."""

    def __init__(self, count=None, offset=None):
        """Constructs a :class:`Byterange` object.

        :param count: (:class:`int`) Number of bytes included in the range.
        :param offset: (:class:`int`) Byte offset at which the range starts.
        """
        self.count = (count if count is not None else 0)
        self.offset = offset

    def __eq__(self, other):
        if not isinstance(other, Byterange):
            # fall back on identity, this should always be False
            return (self is other)
        return (self.count == other.count and self.offset == other.offset)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '{}(offset = {}, count = {})'.format(
            type(self),
            str(self.offset),
            str(self.count)
        )

    def __str__(self):
        """returns a string in HLS format"""

        out_str = str(self.count)
        if self.offset is not None:
            out_str += f'@{str(self.offset)}'

        return out_str

    def to_dict(self):
        """Returns a dict suitable for storing in otio metadata.

        :return: (:class:`dict`) serializable version of byterange.
        """
        range_dict = {BYTE_COUNT_KEY: self.count}
        if self.offset is not None:
            range_dict[BYTE_OFFSET_KEY] = self.offset

        return range_dict

    @classmethod
    def from_string(cls, byterange_string):
        """Construct a :class:`Byterange` given a string in HLS format.

        :param byterange_string: (:class:`str`) a byterange string.
        :return: (:class:`Byterange`) The instance for the provided string.
        """
        m = BYTERANGE_RE.match(byterange_string)

        return cls.from_match_dict(m.groupdict())

    @classmethod
    def from_match_dict(cls, match_dict):
        """
        Construct a :class:`Byterange` given a groupdict from ``BYTERANGE_RE``

        :param match_dict: (:class:`dict`) the ``match_dict``.
        :return: (:class:`Byterange`) The instance for the provided string.
        """
        byterange = cls(count=int(match_dict['n']))

        try:
            byterange.offset = int(match_dict['o'])
        except KeyError:
            pass

        return byterange

    @classmethod
    def from_dict(cls, info_dict):
        """ Creates a :class:`Byterange` given a dictionary containing keys
        like generated from the :meth:`to_dict method`.

        :param info_dict: (:class:`dict`) Dictionary byterange.
        :return: (:class:`Byterange`) an equivalent instance.
        """
        byterange = cls(
            count=info_dict.get(BYTE_COUNT_KEY),
            offset=info_dict.get(BYTE_OFFSET_KEY)
        )

        return byterange


"""
For a given collection of media, HLS has two playlist types:
    - Media Playlist
    - Master Playlist

The media playlist refers directly to the individual segments that make up an
audio or video track of a given program. The master playlist refers to a
collection of media playlists and provides ways to use them together
(rendition groups).

See section 2 of draft-pantos-http-live-streaming for more detail.

The constants below define which tags belong to which schema.
"""

"""
Basic tags appear in both media and master playlists.
See section 4.3.1 of draft-pantos-http-live-streaming for more detail.
"""
BASIC_TAGS = {
    "EXTM3U",
    "EXT-X-VERSION"
}

"""
Media segment tags apply to either the following media or all subsequent
segments. They MUST NOT appear in master playlists.
See section 4.3.2 of draft-pantos-http-live-streaming for more detail.
"""
MEDIA_SEGMENT_TAGS = {
    'EXTINF',
    'EXT-X-BYTERANGE',
    'EXT-X-DISCONTINUITY',
    'EXT-X-KEY',
    'EXT-X-MAP',
    'EXT-X-PROGRAM-DATE-TIME',
    'EXT-X-DATERANGE'
}

""" The subset of above tags that apply to every segment following them """
MEDIA_SEGMENT_SUBSEQUENT_TAGS = {
    'EXT-X-KEY',
    'EXT-X-MAP',
}

"""
Media Playlist tags must only occur once per playlist, and must not appear in
Master Playlists.
See section 4.3.3 of draft-pantos-http-live-streaming for more detail.
"""
MEDIA_PLAYLIST_TAGS = {
    'EXT-X-TARGETDURATION',
    'EXT-X-MEDIA-SEQUENCE',
    'EXT-X-DISCONTINUITY-SEQUENCE',
    'EXT-X-ENDLIST',
    'EXT-X-PLAYLIST-TYPE',
    'EXT-X-I-FRAMES-ONLY'
}

"""
Master playlist tags declare global parameters for the presentation.
They must not appear in media playlists.
See section 4.3.4 of draft-pantos-http-live-streaming for more detail.
"""
MASTER_PLAYLIST_TAGS = {
    'EXT-X-MEDIA',
    'EXT-X-STREAM-INF',
    'EXT-X-I-FRAME-STREAM-INF',
    'EXT-X-SESSION-DATA',
    'EXT-X-SESSION-KEY',
}

"""
Media or Master Playlist tags can appear in either media or master playlists.
See section 4.3.5 of draft-pantos-http-live-streaming for more detail.
These tags SHOULD appear in either the media or master playlist. If they occur
in both, their values MUST agree.
These values MUST NOT appear more than once in a playlist.
"""
MEDIA_OR_MASTER_TAGS = {
    "EXT-X-INDEPENDENT-SEGMENTS",
    "EXT-X-START"
}

"""
Some special tags used by the parser.
"""
PLAYLIST_START_TAG = "EXTM3U"
PLAYLIST_END_TAG = "EXT-X-ENDLIST"
PLAYLIST_VERSION_TAG = "EXT-X-VERSION"
PLAYLIST_SEGMENT_INF_TAG = "EXTINF"

"""
attribute list entries to omit from EXT-I-FRAME-STREAM-INF tags
See section 4.3.4.3 of draft-pantos-http-live-streaming for more detail.
"""
I_FRAME_OMIT_ATTRS = {
    'FRAME-RATE',
    'AUDIO',
    'SUBTITLES',
    'CLOSED-CAPTIONS'
}

""" enum for kinds of playlist entries """
EntryType = type('EntryType', (), {
    'tag': 'tag',
    'comment': 'comment',
    'URI': 'URI'
})

""" enum for types of playlists """
PlaylistType = type('PlaylistType', (), {
    'media': 'media',
    'master': 'master'
})

""" mapping from HLS track type to otio ``TrackKind`` """
HLS_TRACK_TYPE_TO_OTIO_KIND = {
    AttributeListEnum('AUDIO'): otio.schema.TrackKind.Audio,
    AttributeListEnum('VIDEO'): otio.schema.TrackKind.Video,
    # TODO: determine how to handle SUBTITLES and CLOSED-CAPTIONS
}

""" mapping from otio ``TrackKind`` to HLS track type """
OTIO_TRACK_KIND_TO_HLS_TYPE = {
    v: k for k, v in HLS_TRACK_TYPE_TO_OTIO_KIND.items()
}


class HLSPlaylistEntry:
    """An entry in an HLS playlist.

    Entries can be a tag, a comment, or a URI. All HLS playlists are parsed
    into lists of :class:`HLSPlaylistEntry` instances that can then be
    interpreted against the HLS schema.
    """

    # TODO: rename this to entry_type to fix builtin masking
    # type = None
    """ (``EntryType``) the type of entry """

    comment_string = None
    """
    (:class:`str`) value of comment (if the ``entry_type`` is
    ``EntryType.comment``).
    """

    tag_name = None
    """
    (:class:`str`) Name of tag (if the ``entry_type`` is ``EntryType.tag``).
    """

    tag_value = None
    """
    (:class:`str`) Value of tag (if the ``entry_type`` is ``EntryType.tag``).
    """

    uri = None
    """
    (:class:`str`) Value of the URI (if the ``entry_type is ``EntryType.uri``).
    """

    def __init__(self, type):
        """
        Constructs an :class:`HLSPlaylistEntry`.

        :param type: (``EntryType``) Type of entry.
        """
        self.type = type

    def __repr__(self):
        base_str = 'otio.adapter.HLSPlaylistEntry(type={}'.format(
            self.type)
        if self.type == EntryType.tag:
            base_str += ', tag_name={}, tag_value={}'.format(
                repr(self.tag_name),
                repr(self.tag_value)
            )
        elif self.type == EntryType.comment:
            base_str += f', comment={repr(self.comment_string)}'
        elif self.type == EntryType.URI:
            base_str += f', URI={repr(self.uri)}'

        return base_str + ')'

    def __str__(self):
        """
        Returns a string as it would appear in an HLS playlist.

        :return: (:class:`str`) HLS playlist entry string.
        """
        if self.type == EntryType.comment and self.comment_string:
            return f"# {self.comment_string}"
        elif self.type == EntryType.comment:
            # empty comments are blank lines
            return ""
        elif self.type == EntryType.URI:
            return self.uri
        elif self.type == EntryType.tag:
            out_tag_name = self.tag_name
            if self.tag_value is not None:
                return f'#{out_tag_name}:{self.tag_value}'
            else:
                return f'#{out_tag_name}'

    @classmethod
    def tag_entry(cls, name, value=None):
        """
        Creates an ``EntryType.tag`` :class:`HLSPlaylistEntry`.

        :param name: (:class:`str`) tag name.
        :param value: (:class:`str`) tag value.
        :return: (:class:`HLSPlaylistEntry`) Entry instance.
        """
        entry = cls(EntryType.tag)
        entry.tag_name = name
        entry.tag_value = value

        return entry

    @classmethod
    def comment_entry(cls, comment):
        """Creates an ``EntryType.comment`` :class:`HLSPlaylistEntry`.

        :param comment: (:class:`str`) the comment.
        :return: (:class:`HLSPlaylistEntry`) Entry instance.
        """
        entry = cls(EntryType.comment)
        entry.comment_string = comment

        return entry

    @classmethod
    def uri_entry(cls, uri):
        """Creates an ``EntryType.uri`` :class:`HLSPlaylistEntry`.

        :param uri: (:class:`str`) A URI string.
        :return: (:class:`HLSPlaylistEntry`) Entry instance.
        """
        entry = cls(EntryType.URI)
        entry.uri = uri

        return entry

    @classmethod
    def from_string(cls, entry_string):
        """Creates an `:class:`HLSPlaylistEntry` given a string as it appears
        in an HLS playlist.

        :param entry_string: (:class:`str`) String from an HLS playlist.
        :return: (:class:`HLSPlaylistEntry`) Entry instance.
        """
        # Empty lines are skipped
        if not entry_string.strip():
            return None

        # Attempt to parse as a tag
        m = TAG_RE.match(entry_string)
        if m:
            group_dict = m.groupdict()
            tag_value = (
                group_dict['tagvalue']
                if group_dict['hasvalue'] else None
            )
            entry = cls.tag_entry(group_dict['tagname'], tag_value)
            return entry

        # Attempt to parse as a comment
        m = COMMENT_RE.match(entry_string)
        if m:
            entry = cls.comment_entry(m.groupdict()['comment'])
            return entry

        # If it's not the others, treat as a URI
        entry = cls.uri_entry(entry_string)

        return entry

    """A dispatch dictionary for grabbing the right Regex to parse tags."""
    TAG_VALUE_RE_MAP = {
        "EXTINF": re.compile(r'(?P<duration>\d+(\.\d*)?),(?P<title>.*$)'),
        "EXT-X-BYTERANGE": BYTERANGE_RE,
        "EXT-X-KEY": re.compile(r'(?P<attribute_list>.*$)'),
        "EXT-X-MAP": re.compile(r'(?P<attribute_list>.*$)'),
        "EXT-X-MEDIA-SEQUENCE": re.compile(r'(?P<number>\d+)'),
        "EXT-X-PLAYLIST-TYPE": re.compile(r'(?P<type>EVENT|VOD)'),
        PLAYLIST_VERSION_TAG: re.compile(r'(?P<n>\d+)')
    }

    def parsed_tag_value(self, playlist_version=None):
        """Parses and returns ``self.tag_value`` based on the HLS schema.

        The value will be a dictionary where the keys are the names used in the
        draft Pantos HTTP Live Streaming doc. When "attribute-list" is
        specified, an entry "attribute_list" will be present containing
        an :class:`AttributeList` instance.

        :param playlist_version: (:class:`int`) version number of the playlist.
            If none is provided, a best guess will be made.
        :return: The parsed value.
        """
        if self.type != EntryType.tag:
            return None

        try:
            tag_re = self.TAG_VALUE_RE_MAP[self.tag_name]
        except KeyError:
            return None

        # parse the tag
        m = tag_re.match(self.tag_value)
        group_dict = m.groupdict()

        if not m:
            return None

        # If the tag value has an attribute list, parse it and add it
        try:
            attribute_list = group_dict['attribute_list']
            attr_list = AttributeList.from_string(attribute_list)
            group_dict['attributes'] = attr_list
        except KeyError:
            pass

        return group_dict


class HLSPlaylistParser:
    """Bootstraps HLS parsing and hands the playlist string off to the
    appropriate parser for the type
    """

    def __init__(self, edl_string):
        self.timeline = otio.schema.Timeline()
        self.playlist_type = None

        self._parse_playlist(edl_string)

    def _parse_playlist(self, edl_string):
        """Parses the HLS Playlist string line-by-line."""
        # parse lines until we encounter one that identifies the playlist type
        # then hand off
        start_encountered = False
        end_encountered = False
        playlist_entries = []
        playlist_version = 1
        for line in edl_string.splitlines():
            # attempt to parse the entry
            entry = HLSPlaylistEntry.from_string(line)
            if entry is None:
                continue

            entry_is_tag = (entry.type == EntryType.tag)

            # identify if the playlist start/end is encountered
            if (entry_is_tag and not (start_encountered and end_encountered)):
                if entry.tag_name == PLAYLIST_START_TAG:
                    start_encountered = True
                elif entry.tag_name == PLAYLIST_END_TAG:
                    end_encountered = True

            # if the playlist starting tag hasn't been encountered, ignore
            if not start_encountered:
                continue

            # Store the parsed entry
            playlist_entries.append(entry)

            # Determine if this tells us the playlist type
            if not self.playlist_type and entry_is_tag:
                if entry.tag_name in MASTER_PLAYLIST_TAGS:
                    self.playlist_type = PlaylistType.master
                elif entry.tag_name in MEDIA_PLAYLIST_TAGS:
                    self.playlist_type = PlaylistType.media

            if end_encountered:
                break

            # try to grab the version from the playlist
            if entry_is_tag and entry.tag_name == PLAYLIST_VERSION_TAG:
                playlist_version = int(entry.parsed_tag_value()['n'])

        # dispatch to the appropriate schema interpreter
        if self.playlist_type is None:
            self.timeline = None
            raise otio.exceptions.ReadingNotSupportedError(
                "could not determine playlist type"
            )
        elif self.playlist_type == PlaylistType.master:
            self.timeline = None
            raise otio.exceptions.AdapterDoesntSupportFunction(
                "HLS master playlists are not yet supported"
            )
        elif self.playlist_type == PlaylistType.media:
            parser = MediaPlaylistParser(playlist_entries, playlist_version)
            if len(parser.track):
                self.timeline.tracks.append(parser.track)


class MediaPlaylistParser:
    """Parses an HLS Media playlist returning a SEQUENCE"""

    def __init__(self, playlist_entries, playlist_version=None):
        self.track = otio.schema.Track(
            metadata={FORMAT_METADATA_KEY: {}}
        )

        self._parse_entries(playlist_entries, playlist_version)

    def _handle_track_metadata(self, entry, playlist_version, clip):
        """Stashes the tag value in the track metadata"""
        value = entry.tag_value
        self.track.metadata[FORMAT_METADATA_KEY][entry.tag_name] = value

    def _handle_discarded_metadata(self, entry, playlist_version, clip):
        """Handler for tags that are discarded. This is done when a tag's
        information is represented by the native OTIO concepts.

        For instance, the EXT-X-TARGETDURATION tag simply gives a rounded
        value for the maximum segment size in the playlist. This can easily
        be found in OTIO by examining the clips.
        """
        # Do nothing

    def _metadata_dict_for_MAP(self, entry, playlist_version):
        entry_data = entry.parsed_tag_value()
        attributes = entry_data['attributes']
        map_dict = {}
        for attr, value in attributes.items():
            if attr == 'BYTERANGE':
                byterange = Byterange.from_string(value)
                map_dict[INIT_BYTERANGE_KEY] = byterange.to_dict()
            elif attr == 'URI':
                map_dict[INIT_URI_KEY] = value

        return map_dict

    def _handle_INF(self, entry, playlist_version, clip):
        # This specifies segment duration and optional title
        info_dict = entry.parsed_tag_value(playlist_version)
        segment_duration = float(info_dict['duration'])
        segment_title = info_dict['title']
        available_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(segment_duration, 1)
        )

        # Push the info to the clip
        clip.media_reference.available_range = available_range
        clip.source_range = available_range
        clip.name = segment_title

    def _handle_BYTERANGE(self, entry, playlist_version, clip):
        reference_metadata = clip.media_reference.metadata
        ref_streaming_metadata = reference_metadata.setdefault(
            STREAMING_METADATA_KEY,
            {}
        )

        # Pull out the byte count and offset
        byterange = Byterange.from_match_dict(
            entry.parsed_tag_value(playlist_version)
        )
        ref_streaming_metadata.update(byterange.to_dict())

    """
    Specifies handlers for specific HLS tags.
    """
    TAG_HANDLERS = {
        "EXTINF": _handle_INF,
        PLAYLIST_VERSION_TAG: _handle_track_metadata,
        "EXT-X-TARGETDURATION": _handle_discarded_metadata,
        "EXT-X-MEDIA-SEQUENCE": _handle_discarded_metadata,
        "EXT-X-PLAYLIST-TYPE": _handle_track_metadata,
        "EXT-X-INDEPENDENT-SEGMENTS": _handle_track_metadata,
        "EXT-X-BYTERANGE": _handle_BYTERANGE
    }

    def _parse_entries(self, playlist_entries, playlist_version):
        """Interpret the entries through the lens of the schema"""
        current_clip = otio.schema.Clip(
            media_reference=otio.schema.ExternalReference(
                metadata={
                    FORMAT_METADATA_KEY: {},
                    STREAMING_METADATA_KEY: {}
                }
            )
        )
        current_media_ref = current_clip.media_reference
        segment_metadata = {}
        current_map_data = {}
        # per section 4.3.3.2 of Pantos HLS, 0 is default start track
        current_track = 0
        for entry in playlist_entries:
            if entry.type == EntryType.URI:
                # the URI ends the segment definition
                current_media_ref.target_url = entry.uri
                current_media_ref.metadata[FORMAT_METADATA_KEY].update(
                    segment_metadata
                )
                current_media_ref.metadata[STREAMING_METADATA_KEY].update(
                    current_map_data
                )
                current_clip.metadata.setdefault(
                    STREAMING_METADATA_KEY,
                    {}
                )[SEQUENCE_NUM_KEY] = current_track
                self.track.append(current_clip)
                current_track += 1

                # Set up the next segment definition
                current_clip = otio.schema.Clip(
                    media_reference=otio.schema.ExternalReference(
                        metadata={
                            FORMAT_METADATA_KEY: {},
                            STREAMING_METADATA_KEY: {}
                        }
                    )
                )
                current_media_ref = current_clip.media_reference
                continue
            elif entry.type != EntryType.tag:
                # the rest of the code deals only with tags
                continue

            # Explode the EXT-X-MAP info out
            if entry.tag_name == "EXT-X-MAP":
                map_data = self._metadata_dict_for_MAP(entry, playlist_version)
                current_map_data.update(map_data)
                continue

            # Grab the track when it comes around
            if entry.tag_name == "EXT-X-MEDIA-SEQUENCE":
                entry_data = entry.parsed_tag_value()
                current_track = int(entry_data['number'])

            # If the segment tag is one that applies to all that follow
            # store the value to be applied to each segment
            if entry.tag_name in MEDIA_SEGMENT_SUBSEQUENT_TAGS:
                segment_metadata[entry.tag_name] = entry.tag_value
                continue

            # use a handler if available
            try:
                handler = self.TAG_HANDLERS[entry.tag_name]
                handler(self, entry, playlist_version, current_clip)
                continue
            except KeyError:
                pass

            # add the tag to the reference metadata at the correct level
            if entry.tag_name in [PLAYLIST_START_TAG, PLAYLIST_END_TAG]:
                continue
            elif entry.tag_name in MEDIA_SEGMENT_TAGS:
                # Media segments translate into media refs
                hls_metadata = current_media_ref.metadata[FORMAT_METADATA_KEY]
                hls_metadata[entry.tag_name] = entry.tag_value
            elif entry.tag_name in MEDIA_PLAYLIST_TAGS:
                # Media playlists translate into tracks
                hls_metadata = self.track.metadata[FORMAT_METADATA_KEY]
                hls_metadata[entry.tag_name] = entry.tag_value


"""
Compatibility version list:
    EXT-X-BYTERANGE >= 4
    EXT-X-I-FRAMES-ONLY >= 4
    EXT-X-MAP in media playlist with EXT-X-I-FRAMES-ONLY >= 5
    EXT-X-MAP in media playlist without I-FRAMES-ONLY >= 6
    EXT-X-KEY constrants are by attributes specified:
        - IV >= 2
        - KEYFORMAT >= 5
        - KEYFORMATVERSIONS >= 5
    EXTINF with floating point vaules >= 3

    master playlist:
    EXT-X-MEDIA with INSTREAM-ID="SERVICE"
"""


def entries_for_segment(
    uri,
    segment_duration,
    segment_name=None,
    segment_byterange=None,
    segment_tags=None
):
    """Creates a set of :class:`HLSPlaylistEntries` with the given parameters.

    :param uri: (:class:`str`) The uri for the segment media.
    :param segment_duration: (:class:`opentimelineio.opentime.RationalTime`)
        playback duration of the segment.
    :param segment_byterange: (:class:`ByteRange`) The data range for the
        segment in the media (if required)
    :param segment_tags: (:class:`dict`) key/value pairs of to become
        additional tags for the segment

    :return: (:class:`list`) a group of :class:`HLSPlaylistEntry` instances for
        the segment
    """
    # Create the tags dict to build
    if segment_tags:
        tags = copy.deepcopy(segment_tags)
    else:
        tags = {}

    # Start building the entries list
    segment_entries = []

    # add the EXTINF
    name = segment_name if segment_name is not None else ''
    tag_value = '{:.5f},{}'.format(
        otio.opentime.to_seconds(segment_duration),
        name
    )
    extinf_entry = HLSPlaylistEntry.tag_entry('EXTINF', tag_value)
    segment_entries.append(extinf_entry)

    # add the additional tags
    tag_entries = [
        HLSPlaylistEntry.tag_entry(k, v) for k, v in
        tags.items()
    ]
    segment_entries.extend(tag_entries)

    # Now add the byterange for the entry
    if segment_byterange:
        byterange_entry = HLSPlaylistEntry.tag_entry(
            'EXT-X-BYTERANGE',
            str(segment_byterange)
        )
        segment_entries.append(byterange_entry)

    # Add the URI
    # this method expects all fragments come from the same source file
    uri_entry = HLSPlaylistEntry.uri_entry(uri)
    segment_entries.append(uri_entry)

    return segment_entries


def stream_inf_attr_list_for_track(track):
    """ Builds an :class:`AttributeList` instance for use in ``STREAM-INF``
    tags for the provided track.

    :param track: (:class:`otio.schema.Track`) A track representing a
        variant stream
    :return: (:class:`AttributeList`) The instance from the metadata
    """
    streaming_metadata = track.metadata.get(STREAMING_METADATA_KEY, {})

    attributes = []
    bandwidth = streaming_metadata.get('bandwidth')
    if bandwidth is not None:
        attributes.append(('BANDWIDTH', bandwidth))

    codec = streaming_metadata.get('codec')
    if codec is not None:
        attributes.append(('CODECS', codec))

    frame_rate = streaming_metadata.get('frame_rate')
    if frame_rate is not None:
        attributes.append(('FRAME-RATE', frame_rate))

    if 'width' in streaming_metadata and 'height' in streaming_metadata:
        resolution = "{}x{}".format(
            streaming_metadata['width'],
            streaming_metadata['height']
        )
        attributes.append(('RESOLUTION', AttributeListEnum(resolution)))

    al = AttributeList(attributes)

    return al


def master_playlist_to_string(master_timeline):
    """Writes a master playlist describing the tracks"""

    # start with a version number of 1, as features are encountered, we will
    # update the version accordingly
    version_requirements = {1}

    # TODO: detect rather than forcing version 6
    version_requirements.add(6)

    header_tags = copy.copy(
        master_timeline.metadata.get(FORMAT_METADATA_KEY, {})
    )

    # Filter out any values from the HLS metadata that aren't meant to become
    # tags, such as the directive to force an HLS master playlist
    hls_md_rejectlist = ['master_playlist']
    for key in hls_md_rejectlist:
        try:
            del header_tags[key]
        except KeyError:
            pass

    playlist_entries = []

    # First declare the non-visual media
    hls_type_count = {}
    video_tracks = []
    audio_tracks = [
        t for t in master_timeline.tracks if
        t.kind == otio.schema.TrackKind.Audio
    ]
    for track in master_timeline.tracks:
        if track.kind == otio.schema.TrackKind.Video:
            # video is done later, skip
            video_tracks.append(track)
            continue

        # Determine the HLS type
        hls_type = OTIO_TRACK_KIND_TO_HLS_TYPE[track.kind]

        streaming_metadata = track.metadata.get(STREAMING_METADATA_KEY, {})

        # Find the group name
        try:
            group_id = streaming_metadata['group_id']
        except KeyError:
            sub_id = hls_type_count.setdefault(hls_type, 1)
            group_id = f'{hls_type}{sub_id}'
            hls_type_count[hls_type] += 1

        media_playlist_default_uri = f"{track.name}.m3u8"
        try:
            track_uri = track.metadata[FORMAT_METADATA_KEY].get(
                'uri',
                media_playlist_default_uri
            )
        except KeyError:
            track_uri = media_playlist_default_uri

        # Build the attribute list
        attributes = AttributeList(
            [
                ('TYPE', hls_type),
                ('GROUP-ID', group_id),
                ('URI', track_uri),
                ('NAME', track.name),
            ]
        )

        if streaming_metadata.get('autoselect'):
            attributes['AUTOSELECT'] = AttributeListEnum('YES')

        if streaming_metadata.get('default'):
            attributes['DEFAULT'] = AttributeListEnum('YES')

        # Finally, create the tag
        entry = HLSPlaylistEntry.tag_entry(
            'EXT-X-MEDIA',
            str(attributes)
        )

        playlist_entries.append(entry)

    # Add a blank line in the playlist to separate sections
    if playlist_entries:
        playlist_entries.append(HLSPlaylistEntry.comment_entry(''))

    # First write any i-frame playlist entires
    iframe_list_entries = []
    for track in video_tracks:
        try:
            iframe_uri = track.metadata[FORMAT_METADATA_KEY]['iframe_uri']
        except KeyError:
            # don't include iframe playlist
            continue

        # Create the attribute list
        attribute_list = stream_inf_attr_list_for_track(track)

        # Remove entries to not be included for I-Frame streams
        for attr in I_FRAME_OMIT_ATTRS:
            try:
                del attribute_list[attr]
            except KeyError:
                pass

        # Add the URI
        attribute_list['URI'] = iframe_uri

        iframe_list_entries.append(
            HLSPlaylistEntry.tag_entry(
                'EXT-X-I-FRAME-STREAM-INF',
                str(attribute_list)
            )
        )

    if iframe_list_entries:
        iframe_list_entries.append(HLSPlaylistEntry.comment_entry(''))

    playlist_entries.extend(iframe_list_entries)

    # Write an EXT-STREAM-INF for each rendition set
    for track in video_tracks:
        # create the base attribute list for the video track
        al = stream_inf_attr_list_for_track(track)

        # Create the uri
        media_playlist_default_uri = f"{track.name}.m3u8"
        try:
            track_uri = track.metadata[FORMAT_METADATA_KEY].get(
                'uri', media_playlist_default_uri
            )
        except KeyError:
            track_uri = media_playlist_default_uri
        uri_entry = HLSPlaylistEntry.uri_entry(track_uri)

        # TODO: this will break when we have subtitle and CC tracks
        added_entry = False
        for audio_track in audio_tracks:
            if track.name not in audio_track.metadata['linked_tracks']:
                continue

            # Write an entry for using these together
            try:
                audio_track_streaming_metadata = audio_track.metadata[
                    STREAMING_METADATA_KEY
                ]
                aud_group = audio_track_streaming_metadata['group_id']
                aud_codec = audio_track_streaming_metadata['codec']
                aud_bandwidth = audio_track_streaming_metadata['bandwidth']
            except KeyError:
                raise TypeError(
                    "HLS audio tracks must have 'codec', 'group_id', and"
                    " 'bandwidth' specified in metadata"
                )

            combo_al = copy.copy(al)
            combo_al['CODECS'] += f',{aud_codec}'
            combo_al['AUDIO'] = aud_group
            combo_al['BANDWIDTH'] += aud_bandwidth

            entry = HLSPlaylistEntry.tag_entry(
                'EXT-X-STREAM-INF',
                str(combo_al)
            )
            playlist_entries.append(entry)
            playlist_entries.append(uri_entry)

            added_entry = True

        if not added_entry:
            # write out one simple entry
            entry = HLSPlaylistEntry.tag_entry(
                'EXT-X-STREAM-INF',
                str(al)
            )
            playlist_entries.append(entry)
            playlist_entries.append(uri_entry)

        # add a break before the next grouping of entries
        playlist_entries.append(HLSPlaylistEntry.comment_entry(''))

    out_entries = [HLSPlaylistEntry.tag_entry(PLAYLIST_START_TAG, None)]

    playlist_version = max(version_requirements)
    playlist_version_entry = HLSPlaylistEntry.tag_entry(
        PLAYLIST_VERSION_TAG,
        str(playlist_version)
    )

    out_entries.append(playlist_version_entry)

    out_entries += (
        HLSPlaylistEntry.tag_entry(k, v) for k, v in header_tags.items()
    )

    # separate the header entries from the rest of the entries
    out_entries.append(HLSPlaylistEntry.comment_entry(''))

    out_entries += playlist_entries

    playlist_string = '\n'.join(
        str(entry) for entry in out_entries
    )

    return playlist_string


class MediaPlaylistWriter():

    def __init__(
            self,
            media_track,
            min_seg_duration=None,
            max_seg_duration=None
    ):
        # Default to one segment per fragment
        if min_seg_duration is None:
            min_seg_duration = otio.opentime.RationalTime(0, 1)
        if max_seg_duration is None:
            max_seg_duration = otio.opentime.RationalTime(0, 1)

        self._min_seg_duration = min_seg_duration
        self._max_seg_duration = max_seg_duration

        self._playlist_entries = []
        self._playlist_tags = {}

        # Whenever an entry is added that has a minimum version requirement,
        # we add that version to this set. The max value from this set is the
        # playlist's version requirement
        self._versions_used = {1}

        # TODO: detect rather than forcing version 7
        self._versions_used.add(7)

        # Start the build
        self._build_playlist_with_track(media_track)

    def _build_playlist_with_track(self, media_track):
        """
        Executes methods to result in a fully populated _playlist_entries list
        """
        self._copy_HLS_metadata(media_track)
        self._setup_track_info(media_track)
        self._add_segment_entries(media_track)
        self._finalize_entries(media_track)

    def _copy_HLS_metadata(self, media_track):
        """
        Copies any metadata in the "HLS" namespace from the track to the
        playlist-global tags
        """
        # Grab any metadata provided on the otio
        try:
            track_metadata = media_track.metadata[FORMAT_METADATA_KEY]
            self._playlist_tags.update(track_metadata)

            # Remove the version tag from the track metadata, we'll compute
            # based on what we write out
            del self._playlist_tags[PLAYLIST_VERSION_TAG]

        except KeyError:
            pass

        # additionally remove metadata keys added for providing master
        # playlist URIs
        for key in ('uri', 'iframe_uri'):
            try:
                del self._playlist_tags[key]
            except KeyError:
                pass

    def _setup_track_info(self, media_track):
        """sets up playlist global metadata"""

        # Setup the track start
        if 'EXT-X-I-FRAMES-ONLY' in media_track.metadata.get(
            FORMAT_METADATA_KEY,
            {}
        ):
            # I-Frame playlists start at zero no matter what
            track_start = 0
        else:
            # Pull the track num from the first clip, if provided
            first_segment_streaming_metadata = media_track[0].metadata.get(
                STREAMING_METADATA_KEY,
                {}
            )
            track_start = first_segment_streaming_metadata.get(
                SEQUENCE_NUM_KEY
            )

        # If we found a track start or one isn't already set in the
        # metadata, create the tag for it.
        if (
            track_start is not None or
            'EXT-X-MEDIA-SEQUENCE' not in self._playlist_tags
        ):
            # Choose a reasonable track start default
            if track_start is None:
                track_start = 1
            self._playlist_tags['EXT-X-MEDIA-SEQUENCE'] = str(track_start)

    def _add_map_entry(self, fragment):
        """adds an EXT-X-MAP entry from the given fragment

        returns the added entry
        """

        media_ref = fragment.media_reference

        # Extract useful tag data
        media_ref_streaming_metadata = media_ref.metadata[
            STREAMING_METADATA_KEY
        ]
        uri = media_ref_streaming_metadata[INIT_URI_KEY]
        seg_map_byterange_dict = media_ref_streaming_metadata.get(
            INIT_BYTERANGE_KEY
        )

        # Create the attrlist
        map_attr_list = AttributeList([
            ('URI', uri),
        ])

        # Add the byterange if provided
        if seg_map_byterange_dict is not None:
            seg_map_byterange = Byterange.from_dict(seg_map_byterange_dict)
            map_attr_list['BYTERANGE'] = str(seg_map_byterange)

        # Construct the entry with the attrlist as the value
        map_tag_str = str(map_attr_list)
        entry = HLSPlaylistEntry.tag_entry("EXT-X-MAP", map_tag_str)

        self._playlist_entries.append(entry)

        return entry

    def _add_entries_for_segment_from_fragments(
            self,
            fragments,
            omit_hls_keys=None,
            is_iframe_playlist=False
    ):
        """
        For the given list of otio clips representing fragments in the mp4,
        add playlist entries for single HLS segment.

        :param fragments: (:clas:`list`) :class:`opentimelineio.schema.Clip`
            objects to write as a contiguous segment.
        :param omit_hls_keys: (:class:`list`) metadata keys from the original
            "HLS" metadata namespeaces will not be passed through.
        :param is_iframe_playlist: (:class:`bool`) If true, writes one segment
            per fragment, otherwise writes all fragments as a single segment

        :return: (:class:`list` the :class:`HLSPlaylistEntry` instances added
            to the playlist
        """
        if is_iframe_playlist:
            entries = []
            for fragment in fragments:
                name = ''
                fragment_range = Byterange.from_dict(
                    fragment.media_reference.metadata[STREAMING_METADATA_KEY]
                )

                segment_tags = {}
                frag_tags = fragment.media_reference.metadata.get(
                    FORMAT_METADATA_KEY,
                    {}
                )
                segment_tags.update(copy.deepcopy(frag_tags))

                # scrub any metadata marked for omission
                omit_hls_keys = omit_hls_keys or []
                for key in omit_hls_keys:
                    try:
                        del segment_tags[key]
                    except KeyError:
                        pass

                segment_entries = entries_for_segment(
                    fragment.media_reference.target_url,
                    fragment.duration(),
                    name,
                    fragment_range,
                    segment_tags
                )
                entries.extend(segment_entries)

            self._playlist_entries.extend(entries)
            return entries

        segment_tags = {}
        for fragment in fragments:
            frag_tags = fragment.media_reference.metadata.get(
                FORMAT_METADATA_KEY,
                {}
            )
            segment_tags.update(copy.deepcopy(frag_tags))

        # scrub any metadata marked for omission
        omit_hls_keys = omit_hls_keys or []
        for key in omit_hls_keys:
            try:
                del segment_tags[key]
            except KeyError:
                pass

        # Calculate the byterange for the segment (if byteranges are specified)
        first_ref = fragments[0].media_reference
        first_ref_streaming_md = first_ref.metadata[STREAMING_METADATA_KEY]
        if 'byte_offset' in first_ref_streaming_md and len(fragments) == 1:
            segment_range = Byterange.from_dict(first_ref_streaming_md)
        elif 'byte_offset' in first_ref_streaming_md:
            # Find the byterange encapsulating everything
            last_ref = fragments[-1].media_reference
            last_ref_streaming_md = last_ref.metadata[STREAMING_METADATA_KEY]
            first_range = Byterange.from_dict(first_ref_streaming_md)
            last_range = Byterange.from_dict(last_ref_streaming_md)

            segment_offset = first_range.offset
            segment_end = (last_range.offset + last_range.count)
            segment_count = segment_end - segment_offset
            segment_range = Byterange(segment_count, segment_offset)
        else:
            segment_range = None

        uri = fragments[0].media_reference.target_url

        # calculate the combined duration
        segment_duration = fragments[0].duration()
        for frag in fragments[1:]:
            segment_duration += frag.duration()

        # TODO: Determine how to pass a segment name in
        segment_name = ''
        segment_entries = entries_for_segment(
            uri,
            segment_duration,
            segment_name,
            segment_range,
            segment_tags
        )

        self._playlist_entries.extend(segment_entries)
        return segment_entries

    def _fragments_have_same_map(self, fragment, following_fragment):
        """
        Given fragment and following_fragment, returns whether or not their
        initialization data is the same (what becomes EXT-X-MAP)
        """
        media_ref = fragment.media_reference
        media_ref_streaming_md = media_ref.metadata.get(
            STREAMING_METADATA_KEY,
            {}
        )
        following_ref = following_fragment.media_reference
        following_ref_streaming_md = following_ref.metadata.get(
            STREAMING_METADATA_KEY,
            {}
        )
        # Check the init file
        init_uri = media_ref_streaming_md.get(INIT_URI_KEY)
        following_init_uri = media_ref_streaming_md.get(INIT_URI_KEY)
        if init_uri != following_init_uri:
            return False

        # Check the init byterange
        init_dict = media_ref_streaming_md.get(INIT_BYTERANGE_KEY)
        following_init_dict = following_ref_streaming_md.get(
            INIT_BYTERANGE_KEY
        )

        dummy_range = Byterange(0, 0)
        init_range = (
            Byterange.from_dict(init_dict) if init_dict else dummy_range
        )
        following_range = (
            Byterange.from_dict(following_init_dict)
            if following_init_dict else dummy_range
        )

        if init_range != following_range:
            return False

        return True

    def _fragments_are_contiguous(self, fragment, following_fragment):
        """ Given fragment and following_fragment (otio clips) returns whether
        or not they are contiguous.

        To be contiguous the fragments must:
        1. have the same file URL
        2. have the same initialization data (what becomes EXT-X-MAP)
        3. be adjacent in the file (follwoing_fragment's first byte directly
           follows fragment's last byte)

        Returns True if following_fragment is contiguous from fragment
        """
        # Fragments are contiguous if:
        # 1. They have the file url
        # 2. They have the same map info
        # 3. Their byte ranges are contiguous
        media_ref = fragment.media_reference
        media_ref_streaming_md = media_ref.metadata.get(
            STREAMING_METADATA_KEY,
            {}
        )
        following_ref = following_fragment.media_reference
        following_ref_streaming_md = following_ref.metadata.get(
            STREAMING_METADATA_KEY,
            {}
        )
        if media_ref.target_url != following_ref.target_url:
            return False

        if (
            media_ref_streaming_md.get(INIT_URI_KEY) !=
            following_ref_streaming_md.get(INIT_URI_KEY)
        ):
            return False

        if not self._fragments_have_same_map(fragment, following_fragment):
            return False

        # Check if fragments are contiguous in file
        try:
            frag_end = (
                media_ref_streaming_md['byte_offset'] +
                media_ref_streaming_md['byte_count']
            )
            if frag_end != following_ref_streaming_md['byte_offset']:
                return False
        except KeyError:
            return False

        # since we haven't returned yet, all checks must have passed!
        return True

    def _add_segment_entries(self, media_track):
        """given a media track, generates the segment entries"""

        # Determine whether or not this is an I-Frame playlist
        track_hls_metadata = media_track.metadata.get('HLS')
        is_iframe_playlist = 'EXT-X-I-FRAMES-ONLY' in track_hls_metadata

        # Make a list copy of the fragments
        fragments = [clip for clip in media_track]

        segment_durations = []
        previous_fragment = None
        map_changed = True
        while fragments:
            # There should be at least one fragment per segment
            frag_it = iter(fragments)
            first_frag = next(frag_it)
            gathered_fragments = [first_frag]
            gathered_duration = first_frag.duration()

            # Determine this segment will need a new EXT-X-MAP entry
            map_changed = (
                True if previous_fragment is None else
                not self._fragments_have_same_map(
                    previous_fragment,
                    first_frag
                )
            )

            # Iterate through the remaining fragments until a discontinuity
            # is found, our time limit is met, or we add all the fragments to
            # the segment
            for fragment in frag_it:
                # Determine whther or not the fragments are contiguous
                previous_fragment = gathered_fragments[-1]
                contiguous = self._fragments_are_contiguous(
                    previous_fragment,
                    fragment
                )

                # Determine if we've hit our segment time conditions
                new_duration = gathered_duration + fragment.duration()
                segment_full = (
                    gathered_duration >= self._min_seg_duration or
                    new_duration > self._max_seg_duration
                )

                # End condition met, cut the segment
                if not contiguous or segment_full:
                    break

                # Include the fragment
                gathered_duration = new_duration
                gathered_fragments.append(fragment)

            # Write out the segment and start the next
            start_fragment = gathered_fragments[0]

            # If the map for this segment was a change, write it
            if map_changed:
                self._add_map_entry(start_fragment)

            # add the entries for the segment. Omit any EXT-X-MAP metadata
            # that may have come in from reading a file (we're updating)
            self._add_entries_for_segment_from_fragments(
                gathered_fragments,
                omit_hls_keys=('EXT-X-MAP'),
                is_iframe_playlist=is_iframe_playlist
            )

            duration_seconds = otio.opentime.to_seconds(gathered_duration)
            segment_durations.append(duration_seconds)

            # in the next iteration, start where we left off
            fragments = fragments[len(gathered_fragments):]

        # Set the max segment duration
        max_duration = round(max(segment_durations))
        self._playlist_tags['EXT-X-TARGETDURATION'] = str(int(max_duration))

    def _finalize_entries(self, media_track):
        """Does final wrap-up of playlist entries"""

        self._playlist_tags['EXT-X-PLAYLIST-TYPE'] = 'VOD'

        # add the end
        end_entry = HLSPlaylistEntry.tag_entry(PLAYLIST_END_TAG)
        self._playlist_entries.append(end_entry)

        # find the maximum HLS feature version we've used
        playlist_version = max(self._versions_used)
        playlist_version_entry = HLSPlaylistEntry.tag_entry(
            PLAYLIST_VERSION_TAG,
            str(playlist_version)
        )

        # now that we know what was used, let's prepend the header
        playlist_header_entries = [
            HLSPlaylistEntry.tag_entry(PLAYLIST_START_TAG),
            playlist_version_entry
        ]

        # add in the rest of the header entries in a deterministic order
        playlist_header_entries += (
            HLSPlaylistEntry.tag_entry(k, v)
            for k, v in sorted(self._playlist_tags.items(), key=lambda i: i[0])
        )

        # Prepend the entries with the header entries
        self._playlist_entries = (
            playlist_header_entries + self._playlist_entries
        )

    def playlist_string(self):
        """Returns the string representation of the playlist entries"""

        return '\n'.join(
            str(entry) for entry in self._playlist_entries
        )

# Public interface


def read_from_string(input_str):
    """Adapter entry point for reading."""

    parser = HLSPlaylistParser(input_str)
    return parser.timeline


def write_to_string(input_otio):
    """Adapter entry point for writing."""

    if len(input_otio.tracks) == 0:
        return None

    # Determine whether we should write a media or master playlist
    try:
        write_master = input_otio.metadata['HLS']['master_playlist']
    except KeyError:
        # If no explicit directive, infer
        write_master = (len(input_otio.tracks) > 1)

    if write_master:
        return master_playlist_to_string(input_otio)
    else:
        media_track = input_otio.tracks[0]
        track_streaming_md = input_otio.metadata.get(
            STREAMING_METADATA_KEY,
            {}
        )
        min_seg_duration = track_streaming_md.get('min_segment_duration')
        max_seg_duration = track_streaming_md.get('max_segment_duration')

        writer = MediaPlaylistWriter(
            media_track,
            min_seg_duration,
            max_seg_duration
        )
        return writer.playlist_string()
