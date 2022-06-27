# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""OpenTimelineIO CMX 3600 EDL Adapter"""

# Note: this adapter is not an ideal model for new adapters, but it works.
# If you want to write your own adapter, please see:
# https://opentimelineio.readthedocs.io/en/latest/tutorials/write-an-adapter.html#

# TODO: Flesh out Attribute Handler
# TODO: Add line numbers to errors and warnings
# TODO: currently tracks with linked audio/video will lose their linkage when
#       read into OTIO.

import copy
import os
import re
import collections

from .. import (
    exceptions,
    schema,
    opentime,
)


class EDLParseError(exceptions.OTIOError):
    pass


# regex for parsing the playback speed of an M2 event
SPEED_EFFECT_RE = re.compile(
    r"(?P<name>.*?)\s*(?P<speed>-?[0-9\.]*)\s*(?P<tc>[0-9:]{11})$"
)


# these are all CMX_3600 transition codes
# the wipe is written in regex format because it is W### where the ### is
# a 'wipe code'
# @TODO: not currently read by the transition code
transition_regex_map = {
    'C': 'cut',
    'D': 'dissolve',
    r'W\d{3}': 'wipe',
    'KB': 'key_background',
    'K': 'key_foreground',
    'KO': 'key_overlay'
}

# CMX_3600 supports some shorthand for channel assignments
# We name the actual tracks V and A1,A2,A3,etc.
# This channel_map tells you which track to use for each channel shorthand.
# Channels not listed here are used as track names verbatim.
channel_map = {
    'A': ['A1'],
    'AA': ['A1', 'A2'],
    'B': ['V', 'A1'],
    'A2/V': ['V', 'A2'],
    'AA/V': ['V', 'A1', 'A2']
}


# Currently, the 'style' argument determines
# the comment string for the media reference:
#   'avid': '* FROM CLIP:' (default)
#   'nucoda': '* FROM FILE:'
# When adding a new style, please be sure to add sufficient tests
# to verify both the new and existing styles.
VALID_EDL_STYLES = ['avid', 'nucoda']


def _extend_source_range_duration(obj, duration):
    obj.source_range = obj.source_range.duration_extended_by(duration)


class EDLParser(object):
    def __init__(self, edl_string, rate=24, ignore_timecode_mismatch=False):
        self.timeline = schema.Timeline()

        # Start with no tracks. They will be added as we encounter them.
        # This dict maps a track name (e.g "A2" or "V") to an OTIO Track.
        self.tracks_by_name = {}

        self.ignore_timecode_mismatch = ignore_timecode_mismatch

        self.parse_edl(edl_string, rate=rate)

        # TODO: Sort the tracks V, then A1,A2,etc.

    def add_clip(self, line, comments, rate=24, transition_line=None):
        comment_handler = CommentHandler(comments)
        clip_handler = ClipHandler(
            line,
            comment_handler.handled,
            rate=rate,
            transition_line=transition_line
        )
        clip = clip_handler.clip
        transition = clip_handler.transition
        # Add unhandled comments as general comments to meta data.
        if comment_handler.unhandled:
            clip.metadata.setdefault("cmx_3600", {})
            clip.metadata['cmx_3600'].setdefault("comments", [])
            clip.metadata['cmx_3600']['comments'] += (
                comment_handler.unhandled
            )

        # Add reel name to metadata
        # A reel name of `AX` represents an unknown or auxilary source
        # We don't currently track these sources outside of this adapter
        # So lets skip adding AX reels as metadata for now,
        # as that would dirty json outputs with non-relevant information
        if clip_handler.reel and clip_handler.reel != 'AX':
            clip.metadata.setdefault("cmx_3600", {})
            clip.metadata['cmx_3600']['reel'] = clip_handler.reel

        edl_rate = clip_handler.edl_rate
        record_in = opentime.from_timecode(
            clip_handler.record_tc_in,
            edl_rate
        )
        record_out = opentime.from_timecode(
            clip_handler.record_tc_out,
            edl_rate
        )

        src_duration = clip.duration()
        rec_duration = record_out - record_in
        if rec_duration != src_duration:
            motion = comment_handler.handled.get('motion_effect')
            freeze = comment_handler.handled.get('freeze_frame')
            if motion is not None or freeze is not None:
                # Adjust the clip to match the record duration
                clip.source_range = opentime.TimeRange(
                    start_time=clip.source_range.start_time,
                    duration=rec_duration
                )

                if freeze is not None:
                    clip.effects.append(schema.FreezeFrame())
                    # XXX remove 'FF' suffix (writing edl will add it back)
                    if clip.name.endswith(' FF'):
                        clip.name = clip.name[:-3]
                elif motion is not None:
                    fps = float(
                        SPEED_EFFECT_RE.match(motion).group("speed")
                    )
                    time_scalar = fps / rate
                    clip.effects.append(
                        schema.LinearTimeWarp(time_scalar=time_scalar)
                    )

            elif self.ignore_timecode_mismatch:
                # Pretend there was no problem by adjusting the record_out.
                # Note that we don't actually use record_out after this
                # point in the code, since all of the subsequent math uses
                # the clip's source_range. Adjusting the record_out is
                # just to document what the implications of ignoring the
                # mismatch here entails.
                record_out = record_in + src_duration

            else:
                raise EDLParseError(
                    "Source and record duration don't match: {} != {}"
                    " for clip {}".format(
                        src_duration,
                        rec_duration,
                        clip.name
                    ))

        # Add clip instances to the tracks
        tracks = self.tracks_for_channel(clip_handler.channel_code)
        for track in tracks:
            track_transition = transition
            if len(tracks) > 1:
                track_clip = copy.deepcopy(clip)
                if transition:
                    track_transition = copy.deepcopy(transition)
            else:
                track_clip = clip

            if track.source_range is None:
                zero = opentime.RationalTime(0, edl_rate)
                track.source_range = opentime.TimeRange(
                    start_time=zero - record_in,
                    duration=zero
                )

            track_end = track.duration() - track.source_range.start_time
            if record_in < track_end:
                if self.ignore_timecode_mismatch:
                    # shift it over
                    record_in = track_end
                    record_out = record_in + rec_duration
                else:
                    raise EDLParseError(
                        "Overlapping record in value: {} for clip {}".format(
                            clip_handler.record_tc_in,
                            track_clip.name
                        ))

            # If the next clip is supposed to start beyond the end of the
            # clips we've accumulated so far, then we need to add a Gap
            # to fill that space. This can happen when an EDL has record
            # timecodes that are sparse (e.g. from a single track of a
            # multi-track composition).
            if record_in > track_end and len(track) > 0:
                gap = schema.Gap()
                gap.source_range = opentime.TimeRange(
                    start_time=opentime.RationalTime(0, edl_rate),
                    duration=record_in - track_end
                )
                track.append(gap)
                _extend_source_range_duration(track, gap.duration())

            if track_transition:
                if len(track) < 1:
                    raise EDLParseError(
                        "Transitions can't be at the very beginning of a track"
                    )
                track.append(track_transition)
            track.append(track_clip)
            _extend_source_range_duration(track, track_clip.duration())

    def guess_kind_for_track_name(self, name):
        if name.startswith("V"):
            return schema.TrackKind.Video
        if name.startswith("A"):
            return schema.TrackKind.Audio
        return schema.TrackKind.Video

    def tracks_for_channel(self, channel_code):
        # Expand channel shorthand into a list of track names.
        if channel_code in channel_map:
            track_names = channel_map[channel_code]
        else:
            track_names = [channel_code]

        # Create any channels we don't already have
        for track_name in track_names:
            if track_name not in self.tracks_by_name:
                track = schema.Track(
                    name=track_name,
                    kind=self.guess_kind_for_track_name(track_name)
                )
                self.tracks_by_name[track_name] = track
                self.timeline.tracks.append(track)

        # Return a list of actual tracks
        return [self.tracks_by_name[c] for c in track_names]

    def parse_edl(self, edl_string, rate=24):
        # edl 'events' can be comprised of an indeterminate amount of lines
        # we are to translating 'events' to a single clip and transition
        # then we add the transition and the clip to all channels the 'event'
        # channel code is mapped to the transition given in the 'event'
        # precedes the clip

        # remove all blank lines from the edl
        edl_lines = [
            line for line in
            (line.strip() for line in edl_string.splitlines()) if line
        ]

        while edl_lines:
            # a basic for loop wont work cleanly since we need to look ahead at
            # array elements to determine what type of 'event' we are looking
            # at
            line = edl_lines.pop(0)

            if line.startswith('TITLE:'):
                # this is the first line of interest in an edl
                # it is required to be in the header
                self.timeline.name = line.replace('TITLE:', '').strip()

            elif line.startswith('FCM'):
                # this can occur either in the header or before any 'event'
                # in both cases we can ignore it since it is meant for tape
                # timecode
                pass

            elif line.startswith('SPLIT'):
                # this is the only comment preceding an 'event' that we care
                # about in our context it simply means the next two clips will
                # have the same comment data it is for reading purposes only
                audio_delay = None
                video_delay = None

                if 'AUDIO DELAY' in line:
                    audio_delay = line.split()[-1].strip()
                if 'VIDEO DELAY' in line:
                    video_delay = line.split()[-1].strip()
                if audio_delay and video_delay:
                    raise EDLParseError(
                        'both audio and video delay declared after SPLIT.'
                    )
                if not (audio_delay or video_delay):
                    raise EDLParseError(
                        'either audio or video delay declared after SPLIT.'
                    )

                line_1 = edl_lines.pop(0)
                line_2 = edl_lines.pop(0)
                # TODO: check if transitions can happen in this case
                comments = []
                while edl_lines:
                    if re.match(r'^\D', edl_lines[0]):
                        comments.append(edl_lines.pop(0))
                    else:
                        break
                self.add_clip(line_1, comments, rate=rate)
                self.add_clip(line_2, comments, rate=rate)
            # Check if the first character in the line is a digit
            elif line[0].isdigit():
                transition_line = None
                # all 'events' start_time with an edit decision. this is
                # denoted by the line beginning with a padded integer 000-999
                comments = []
                event_id = int(re.match(r'^\d+', line).group(0))
                while edl_lines:
                    # Any non-numbered lines after an edit decision should be
                    # treated as 'comments'.
                    # Comments are string tags used by the reader to get extra
                    # information not able to be found in the restricted edl
                    # format.
                    # If the current event id is repeated it means that there is
                    # a transition between the current event and the preceding
                    # one. We collect it and process it when adding the clip.
                    m = re.match(r'^\d+', edl_lines[0])
                    if not m:
                        comments.append(edl_lines.pop(0))
                    else:
                        if int(m.group(0)) == event_id:
                            # It is not possible to have multiple transitions
                            # for the same event.
                            if transition_line:
                                raise EDLParseError(
                                    'Invalid transition %s' % edl_lines[0]
                                )
                            # Same event id, this is a transition
                            transition_line = edl_lines.pop(0)
                        else:
                            # New event, stop collecting comments and transitions
                            break

                self.add_clip(
                    line,
                    comments,
                    rate=rate,
                    transition_line=transition_line
                )
            else:
                raise EDLParseError('Unknown event type')

        for track in self.timeline.tracks:
            # if the source_range is the same as the available_range
            # then we don't need to set it at all.
            if track.source_range == track.available_range():
                track.source_range = None


class ClipHandler(object):
    # /path/filename.[1001-1020].ext
    image_sequence_pattern = re.compile(
        r'.*\.(?P<range>\[(?P<start>[0-9]+)-(?P<end>[0-9]+)\])\.\w+$'
    )

    def __init__(self, line, comment_data, rate=24, transition_line=None):
        self.clip_num = None
        self.reel = None
        self.channel_code = None
        self.edl_rate = rate
        self.transition_id = None
        self.transition_data = None
        self.transition_type = None
        self.source_tc_in = None
        self.source_tc_out = None
        self.record_tc_in = None
        self.record_tc_out = None
        self.clip = None
        self.transition = None
        self.parse(line)
        if transition_line:
            self.parse(transition_line)
        self.clip = self.make_clip(comment_data)
        if transition_line:
            self.transition = self.make_transition(comment_data)

    def is_image_sequence(self, comment_data):
        return self.image_sequence_pattern.search(
            comment_data['media_reference']
        ) is not None

    def create_imagesequence_reference(self, comment_data):
        regex_obj = self.image_sequence_pattern.search(
            comment_data['media_reference']
        )

        path, basename = os.path.split(comment_data['media_reference'])
        prefix, suffix = basename.split(regex_obj.group('range'))
        ref = schema.ImageSequenceReference(
            target_url_base=path,
            name_prefix=prefix,
            name_suffix=suffix,
            rate=self.edl_rate,
            start_frame=int(regex_obj.group('start')),
            frame_zero_padding=len(regex_obj.group('start')),
            available_range=opentime.range_from_start_end_time(
                opentime.from_timecode(self.source_tc_in, self.edl_rate),
                opentime.from_timecode(self.source_tc_out, self.edl_rate)
            )
        )

        return ref

    def make_clip(self, comment_data):
        clip = schema.Clip()
        clip.name = str(self.clip_num)

        # BLACK/BL and BARS are called out as "Special Source Identifiers" in
        # the documents referenced here:
        # https://github.com/AcademySoftwareFoundation/OpenTimelineIO#cmx3600-edl
        if self.reel in ['BL', 'BLACK']:
            clip.media_reference = schema.GeneratorReference()
            # TODO: Replace with enum, once one exists
            clip.media_reference.generator_kind = 'black'
        elif self.reel == 'BARS':
            clip.media_reference = schema.GeneratorReference()
            # TODO: Replace with enum, once one exists
            clip.media_reference.generator_kind = 'SMPTEBars'
        elif 'media_reference' in comment_data:
            if self.is_image_sequence(comment_data):
                clip.media_reference = self.create_imagesequence_reference(
                    comment_data
                )
            else:
                clip.media_reference = schema.ExternalReference()
                clip.media_reference.target_url = comment_data[
                    'media_reference'
                ]
        else:
            clip.media_reference = schema.MissingReference()

        # this could currently break without a 'FROM CLIP' comment.
        # Without that there is no 'media_reference' Do we have a default
        # clip name?
        if 'clip_name' in comment_data:
            clip.name = comment_data["clip_name"]
        elif (
            clip.media_reference and
            hasattr(clip.media_reference, 'target_url') and
            clip.media_reference.target_url is not None
        ):
            clip.name = os.path.splitext(
                os.path.basename(clip.media_reference.target_url)
            )[0]

        elif (
            clip.media_reference and
            hasattr(clip.media_reference, 'target_url_base') and
            clip.media_reference.target_url_base is not None
        ):
            clip.name = os.path.splitext(
                os.path.basename(_get_image_sequence_url(clip))
            )[0]

        asc_sop = comment_data.get('asc_sop', None)
        asc_sat = comment_data.get('asc_sat', None)
        if asc_sop or asc_sat:
            slope = (1, 1, 1)
            offset = (0, 0, 0)
            power = (1, 1, 1)
            sat = 1.0

            if asc_sop:
                triple = r'([-+]?[\d.]+),? ([-+]?[\d.]+),? ([-+]?[\d.]+),?'
                m = re.match(
                    r'\('
                    + triple
                    + r'\)\s*\('
                    + triple + r'\)\s*\('
                    + triple + r'\)',
                    asc_sop
                )
                if m:
                    floats = [float(g) for g in m.groups()]
                    slope = [floats[0], floats[1], floats[2]]
                    offset = [floats[3], floats[4], floats[5]]
                    power = [floats[6], floats[7], floats[8]]
                else:
                    raise EDLParseError(
                        'Invalid ASC_SOP found: {}'.format(asc_sop))

            if asc_sat:
                sat = float(asc_sat)

            clip.metadata['cdl'] = {
                'asc_sat': sat,
                'asc_sop': {
                    'slope': slope,
                    'offset': offset,
                    'power': power
                }
            }

        # Get the clip name from "TO CLIP NAME" if present
        if 'dest_clip_name' in comment_data:
            clip.name = comment_data['dest_clip_name']

        if 'locators' in comment_data:
            # An example EDL locator line looks like this:
            # * LOC: 01:00:01:14 RED     ANIM FIX NEEDED
            # We get the part after "LOC: " as the comment_data entry
            # Given the fixed-width nature of these, we could be more
            # strict about the field widths, but there are many
            # variations of EDL, so if we are lenient then maybe we
            # can handle more of them? Only real-world testing will
            # determine this for sure...
            for locator in comment_data['locators']:
                m = re.match(
                    r'(\d\d:\d\d:\d\d:\d\d)\s+(\w*)(\s+|$)(.*)',
                    locator
                )
                if not m:
                    # TODO: Should we report this as a warning somehow?
                    continue

                marker = schema.Marker()
                marker.marked_range = opentime.TimeRange(
                    start_time=opentime.from_timecode(
                        m.group(1),
                        self.edl_rate
                    ),
                    duration=opentime.RationalTime()
                )

                # always write the source value into metadata, in case it
                # is not a valid enum somehow.
                color_parsed_from_file = m.group(2)

                marker.metadata.update({
                    "cmx_3600": {
                        "color": color_parsed_from_file
                    }
                })

                # @TODO: if it is a valid
                if hasattr(
                    schema.MarkerColor,
                    color_parsed_from_file.upper()
                ):
                    marker.color = color_parsed_from_file.upper()
                else:
                    marker.color = schema.MarkerColor.RED

                marker.name = m.group(4)
                clip.markers.append(marker)

        clip.source_range = opentime.range_from_start_end_time(
            opentime.from_timecode(self.source_tc_in, self.edl_rate),
            opentime.from_timecode(self.source_tc_out, self.edl_rate)
        )

        return clip

    def parse(self, line):
        fields = tuple(e.strip() for e in line.split() if e.strip())
        field_count = len(fields)

        if field_count == 9:
            # has transition data
            # this is for edits with timing or other needed info
            # transition data for D and W*** transitions is a n integer that
            # denotes frame count
            # i haven't figured out how the key transitions (K, KB, KO) work
            (
                self.transition_id,
                self.reel,
                self.channel_code,
                self.transition_type,
                self.transition_data,
                self.source_tc_in,
                self.source_tc_out,
                self.record_tc_in,
                self.record_tc_out
            ) = fields

        elif field_count == 8:
            edit_type = None
            # no transition data
            # this is for basic cuts
            (
                self.clip_num,
                self.reel,
                self.channel_code,
                edit_type,
                self.source_tc_in,
                self.source_tc_out,
                self.record_tc_in,
                self.record_tc_out
            ) = fields
            # Double check it is a cut
            if edit_type not in ["C"]:
                raise EDLParseError(
                    'incorrect edit type {} in form statement: {}'.format(
                        edit_type, line,
                    )
                )
        else:
            raise EDLParseError(
                'incorrect number of fields [{0}] in form statement: {1}'
                ''.format(field_count, line))

        # Frame numbers (not just timecode) are ok
        for prop in [
            'source_tc_in',
            'source_tc_out',
            'record_tc_in',
            'record_tc_out'
        ]:
            if ':' not in getattr(self, prop):
                setattr(
                    self,
                    prop,
                    opentime.to_timecode(
                        opentime.from_frames(
                            int(getattr(self, prop)),
                            self.edl_rate
                        ),
                        self.edl_rate
                    )
                )

    def make_transition(self, comment_data):
        # Do some sanity check
        if not self.clip:
            raise RuntimeError("Transitions can't be handled without a clip")
        if self.transition_id != self.clip_num:
            raise EDLParseError(
                'transition and event id mismatch: {} vs {}'.format(
                    self.transaction_id, self.clip_num,
                )
            )
        if re.match(r'W(\d{3})', self.transition_type):
            otio_transition_type = "SMPTE_Wipe"
        elif self.transition_type in ['D']:
            otio_transition_type = schema.TransitionTypes.SMPTE_Dissolve
        else:
            raise EDLParseError(
                "Transition type '{}' not supported by the CMX EDL reader "
                "currently.".format(self.transition_type)
            )
        # TODO: support delayed transition like described here:
        # https://xmil.biz/EDL-X/CMX3600.pdf
        transition_duration = opentime.RationalTime(
            float(self.transition_data),
            self.clip.source_range.duration.rate
        )
        # Note: Transitions in EDLs are unconventionally represented.
        #
        # Where a transition might normally be visualized like:
        #            |---57.0 Trans 43.0----|
        # |------Clip1 102.0------|----------Clip2 143.0----------|Clip3 24.0|
        #
        # In an EDL it can be thought of more like this:
        #            |---0.0 Trans 100.0----|
        # |Clip1 45.0|----------------Clip2 200.0-----------------|Clip3 24.0|
        #
        # So the transition starts at the beginning of the clip with `duration`
        # frames from the previous clip.

        # Give the transition a detailed name if we can
        transition_name = '{} to {}'.format(
            otio_transition_type,
            self.clip.name,
        )
        if 'dest_clip_name' in comment_data:
            if 'clip_name' in comment_data:
                transition_name = '{} from {} to {}'.format(
                    otio_transition_type,
                    comment_data['clip_name'],
                    comment_data['dest_clip_name'],
                )

        new_trx = schema.Transition(
            name=transition_name,
            # only supported type at the moment
            transition_type=otio_transition_type,
            metadata={
                'cmx_3600': {
                    'transition': self.transition_type,
                    'transition_duration': transition_duration.value,
                }
            },
        )
        new_trx.in_offset = opentime.RationalTime(
            0,
            transition_duration.rate
        )
        new_trx.out_offset = transition_duration
        return new_trx


class CommentHandler(object):
    # this is the for that all comment 'id' tags take
    regex_template = r'\*?\s*{id}:?\s*(?P<comment_body>.*)'

    # this should be a map of all known comments that we can read
    # 'FROM CLIP' or 'FROM FILE' is a required comment to link media
    # An exception is raised if both 'FROM CLIP' and 'FROM FILE' are found
    # needs to be ordered so that FROM CLIP NAME gets matched before FROM CLIP
    comment_id_map = collections.OrderedDict([
        ('FROM CLIP NAME', 'clip_name'),
        ('TO CLIP NAME', 'dest_clip_name'),
        ('FROM CLIP', 'media_reference'),
        ('FROM FILE', 'media_reference'),
        ('LOC', 'locators'),
        ('ASC_SOP', 'asc_sop'),
        ('ASC_SAT', 'asc_sat'),
        ('M2', 'motion_effect'),
        ('\\* FREEZE FRAME', 'freeze_frame'),
    ])

    def __init__(self, comments):
        self.handled = {}
        self.unhandled = []
        for comment in comments:
            self.parse(comment)

    def parse(self, comment):
        for comment_id, comment_type in self.comment_id_map.items():
            regex = self.regex_template.format(id=comment_id)
            match = re.match(regex, comment)
            if match:
                comment_body = match.group('comment_body').strip()

                # Special case for locators. There can be multiple locators per clip.
                if comment_type == 'locators':
                    try:
                        self.handled[comment_type].append(comment_body)
                    except KeyError:
                        self.handled[comment_type] = [comment_body]

                else:
                    self.handled[comment_type] = comment_body

                break
        else:
            stripped = comment.lstrip('*').strip()
            if stripped:
                self.unhandled.append(stripped)


def read_from_string(input_str, rate=24, ignore_timecode_mismatch=False):
    """Reads a CMX Edit Decision List (EDL) from a string.
    Since EDLs don't contain metadata specifying the rate they are meant
    for, you may need to specify the rate parameter (default is 24).
    By default, read_from_string will throw an exception if it discovers
    invalid timecode in the EDL. For example, if a clip's record timecode
    overlaps with the previous cut. Since this is a common mistake in
    many EDLs, you can specify ignore_timecode_mismatch=True, which will
    supress these errors and attempt to guess at the correct record
    timecode based on the source timecode and adjacent cuts.
    For best results, you may wish to do something like this:

    Example:
        >>> try:
        ...     timeline = otio.adapters.read_from_string("mymovie.edl", rate=30)
        ... except EDLParseError:
        ...    print('Log a warning here')
        ...    try:
        ...        timeline = otio.adapters.read_from_string(
        ...            "mymovie.edl",
        ...            rate=30,
        ...            ignore_timecode_mismatch=True)
        ...    except EDLParseError:
        ...        print('Log an error here')
    """
    parser = EDLParser(
        input_str,
        rate=float(rate),
        ignore_timecode_mismatch=ignore_timecode_mismatch
    )
    result = parser.timeline
    return result


def write_to_string(input_otio, rate=None, style='avid', reelname_len=8):
    # TODO: We should have convenience functions in Timeline for this?
    # also only works for a single video track at the moment

    video_tracks = [t for t in input_otio.tracks
                    if t.kind == schema.TrackKind.Video and t.enabled]
    audio_tracks = [t for t in input_otio.tracks
                    if t.kind == schema.TrackKind.Audio and t.enabled]

    if len(video_tracks) != 1:
        raise exceptions.NotSupportedError(
            "Only a single video track is supported, got: {}".format(
                len(video_tracks)
            )
        )

    if len(audio_tracks) > 2:
        raise exceptions.NotSupportedError(
            "No more than 2 audio tracks are supported."
        )
    # if audio_tracks:
    #     raise exceptions.NotSupportedError(
    #         "No audio tracks are currently supported."
    #     )

    # TODO: We should try to detect the frame rate and output an
    # appropriate "FCM: NON-DROP FRAME" etc here.

    writer = EDLWriter(
        tracks=input_otio.tracks,
        # Assume all rates are the same as the 1st track's
        rate=rate or input_otio.tracks[0].duration().rate,
        style=style,
        reelname_len=reelname_len
    )

    return writer.get_content_for_track_at_index(0, title=input_otio.name)


class EDLWriter(object):
    def __init__(self, tracks, rate, style, reelname_len=8):
        self._tracks = tracks
        self._rate = rate
        self._style = style
        self._reelname_len = reelname_len

        if style not in VALID_EDL_STYLES:
            raise exceptions.NotSupportedError(
                "The EDL style '{}' is not supported.".format(
                    style
                )
            )

    def get_content_for_track_at_index(self, idx, title):
        track = self._tracks[idx]

        # Add a gap if the last child is a transition.
        if isinstance(track[-1], schema.Transition):
            gap = schema.Gap(
                source_range=opentime.TimeRange(
                    start_time=track[-1].duration(),
                    duration=opentime.RationalTime(0.0, self._rate)
                )
            )
            track.append(gap)

        # Note: Transitions in EDLs are unconventionally represented.
        #
        # Where a transition might normally be visualized like:
        #            |---57.0 Trans 43.0----|
        # |------Clip1 102.0------|----------Clip2 143.0----------|Clip3 24.0|
        #
        # In an EDL it can be thought of more like this:
        #            |---0.0 Trans 100.0----|
        # |Clip1 45.0|----------------Clip2 200.0-----------------|Clip3 24.0|

        # Adjust cut points to match EDL event representation.
        for idx, child in enumerate(track):
            if isinstance(child, schema.Transition):
                if idx != 0:
                    # Shorten the a-side
                    _extend_source_range_duration(track[idx - 1], -child.in_offset)

                # Lengthen the b-side
                sr = track[idx + 1].source_range
                track[idx + 1].source_range = opentime.TimeRange(
                    sr.start_time - child.in_offset,
                    sr.duration + child.in_offset
                )

                # Just clean up the transition for goodness sake
                in_offset = child.in_offset
                child.in_offset = opentime.RationalTime(0.0, self._rate)
                child.out_offset += in_offset

        # Group events into either simple clip/a-side or transition and b-side
        # to match EDL edit/event representation and edit numbers.
        events = []
        for idx, child in enumerate(track):
            if isinstance(child, schema.Transition):
                # Transition will be captured in subsequent iteration.
                continue

            prv = track[idx - 1] if idx > 0 else None

            if isinstance(prv, schema.Transition):
                events.append(
                    DissolveEvent(
                        events[-1] if len(events) else None,
                        prv,
                        child,
                        self._tracks,
                        track.kind,
                        self._rate,
                        self._style,
                        self._reelname_len
                    )
                )
            elif isinstance(child, schema.Clip):
                if child.enabled:
                    events.append(
                        Event(
                            child,
                            self._tracks,
                            track.kind,
                            self._rate,
                            self._style,
                            self._reelname_len
                        )
                    )
                else:
                    pass
            elif isinstance(child, schema.Gap):
                # Gaps are represented as missing record timecode, no event
                # needed.
                pass

        content = "TITLE: {}\n\n".format(title) if title else ''
        if track.enabled:
            # Convert each event/dissolve-event into plain text.
            for idx, event in enumerate(events):
                event.edit_number = idx + 1
                content += event.to_edl_format() + '\n'

        return content


def _supported_timing_effects(clip):
    return [
        fx for fx in clip.effects
        if isinstance(fx, schema.LinearTimeWarp)
    ]


def _relevant_timing_effect(clip):
    # check to see if there is more than one timing effect
    effects = _supported_timing_effects(clip)

    if effects != clip.effects:
        for thing in clip.effects:
            if thing not in effects and isinstance(thing, schema.TimeEffect):
                raise exceptions.NotSupportedError(
                    "Clip contains timing effects not supported by the EDL"
                    " adapter.\nClip: {}".format(str(clip)))

    timing_effect = None
    if effects:
        timing_effect = effects[0]
    if len(effects) > 1:
        raise exceptions.NotSupportedError(
            "EDL Adapter only allows one timing effect / clip."
        )

    return timing_effect


class Event(object):
    def __init__(
        self,
        clip,
        tracks,
        kind,
        rate,
        style,
        reelname_len
    ):

        line = EventLine(kind, rate, reel=_reel_from_clip(clip, reelname_len))
        line.source_in = clip.source_range.start_time
        line.source_out = clip.source_range.end_time_exclusive()

        timing_effect = _relevant_timing_effect(clip)

        if timing_effect:
            if timing_effect.effect_name == "FreezeFrame":
                line.source_out = line.source_in + opentime.RationalTime(
                    1,
                    line.source_in.rate
                )
            elif timing_effect.effect_name == "LinearTimeWarp":
                value = clip.trimmed_range().duration.value / timing_effect.time_scalar
                line.source_out = (
                    line.source_in + opentime.RationalTime(value, rate))

        range_in_timeline = clip.transformed_time_range(
            clip.trimmed_range(),
            tracks
        )
        line.record_in = range_in_timeline.start_time
        line.record_out = range_in_timeline.end_time_exclusive()
        self.line = line

        self.comments = _generate_comment_lines(
            clip=clip,
            style=style,
            edl_rate=rate,
            reelname_len=reelname_len,
            from_or_to='FROM'
        )

        self.clip = clip
        self.source_out = line.source_out
        self.record_out = line.record_out
        self.reel = line.reel

    def __str__(self):
        return '{type}({name})'.format(
            type=self.clip.schema_name(),
            name=self.clip.name
        )

    def to_edl_format(self):
        """
        Example output:
            002 AX V C        00:00:00:00 00:00:00:05 00:00:00:05 00:00:00:10
            * FROM CLIP NAME:  test clip2
            * FROM FILE: S:\\var\\tmp\\test.exr

        """
        lines = [self.line.to_edl_format(self.edit_number)]
        lines += self.comments if len(self.comments) else []

        return "\n".join(lines)


class DissolveEvent(object):

    def __init__(
        self,
        a_side_event,
        transition,
        b_side_clip,
        tracks,
        kind,
        rate,
        style,
        reelname_len
    ):
        # Note: We don't make the A-Side event line here as it is represented
        # by its own event (edit number).

        cut_line = EventLine(kind, rate)

        if a_side_event:
            cut_line.reel = a_side_event.reel
            cut_line.source_in = a_side_event.source_out
            cut_line.source_out = a_side_event.source_out
            cut_line.record_in = a_side_event.record_out
            cut_line.record_out = a_side_event.record_out

            self.from_comments = _generate_comment_lines(
                clip=a_side_event.clip,
                style=style,
                edl_rate=rate,
                reelname_len=reelname_len,
                from_or_to='FROM'
            )
        else:
            cut_line.reel = 'BL'
            cut_line.source_in = opentime.RationalTime(0.0, rate)
            cut_line.source_out = opentime.RationalTime(0.0, rate)
            cut_line.record_in = opentime.RationalTime(0.0, rate)
            cut_line.record_out = opentime.RationalTime(0.0, rate)

        self.cut_line = cut_line

        dslve_line = EventLine(
            kind,
            rate,
            reel=_reel_from_clip(b_side_clip, reelname_len)
        )
        dslve_line.source_in = b_side_clip.source_range.start_time
        dslve_line.source_out = b_side_clip.source_range.end_time_exclusive()
        range_in_timeline = b_side_clip.transformed_time_range(
            b_side_clip.trimmed_range(),
            tracks
        )
        dslve_line.record_in = range_in_timeline.start_time
        dslve_line.record_out = range_in_timeline.end_time_exclusive()
        dslve_line.dissolve_length = transition.out_offset
        self.dissolve_line = dslve_line

        self.to_comments = _generate_comment_lines(
            clip=b_side_clip,
            style=style,
            edl_rate=rate,
            reelname_len=reelname_len,
            from_or_to='TO'
        )

        self.a_side_event = a_side_event
        self.transition = transition
        self.b_side_clip = b_side_clip

        # Expose so that any subsequent dissolves can borrow their values.
        self.clip = b_side_clip
        self.source_out = dslve_line.source_out
        self.record_out = dslve_line.record_out
        self.reel = dslve_line.reel

    def __str__(self):
        a_side = self.a_side_event
        return '{a_type}({a_name}) -> {b_type}({b_name})'.format(
            a_type=a_side.clip.schema_name() if a_side else '',
            a_name=a_side.clip.name if a_side else '',
            b_type=self.b_side_clip.schema_name(),
            b_name=self.b_side_clip.name
        )

    def to_edl_format(self):
        """
        Example output:

        Cross dissolve...
        002 Clip1 V C     00:00:07:08 00:00:07:08 00:00:01:21 00:00:01:21
        002 Clip2 V D 100 00:00:09:07 00:00:17:15 00:00:01:21 00:00:10:05
        * FROM CLIP NAME:  Clip1
        * FROM CLIP: /var/tmp/clip1.001.exr
        * TO CLIP NAME:  Clip2
        * TO CLIP: /var/tmp/clip2.001.exr

        Fade in...
        001 BL      V C     00:00:00:00 00:00:00:00 00:00:00:00 00:00:00:00
        001 My_Clip V D 012 00:00:02:02 00:00:03:04 00:00:00:00 00:00:01:02
        * TO CLIP NAME:  My Clip
        * TO FILE: /var/tmp/clip.001.exr

        Fade out...
        002 My_Clip V C     00:00:01:12 00:00:01:12 00:00:00:12 00:00:00:12
        002 BL      V D 012 00:00:00:00 00:00:00:12 00:00:00:12 00:00:01:00
        * FROM CLIP NAME:  My Clip
        * FROM FILE: /var/tmp/clip.001.exr
        """

        lines = [
            self.cut_line.to_edl_format(self.edit_number),
            self.dissolve_line.to_edl_format(self.edit_number)
        ]
        lines += self.from_comments if hasattr(self, 'from_comments') else []
        lines += self.to_comments if len(self.to_comments) else []

        return "\n".join(lines)


class EventLine(object):
    def __init__(self, kind, rate, reel='AX'):
        self.reel = reel
        self._kind = 'V' if kind == schema.TrackKind.Video else 'A'
        self._rate = rate

        self.source_in = opentime.RationalTime(0.0, rate=rate)
        self.source_out = opentime.RationalTime(0.0, rate=rate)
        self.record_in = opentime.RationalTime(0.0, rate=rate)
        self.record_out = opentime.RationalTime(0.0, rate=rate)

        self.dissolve_length = opentime.RationalTime(0.0, rate)

    def to_edl_format(self, edit_number):
        ser = {
            'edit': edit_number,
            'reel': self.reel,
            'kind': self._kind,
            'src_in': opentime.to_timecode(self.source_in, self._rate),
            'src_out': opentime.to_timecode(self.source_out, self._rate),
            'rec_in': opentime.to_timecode(self.record_in, self._rate),
            'rec_out': opentime.to_timecode(self.record_out, self._rate),
            'diss': int(
                opentime.to_frames(self.dissolve_length, self._rate)
            ),
        }

        if self.is_dissolve():
            return "{edit:03d}  {reel:8} {kind:5} D {diss:03d}    " \
                "{src_in} {src_out} {rec_in} {rec_out}".format(**ser)
        else:
            return "{edit:03d}  {reel:8} {kind:5} C        " \
                "{src_in} {src_out} {rec_in} {rec_out}".format(**ser)

    def is_dissolve(self):
        return self.dissolve_length.value > 0


def _generate_comment_lines(
    clip,
    style,
    edl_rate,
    reelname_len,
    from_or_to='FROM'
):
    lines = []
    url = None

    if not clip or isinstance(clip, schema.Gap):
        return []

    suffix = ''
    timing_effect = _relevant_timing_effect(clip)
    if timing_effect and timing_effect.effect_name == 'FreezeFrame':
        suffix = ' FF'

    if clip.media_reference:
        if hasattr(clip.media_reference, 'target_url'):
            url = clip.media_reference.target_url

        elif hasattr(clip.media_reference, 'abstract_target_url'):
            url = _get_image_sequence_url(clip)

    else:
        url = clip.name

    if from_or_to not in ['FROM', 'TO']:
        raise exceptions.NotSupportedError(
            "The clip FROM or TO value '{}' is not supported.".format(
                from_or_to
            )
        )

    if timing_effect and isinstance(timing_effect, schema.LinearTimeWarp):
        lines.append(
            'M2   {}\t\t{}\t\t\t{}'.format(
                clip.name,
                timing_effect.time_scalar * edl_rate,
                opentime.to_timecode(
                    clip.trimmed_range().start_time,
                    edl_rate
                )
            )
        )

    if clip.name:
        # Avid Media Composer outputs two spaces before the
        # clip name so we match that.
        lines.append(
            "* {from_or_to} CLIP NAME:  {name}{suffix}".format(
                from_or_to=from_or_to,
                name=clip.name,
                suffix=suffix
            )
        )
    if timing_effect and timing_effect.effect_name == "FreezeFrame":
        lines.append('* * FREEZE FRAME')
    if url and style == 'avid':
        lines.append("* {from_or_to} CLIP: {url}".format(
            from_or_to=from_or_to,
            url=url
        ))
    if url and style == 'nucoda':
        lines.append("* {from_or_to} FILE: {url}".format(
            from_or_to=from_or_to,
            url=url
        ))

    if reelname_len and not clip.metadata.get('cmx_3600', {}).get('reel'):
        lines.append("* OTIO TRUNCATED REEL NAME FROM: {url}".format(
            url=os.path.basename(_flip_windows_slashes(url or clip.name))
        ))

    cdl = clip.metadata.get('cdl')
    if cdl:
        asc_sop = cdl.get('asc_sop')
        asc_sat = cdl.get('asc_sat')
        if asc_sop:
            lines.append(
                "*ASC_SOP ({} {} {}) ({} {} {}) ({} {} {})".format(
                    asc_sop['slope'][0],
                    asc_sop['slope'][1],
                    asc_sop['slope'][2],
                    asc_sop['offset'][0],
                    asc_sop['offset'][1],
                    asc_sop['offset'][2],
                    asc_sop['power'][0],
                    asc_sop['power'][1],
                    asc_sop['power'][2]
                ))
        if asc_sat:
            lines.append("*ASC_SAT {}".format(
                asc_sat
            ))

    # Output any markers on this clip
    for marker in clip.markers:
        timecode = opentime.to_timecode(
            marker.marked_range.start_time,
            edl_rate
        )

        color = marker.color
        meta = marker.metadata.get("cmx_3600")
        if not color and meta and meta.get("color"):
            color = meta.get("color").upper()
        comment = (marker.name or '').upper()
        lines.append("* LOC: {} {:7} {}".format(timecode, color, comment))

    # If we are carrying any unhandled CMX 3600 comments on this clip
    # then output them blindly.
    extra_comments = clip.metadata.get('cmx_3600', {}).get('comments', [])
    for comment in extra_comments:
        lines.append("* {}".format(comment))

    return lines


def _get_image_sequence_url(clip):
    ref = clip.media_reference
    start_frame, end_frame = ref.frame_range_for_time_range(
        clip.trimmed_range()
    )

    frame_range_str = '[{start}-{end}]'.format(
        start=start_frame,
        end=end_frame
    )

    url = clip.media_reference.abstract_target_url(frame_range_str)

    return url


def _flip_windows_slashes(path):
    return re.sub(r'\\', '/', path)


def _reel_from_clip(clip, reelname_len):
    if isinstance(clip, schema.Gap):
        return 'BL'

    elif clip.metadata.get('cmx_3600', {}).get('reel'):
        return clip.metadata.get('cmx_3600').get('reel')

    _reel = clip.name or 'AX'

    valid_refs = (schema.ExternalReference, schema.ImageSequenceReference)
    if isinstance(clip.media_reference, valid_refs):
        if clip.media_reference.name:
            _reel = clip.media_reference.name

        elif hasattr(clip.media_reference, 'target_url'):
            _reel = os.path.basename(
                clip.media_reference.target_url
            )

        else:
            _reel = _get_image_sequence_url(clip)

    # Flip Windows slashes
    _reel = os.path.basename(_flip_windows_slashes(_reel))

    # Strip extension
    reel = re.sub(r'([.][a-zA-Z]+)$', '', _reel)

    if reelname_len:
        # Remove non valid characters
        reel = re.sub(r'[^ a-zA-Z0-9]+', '', reel)

        if len(reel) > reelname_len:
            reel = reel[:reelname_len]

        elif len(reel) < reelname_len:
            reel += ' ' * (reelname_len - len(reel))

    return reel
