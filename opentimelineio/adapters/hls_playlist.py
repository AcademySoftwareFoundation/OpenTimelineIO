import re

import opentimelineio as otio

#TODO: determine output version based on features used
OUTPUT_PLAYLIST_VERSION="7"

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
        r'(?P<AttributeValue>(?:\"[^\r\n"]*\")|[^,]+)'+ r',?')

BYTERANGE_RE = re.compile(r'(?P<n>\d+)(?:@(?P<o>\d+))?')

TAG_RE = re.compile(r'#(?P<tagname>EXT[^:\s]+):?(?P<tagvalue>.*)')
COMMENT_RE = re.compile(r'#(?!EXT)(?P<comment>.*)')

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
    for k,v in group_dict.iteritems():
        # not a successful group match
        if v is None:
            continue
        
        # decode the string
        if k in ('resolution', 'enumerated'):
            return v
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

def _parse_attribute_list(attribute_list_string):
    '''
    Accepts an attribute list string and returns a list of tuples where the
    first item is the Attribute name and the second is the attribute value.

    The values will be transformed to python types.
    '''
    attr_list = []
    match = ATTRIBUTE_RE.search(attribute_list_string)
    while match:
        # unpack the values from the match
        group_dict = match.groupdict()
        name = group_dict['AttributeName']
        raw_value = group_dict['AttributeValue']
        
        # parse the raw value
        value = _value_from_raw_attribute_value(raw_value)
        attr_list.append((name, value))
        
        # search for the next attribute in the string
        match_end = match.span()[1]
        match = ATTRIBUTE_RE.search(attribute_list_string, match_end)
    
    return attr_list

def _byte_range_dict_from_dict(byte_range_info):
    '''
    Accepts a raw dictionary resulting from BYTERANGE_RE and generates
    a dictionary with 'byte_count' and optionally 'byte_offset' key/value
    pairs.
    '''
    count = int(byte_range_info['n'])
    range_dict = {'byte_count': count}
    
    offset = byte_range_info['o']
    if offset:
        range_dict['byte_offset'] = int(offset)

    return range_dict

INIT_BYTERANGE_KEY = 'init_byterange'
INIT_URI_KEY = 'init_uri'

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
            base_str += ', comment={}'.format(repr(self.comment))
        elif self.type == EntryType.URI:
            base_str += ', URI={}'.format(repr(self.uri))

        return base_str + ')'
                
    @classmethod
    def from_string(cls, entry_string):
        # Empty lines are skipped
        if not entry_string.strip():
            return None

        # Attempt to parse as a tag
        m = TAG_RE.match(entry_string)
        if m:
            group_dict = m.groupdict()
            entry = cls(EntryType.tag)
            entry.tag_name = group_dict['tagname']
            entry.tag_value = group_dict['tagvalue']
            return entry

        # Attempt to parse as a comment
        m = COMMENT_RE.match(entry_string)
        if m:
            return m.groupdict()['comment']

        # If it's not the others, treat as a URI
        entry = cls(EntryType.URI)
        entry.uri = entry_string

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
            attr_list = _parse_attribute_list(attribute_list)
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
                metadata = {'HLS': {} }
        )

        self._parse_entries(playlist_entries, playlist_version)
    
    def _handle_sequence_metadata(self, entry, playlist_version, clip):
        '''
        Stashes the tag value in the sequence metadata
        '''
        value = entry.tag_value
        if entry.tag_name == "EXT-X-INDEPENDENT-SEGMENTS":
            value = True

        self.sequence.metadata['HLS'][entry.tag_name] = value

    def _metadata_dict_for_MAP(self, entry, playlist_version):
        entry_data = entry.parsed_tag_value()
        attributes = entry_data['attributes']
        map_dict = {}
        for attr, value in attributes:
            if attr == 'BYTERANGE':
                m = BYTERANGE_RE.match(value)
                range_dict = _byte_range_dict_from_dict(m.groupdict())
                map_dict[INIT_BYTERANGE_KEY] = range_dict
            elif attr == 'URI':
                map_dict[INIT_URI_KEY] = value

        return map_dict

    def _handle_INF(self, entry, playlist_version, clip):
        # This specifies segment duration and optional title
        info_dict = entry.parsed_tag_value(playlist_version)
        segment_duration = float(info_dict['duration'])
        segment_title = info_dict['title']
        available_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(0,1),
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
        byte_range_info = entry.parsed_tag_value(playlist_version)
        byte_range_dict = _byte_range_dict_from_dict(byte_range_info)
        reference_metadata.update(byte_range_dict)

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
                current_clip.metadata['seq_number'] = current_sequence
                self.sequence.append(current_clip)
                current_sequence += 1

                current_media_ref = otio.media_reference.External(
                        metadata = {'HLS':{}}
                )
                current_clip = otio.schema.Clip(
                        media_reference = current_media_ref
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

### Public interface
def read_from_string(input_str):
    parser = HLSPlaylistParser(input_str)
    return parser.timeline


