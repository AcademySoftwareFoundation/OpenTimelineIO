import re
import math
import copy
import itertools

import opentimelineio as otio

# TODO: determine output version based on features used
OUTPUT_PLAYLIST_VERSION = "7"

# TODO: make sure all strings get sanitized through encoding and decoding
PLAYLIST_STRING_ENCODING = "utf-8"


'''
This lists the regexes to match AttributeValue sections of attribute lists
see section 4.2 of draft-pantos-http-live-streaming for more detail.
Note that these are meant to be joined using regex or in this order.
'''
_ATTRIBUTE_RE_VALUE_STR_LIST = [
    r'(?P<resolution>(?P<width>[0-9]+)x(?P<height>[0-9]+))\Z',
    r'(?P<hexcidecimal>0[xX](?P<hex_value>[0-9A-F]+))\Z',
    r'(?P<floating_point>-?[0-9]+\.[0-9]+)\Z',
    r'(?P<decimal>[0-9]+)\Z',
    r'(?P<string>\"(?P<string_value>[^\r\n"]*)\")\Z',
    r'(?P<enumerated>[^",\s]+)\Z'
]

# this composes an RE for matching attribute key/value pairs
_ATTRIBUTE_RE_VALUE_STR = "|".join(_ATTRIBUTE_RE_VALUE_STR_LIST)
ATTRIBUTE_VALUE_RE = re.compile(_ATTRIBUTE_RE_VALUE_STR)
ATTRIBUTE_RE = re.compile(r'(?P<AttributeName>[A-Z0-9-]+)' + r'\=' +
                          r'(?P<AttributeValue>(?:\"[^\r\n"]*\")|[^,]+)' + r',?')

BYTERANGE_RE = re.compile(r'(?P<n>\d+)(?:@(?P<o>\d+))?')

TAG_RE = re.compile(r'#(?P<tagname>EXT[^:\s]+):?(?P<tagvalue>.*)')
COMMENT_RE = re.compile(r'#(?!EXT)(?P<comment>.*)')


class AttributeListEnum(unicode):
    ''' a subclass allowing us to differentiate enums in HLS attribute lists '''

    def to_HLS_string(self):
        return self.encode(PLAYLIST_STRING_ENCODING)


def _value_from_raw_attribute_value(raw_attribute_value):
    '''
    Takes in a raw AttributeValue and returns a parsed and conformed version.
    If there is a problem decoding the value, None is returned.
    '''
    value_match = ATTRIBUTE_VALUE_RE.match(raw_attribute_value)
    if not value_match:
        return None

    group_dict = value_match.groupdict()
    # suss out the match
    for k, v in group_dict.iteritems():
        # not a successful group match
        if v is None:
            continue

        # decode the string
        if k == 'resolution':
            return v
        elif k == 'enumerated':
            return AttributeListEnum(v.decode(PLAYLIST_STRING_ENCODING))
        elif k == 'hexcidecimal':
            return int(group_dict['hex_value'], base=16)
        elif k == 'floating_point':
            return float(v)
        elif k == 'decimal':
            return int(v)
        elif k == 'string':
            # grab only the data within the quotes, excluding the quotes
            string_value = group_dict['string_value']
            return string_value.decode(PLAYLIST_STRING_ENCODING)

    return None


class AttributeList(dict):
    '''
    Dictionary-like object representing an HLS AttributeList.
    '''

    def __init__(self, other=None):
        '''
        contstructs an AttributeList

        other can be either another dictionary-like object or a list of
        key/value pairs
        '''
        if not other:
            return

        try:
            items = other.items()
        except AttributeError:
            items = other

        for k, v in items:
            self[k] = v

    def __str__(self):
        attr_list_entries = []
        for k, v in self.iteritems():
            out_value = ''
            if isinstance(v, AttributeListEnum):
                out_value = v.to_HLS_string()
            elif isinstance(v, str) or isinstance(v, unicode):
                out_value = '"{}"'.format(
                    v.encode(PLAYLIST_STRING_ENCODING)
                )
            else:
                out_value = str(v).encode(PLAYLIST_STRING_ENCODING)

            attr_list_entries.append('{}={}'.format(
                k.encode(PLAYLIST_STRING_ENCODING),
                out_value
            ))

        return ','.join(attr_list_entries)

    @classmethod
    def from_string(cls, attrlist_string):
        '''
        Accepts an attribute list string and returns an AttributeList.

        The values will be transformed to python types.
        '''
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

# some special keys that HLS metadata will be decoded into
INIT_BYTERANGE_KEY = 'init_byterange'
INIT_URI_KEY = 'init_uri'
SEQUENCE_NUM_KEY = 'sequence_num'
BYTE_OFFSET_KEY = 'byte_offset'
BYTE_COUNT_KEY = 'byte_count'


class Byterange(object):
    '''
    Offers interpretation of HLS byte ranges in various forms
    '''

    def __init__(self, count=None, offset=None):
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
        ''' returns a string in HLS format '''
        out_str = str(self.count)
        if self.offset is not None:
            out_str += '@{}'.format(str(self.offset))

        return out_str

    def to_dict(self):
        ''' returns a dict suitable for storing in otio metadata '''
        range_dict = {BYTE_COUNT_KEY: self.count}
        if self.offset is not None:
            range_dict[BYTE_OFFSET_KEY] = self.offset

        return range_dict

    @classmethod
    def from_string(cls, byterange_string):
        ''' returns a Byterange given a string in HLS format '''
        m = BYTERANGE_RE.match(byterange_string)

        return cls.from_match_dict(m.groupdict())

    @classmethod
    def from_match_dict(cls, match_dict):
        ''' returns a Byterange given a groupdict from BYTERANGE_RE '''
        byterange = cls(count=int(match_dict['n']))

        try:
            byterange.offset = int(match_dict['o'])
        except KeyError:
            pass

        return byterange

    @classmethod
    def from_dict(cls, info_dict):
        '''
        returns a string given a dictionary containing keys like generated
        from the to_dict method
        '''
        byterange = cls(
            count=info_dict.get(BYTE_COUNT_KEY),
            offset=info_dict.get(BYTE_OFFSET_KEY)
        )

        return byterange

'''
Media segment tags apply to either the following media or all subsequent
segments. They MUST NOT appear in master playlists
'''
MEDIA_SEGMENT_TAGS = set([
    'EXTINF',
    'EXT-X-BYTERANGE',
    'EXT-X-DISCONTINUITY',
    'EXT-X-KEY',
    'EXT-X-MAP',
    'EXT-X-PROGRAM-DATE-TIME',
    'EXT-X-DATERANGE'
])

''' The subset of above tags that apply to every segment following them '''
MEDIA_SEGMENT_SUBSEQUENT_TAGS = set([
    'EXT-X-KEY',
    'EXT-X-MAP',
])

'''
Media Playlist tags must only occur once per playlist, and must not appear in
Master Playlists
'''
MEDIA_PLAYLIST_TAGS = set([
    'EXT-X-TARGETDURATION',
    'EXT-X-MEDIA-SEQUENCE',
    'EXT-X-DISCONTINUITY-SEQUENCE',
    'EXT-X-ENDLIST',
    'EXT-X-PLAYLIST-TYPE',
    'EXT-X-I-FRAMES-ONLY'
])

'''
Master playlist tags declare global parameters for the presentation.
They must not appear in media playlists.
'''
MASTER_PLAYLIST_TAGS = set([
    'EXT-X-MEDIA',
    'EXT-X-STREAM-INF',
    'EXT-X-I-FRAME-STREAM-INF',
    'EXT-X-SESSION-DATA',
    'EXT-X-SESSION-KEY',
])

''' appear in both media and master playlists '''
BASIC_TAGS = set([
    "EXTM3U",
    "EXT-X-VERSION"
])

"""
Tags that can appear in either media or master playlists. See section 4.3.5.
These tags SHOULD appear in either the media or master playlist. If they occur
in both, their values MUST agree.
These values MUST NOT appear more than once in a playlist.
"""
MEDIA_OR_MASTER_TAGS = set([
    "EXT-X-INDEPENDENT-SEGMENTS",
    "EXT-X-START"
])

PLAYLIST_START_TAG = "EXTM3U"
PLAYLIST_END_TAG = "EXT-X-ENDLIST"
PLAYLIST_VERSION_TAG = "EXT-X-VERSION"
PLAYLIST_SEGMENT_INF_TAG = "EXTINF"

'''
For a given collection of media, HLS has two playlist types:
    - Media Playlist
    - Master Playlist

The media playlist refers directly to the individual segments that make up an
audio or video track of a given program. The master playlist refers to a
collection of media playlists and provides ways to use them together
(rendition groups).

See https://tools.ietf.org/html/draft-pantos-http-live-streaming-20 for more
detail.
'''

EntryType = type('EntryType', (), {
    'tag': 'tag',
    'comment': 'comment',
    'URI': 'URI'
})

PlaylistType = type('PlaylistType', (), {
    'media': 'media',
    'master': 'master'
})

# mappings to get HLS track types in and out of otio
HLS_TRACK_TYPE_TO_OTIO_KIND = {
        AttributeListEnum('AUDIO'): otio.schema.SequenceKind.Audio,
        AttributeListEnum('VIDEO'): otio.schema.SequenceKind.Video,
        AttributeListEnum('SUBTITLES'): otio.schema.SequenceKind.Subtitles,
        AttributeListEnum('CLOSED-CAPTIONS'): otio.schema.SequenceKind.Captions
}

OTIO_TRACK_KIND_TO_HLS_TYPE = dict((
    (v,k) for k,v in HLS_TRACK_TYPE_TO_OTIO_KIND.iteritems()
))

class HLSPlaylistEntry(object):
    '''
    A parsed entry in an HLS playlist
    '''

    def __init__(self, type):
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
            base_str += ', comment={}'.format(repr(self.comment_string))
        elif self.type == EntryType.URI:
            base_str += ', URI={}'.format(repr(self.uri))

        return base_str + ')'

    def __str__(self):
        '''
        Returns an HLS string for the entry
        '''
        if self.type == EntryType.comment:
            return "# {}".format(
                self.comment_string.encode(PLAYLIST_STRING_ENCODING)
            )
        elif self.type == EntryType.URI:
            return self.uri.encode(PLAYLIST_STRING_ENCODING)
        elif self.type == EntryType.tag:
            out_tag_name = self.tag_name.encode(PLAYLIST_STRING_ENCODING)
            if self.tag_value is not None:
                return '#{}:{}'.format(
                    out_tag_name,
                    self.tag_value.encode(PLAYLIST_STRING_ENCODING)
                )
            else:
                return '#{}'.format(out_tag_name)

    @classmethod
    def tag_entry(cls, name, value=None):
        entry = cls(EntryType.tag)
        entry.tag_name = name
        entry.tag_value = value

        return entry

    @classmethod
    def comment_entry(cls, comment):
        entry = cls(EntryType.comment)
        entry.comment_string = comment

        return entry

    @classmethod
    def uri_entry(cls, uri):
        entry = cls(EntryType.URI)
        entry.uri = uri

        return entry

    @classmethod
    def from_string(cls, entry_string):
        # Empty lines are skipped
        if not entry_string.strip():
            return None

        # Attempt to parse as a tag
        m = TAG_RE.match(entry_string)
        if m:
            group_dict = m.groupdict()
            entry = cls.tag_entry(
                group_dict['tagname'],
                group_dict['tagvalue']
            )
            return entry

        # Attempt to parse as a comment
        m = COMMENT_RE.match(entry_string)
        if m:
            entry = cls.comment_entry(m.groupdict()['comment'])
            return entry

        # If it's not the others, treat as a URI
        entry = cls.uri_entry(entry_string)

        return entry

    '''
    A dispatch dictionary for grabbing Regex to parse tags
    '''
    RE_DICT = {
        "EXTINF": re.compile(r'(?P<duration>\d+(\.\d*)?),(?P<title>.*$)'),
        "EXT-X-BYTERANGE": BYTERANGE_RE,
        "EXT-X-KEY": re.compile(r'(?P<attribute_list>.*$)'),
        "EXT-X-MAP": re.compile(r'(?P<attribute_list>.*$)'),
        "EXT-X-MEDIA-SEQUENCE": re.compile(r'(?P<number>\d+)'),
        "EXT-X-PLAYLIST-TYPE": re.compile(r'(?P<type>EVENT|VOD)'),
        PLAYLIST_VERSION_TAG: re.compile(r'(?P<n>\d+)')
    }

    def parsed_tag_value(self, playlist_version=None):
        '''
        Returns a parsed value, based on the hls schema

        The value will be a dictionary where the keys are the names used in the
        draft Pantos HTTP Live Streaming doc.
        '''
        if self.type != EntryType.tag:
            return None

        try:
            tag_re = self.RE_DICT[self.tag_name]
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


class HLSPlaylistParser(object):
    '''
    Bootstraps HLS parsing and hands the playlist string of to the appropriate
    parser for the type
    '''

    def __init__(self, edl_string):
        self.timeline = otio.schema.Timeline()
        self.playlist_type = None

        self._parse_playlist(edl_string)

    def _parse_playlist(self, edl_string):

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

            # identify if the playlist start is encountered
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
                "could not determine playlist type")
        elif self.playlist_type == PlaylistType.master:
            self.timeline = None
            raise otio.exceptions.AdapterDoesntSupportFunction(
                "HLS master playlists are not yet supported")
        elif self.playlist_type == PlaylistType.media:
            parser = MediaPlaylistParser(playlist_entries, playlist_version)
            if len(parser.sequence):
                self.timeline.tracks.append(parser.sequence)


class MediaPlaylistParser(object):
    '''
    Parses an HLS Media playlist returning a sequence
    '''

    def __init__(self, playlist_entries, playlist_version=None):
        self.sequence = otio.schema.Sequence(
            metadata={'HLS': {}}
        )

        self._parse_entries(playlist_entries, playlist_version)

    def _handle_sequence_metadata(self, entry, playlist_version, clip):
        '''
        Stashes the tag value in the sequence metadata
        '''
        value = entry.tag_value
        self.sequence.metadata['HLS'][entry.tag_name] = value

    def _metadata_dict_for_MAP(self, entry, playlist_version):
        entry_data = entry.parsed_tag_value()
        attributes = entry_data['attributes']
        map_dict = {}
        for attr, value in attributes.iteritems():
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
        # First, stash the raw value
        reference_metadata = clip.media_reference.metadata
        reference_metadata['HLS'][entry.tag_name] = entry.tag_value

        # Pull out the byte count and offset
        byterange = Byterange.from_match_dict(
            entry.parsed_tag_value(playlist_version)
        )
        reference_metadata.update(byterange.to_dict())

    TAG_HANDLERS = {
        "EXTINF": _handle_INF,
        PLAYLIST_VERSION_TAG: _handle_sequence_metadata,
        "EXT-X-TARGETDURATION": _handle_sequence_metadata,
        "EXT-X-MEDIA-SEQUENCE": _handle_sequence_metadata,
        "EXT-X-PLAYLIST-TYPE": _handle_sequence_metadata,
        "EXT-X-INDEPENDENT-SEGMENTS": _handle_sequence_metadata,
        "EXT-X-BYTERANGE": _handle_BYTERANGE
    }

    def _parse_entries(self, playlist_entries, playlist_version):
        ''' interpret the entries through the lens of the schema '''
        current_media_ref = otio.media_reference.External(metadata={'HLS': {}})
        current_clip = otio.schema.Clip(
            media_reference=current_media_ref
        )
        segment_metadata = {}
        current_map_data = {}
        # per section 4.3.3.2 of Pantos HLS, 0 is default start sequence
        current_sequence = 0
        for entry in playlist_entries:
            if entry.type == EntryType.URI:
                # the URI ends the segment definition
                current_media_ref.target_url = entry.uri
                current_media_ref.metadata['HLS'].update(segment_metadata)
                current_media_ref.metadata.update(current_map_data)
                current_clip.metadata[SEQUENCE_NUM_KEY] = current_sequence
                self.sequence.append(current_clip)
                current_sequence += 1

                current_media_ref = otio.media_reference.External(
                    metadata={'HLS': {}}
                )
                current_clip = otio.schema.Clip(
                    media_reference=current_media_ref
                )
                continue
            elif entry.type != EntryType.tag:
                # the rest of the code deals only with tags
                continue

            # Explode the EXT-X-MAP info out
            if entry.tag_name == "EXT-X-MAP":
                map_data = self._metadata_dict_for_MAP(entry, playlist_version)
                current_map_data.update(map_data)

            # Grab the sequence when it comes around
            if entry.tag_name == "EXT-X-MEDIA-SEQUENCE":
                entry_data = entry.parsed_tag_value()
                current_sequence = int(entry_data['number'])

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

            # add the tag to the reference metadata
            if entry.tag_name in [PLAYLIST_START_TAG, PLAYLIST_END_TAG]:
                continue
            elif entry.tag_name in MEDIA_SEGMENT_TAGS:
                current_media_ref.metadata['HLS'][entry.tag_name] =\
                    entry.tag_value
            elif entry.tag_name in MEDIA_PLAYLIST_TAGS:
                self.sequence.metadata['HLS'][entry.tag_name] = entry.tag_value

'''
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
'''
def master_playlist_to_string(master_timeline):
    '''
    Writes a master playlist describing the tracks
    '''
    # start with a version number of 1, as features are encountered, we will
    # update the version accordingly
    version_requirements = set([1])

    # TODO: detect rather than forcing version 6
    version_requirements.add(6)
    
    header_tags = copy.copy(master_timeline.metadata.get('HLS', {}))
    
    playlist_entries = []

    # First declare the non-visual media
    hls_type_count = {}
    video_tracks = []
    audio_tracks = (
            t for t in master_timeline.tracks if
            t.kind == otio.schema.SequenceKind.Audio
    )
    for track in master_timeline.tracks:
        if track.kind == otio.schema.SequenceKind.Video:
            # video is done later, skip
            video_tracks.append(track)
            continue

        # Determine the HLS type
        hls_type = OTIO_TRACK_KIND_TO_HLS_TYPE[track.kind]

        # Find the group name
        try:
            group_id = track.metadata['group_id']
        except KeyError:
            sub_id = hls_type_count.setdefault(hls_type, 1)
            group_id = '{}{}'.format(hls_type, sub_id)
            hls_type_count[hls_type] += 1
        
        uri = track.name + '.m3u8'

        # Build the attribute list
        attributes = AttributeList([
                ('TYPE', hls_type),
                ('GROUP-ID', group_id),
                ('URI', uri),
                ('NAME', track.name),
        ])

        if track.metadata.get('autoselect'):
            attributes['AUTOSELECT'] = AttributeListEnum('YES')

        if track.metadata.get('default'):
            attributes['DEFAULT'] = AttributeListEnum('YES')

        # Finally, create the tag
        entry = HLSPlaylistEntry.tag_entry(
                'EXT-X-MEDIA',
                str(attributes)
        )

        playlist_entries.append(entry)

    for track in video_tracks:
        # create the base attribute list for the video track
        bandwidth = track.metadata['bandwidth']
        codec = track.metadata['codec']
        resolution = "{}x{}".format(
                track.metadata['width'],
                track.metadata['height']
        )
        frame_rate = track.metadata['frame_rate']

        al = AttributeList([
                ('BANDWIDTH', bandwidth),
                ('CODECS', codec),
                ('RESOLUTION', AttributeListEnum(resolution)),
                ('FRAME-RATE', frame_rate)
        ])

        # Create the uri
        uri_entry = HLSPlaylistEntry.uri_entry(
                "{}.m3u8".format(track.name)
        )
        
        # TODO: this will break when we have subtitle and CC tracks
        added_entry = False
        for audio_track in audio_tracks:
            if track.name not in audio_track.metadata['linked_tracks']:
                continue

            # Write an entry for using these together
            aud_group = audio_track.metadata['group_id']
            
            combo_al = copy.copy(al)
            combo_al['CODECS'] += ',{}'.format(audio_track.metadata['codec'])
            combo_al['AUDIO'] = aud_group

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

    out_entries = [HLSPlaylistEntry.tag_entry(PLAYLIST_START_TAG, None)]

    playlist_version = max(version_requirements)
    playlist_version_entry = HLSPlaylistEntry.tag_entry(
        PLAYLIST_VERSION_TAG,
        str(playlist_version)
    )

    out_entries.append(playlist_version_entry)

    out_entries += (
            HLSPlaylistEntry.tag_entry(k,v) for k,v in header_tags.iteritems()
    )

    out_entries += playlist_entries
    
    playlist_string = '\n'.join(
        (str(entry) for entry in out_entries)
    )

    return playlist_string

def media_playlist_to_string(media_sequence):
    '''
    Writes a media playlist for an OTIO Sequence
    '''
    # start with a version number of 1, as features are encountered, we will
    # update the version accordingly
    version_requirements = set([1])

    # TODO: detect rather than forcing version 7
    version_requirements.add(7)

    # seed the intial playlist-global tag values
    playlist_tags = {
        'EXT-X-PLAYLIST-TYPE': 'VOD',
    }

    # Grab any metadata provided on the otio
    try:
        sequence_metadata = media_sequence.metadata['HLS']
        playlist_tags.update(sequence_metadata)
    except KeyError:
        pass

    # Setup the sequence start
    try:
        sequence_start = media_sequence[0].metadata[SEQUENCE_NUM_KEY]
    except KeyError:
        sequence_start = None

    if (sequence_start is not None or
            'EXT-X-MEDIA-SEQUENCE' not in playlist_tags):

        # Choose a reasonable sequence start default
        if sequence_start is None:
            sequence_start = 1
        playlist_tags['EXT-X-MEDIA-SEQUENCE'] = str(sequence_start)

    # Set the duration
    duration = media_sequence.computed_duration()
    duration_seconds = math.ceil(float(duration.value) / float(duration.rate))
    playlist_tags['EXT-X-TARGETDURATION'] = str(int(duration_seconds))

    # Remove the version tag from the sequence metadata, we'll compute it
    # based on what we write out
    try:
        del(playlist_tags[PLAYLIST_VERSION_TAG])
    except KeyError:
        pass

    # iterate through the clips and serialize
    playlist_entries = []
    last_init_uri = None
    last_init_byterange = None
    for clip in media_sequence:
        media_ref = clip.media_reference
        # build a tag dict for the segment
        segment_tags = clip.media_reference.metadata.get('HLS', {})

        # see if the map needs updating
        try:
            seg_map_uri = media_ref.metadata[INIT_URI_KEY]
            seg_map_byterange_dict = media_ref.metadata.get(INIT_BYTERANGE_KEY)
            seg_map_byterange = Byterange.from_dict(seg_map_byterange_dict)
            if (seg_map_uri != last_init_uri or
                    seg_map_byterange != last_init_byterange):
                map_attr_list = AttributeList([
                    ('URI', seg_map_uri),
                    ('BYTERANGE', str(seg_map_byterange))
                ])
                map_tag_str = str(map_attr_list)
                entry = HLSPlaylistEntry.tag_entry(
                    "EXT-X-MAP",
                    map_tag_str
                )
                playlist_entries.append(entry)

                last_init_uri = seg_map_uri
                last_init_byterange = seg_map_byterange

        except KeyError:
            pass

        # if we're managing the MAP, strip it from the metadata
        if last_init_uri:
            try:
                del(segment_tags['EXT-X-MAP'])
            except KeyError:
                pass

        # add the byterange to the segment if needed
        try:
            byterange = Byterange.from_dict(media_ref.metadata)
            segment_tags['EXT-X-BYTERANGE'] = str(byterange)
        except KeyError:
            pass

        # add the tags
        playlist_entries += (HLSPlaylistEntry.tag_entry(k, v) for k, v in
                             segment_tags.iteritems())

        # add the EXTINF
        clip_duration = clip.computed_duration()
        clip_duration_seconds = (float(clip_duration.value) /
                                 float(clip_duration.rate))
        tag_value = '{0:.5f},{1}'.format(
            clip_duration_seconds,
            (clip.name if clip.name else '')
        )
        entry = HLSPlaylistEntry.tag_entry('EXTINF', tag_value)
        playlist_entries.append(entry)

        # Add the URI
        entry = HLSPlaylistEntry.uri_entry(media_ref.target_url)
        playlist_entries.append(entry)

    # add the end
    end_entry = HLSPlaylistEntry.tag_entry(PLAYLIST_END_TAG)
    playlist_entries.append(end_entry)

    # now that we know what was used, let's prepend the header
    playlist_header_entries = [HLSPlaylistEntry.tag_entry(PLAYLIST_START_TAG)]
    playlist_version = max(version_requirements)
    playlist_version_entry = HLSPlaylistEntry.tag_entry(
        PLAYLIST_VERSION_TAG,
        str(playlist_version)
    )
    playlist_header_entries.append(playlist_version_entry)

    playlist_header_entries += (HLSPlaylistEntry.tag_entry(k, v) for k, v in
                                playlist_tags.iteritems())

    playlist_string = '\n'.join(
        (str(entry) for entry in playlist_header_entries)
    )
    playlist_string += '\n'
    playlist_string += '\n'.join(
        (str(entry) for entry in playlist_entries)
    )

    return playlist_string

# Public interface

def read_from_string(input_str):
    parser = HLSPlaylistParser(input_str)
    return parser.timeline



def write_to_string(input_otio):
    if len(input_otio.tracks) == 0:
        return None

    if len(input_otio.tracks) == 1:
        media_sequence = input_otio.tracks[0]
        return media_playlist_to_string(media_sequence)
    else:
        return master_playlist_to_string(input_otio)


