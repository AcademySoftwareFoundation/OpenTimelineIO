#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

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
import math
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
    r"(?P<name>.*?)\s*(?P<speed>[0-9\.]*)\s*(?P<tc>[0-9:]{11})$"
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

    def add_clip(self, line, comments, rate=24):
        comment_handler = CommentHandler(comments)
        clip_handler = ClipHandler(line, comment_handler.handled, rate=rate)
        clip = clip_handler.clip
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

        # each edit point between two clips is a transition. the default is a
        # cut in the edl format the transition codes are for the transition
        # into the clip
        self.add_transition(
            clip_handler,
            clip_handler.transition_type,
            clip_handler.transition_data
        )

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
            if len(tracks) > 1:
                track_clip = copy.deepcopy(clip)
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

    def add_transition(self, clip_handler, transition, data):
        if transition not in ['C']:
            md = clip_handler.clip.metadata.setdefault("cmx_3600", {})
            md["transition"] = transition

    def parse_edl(self, edl_string, rate=24):
        # edl 'events' can be comprised of an indeterminate amount of lines
        # we are to translating 'events' to a single clip and transition
        # then we add the transition and the clip to all channels the 'event'
        # channel code is mapped to the transition given in the 'event'
        # precedes the clip

        # remove all blank lines from the edl
        edl_lines = [
            l for l in (l.strip() for l in edl_string.splitlines()) if l
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

                comments = []
                while edl_lines:
                    if re.match(r'^\D', edl_lines[0]):
                        comments.append(edl_lines.pop(0))
                    else:
                        break
                self.add_clip(line_1, comments, rate=rate)
                self.add_clip(line_2, comments, rate=rate)

            elif line[0].isdigit():
                # all 'events' start_time with an edit decision. this is
                # denoted by the line beginning with a padded integer 000-999
                comments = []
                while edl_lines:
                    # any non-numbered lines after an edit decision should be
                    # treated as 'comments'
                    # comments are string tags used by the reader to get extra
                    # information not able to be found in the restricted edl
                    # format
                    if re.match(r'^\D', edl_lines[0]):
                        comments.append(edl_lines.pop(0))
                    else:
                        break

                self.add_clip(line, comments, rate=rate)

            else:
                raise EDLParseError('Unknown event type')

        for track in self.timeline.tracks:
            # if the source_range is the same as the available_range
            # then we don't need to set it at all.
            if track.source_range == track.available_range():
                track.source_range = None


class ClipHandler(object):

    def __init__(self, line, comment_data, rate=24):
        self.clip_num = None
        self.reel = None
        self.channel_code = None
        self.edl_rate = rate
        self.transition_id = None
        self.transition_data = None
        self.source_tc_in = None
        self.source_tc_out = None
        self.record_tc_in = None
        self.record_tc_out = None

        self.parse(line)
        self.clip = self.make_clip(comment_data)

    def make_clip(self, comment_data):
        clip = schema.Clip()
        clip.name = str(self.clip_num)

        # BLACK/BL and BARS are called out as "Special Source Identifiers" in
        # the documents referenced here:
        # https://github.com/PixarAnimationStudios/OpenTimelineIO#cmx3600-edl
        if self.reel in ['BL', 'BLACK']:
            clip.media_reference = schema.GeneratorReference()
            # TODO: Replace with enum, once one exists
            clip.media_reference.generator_kind = 'black'
        elif self.reel == 'BARS':
            clip.media_reference = schema.GeneratorReference()
            # TODO: Replace with enum, once one exists
            clip.media_reference.generator_kind = 'SMPTEBars'
        elif 'media_reference' in comment_data:
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

        asc_sop = comment_data.get('asc_sop', None)
        asc_sat = comment_data.get('asc_sat', None)
        if asc_sop or asc_sat:
            slope = (1, 1, 1)
            offset = (0, 0, 0)
            power = (1, 1, 1)
            sat = 1.0

            if asc_sop:
                triple = r'([-+]?[\d.]+) ([-+]?[\d.]+) ([-+]?[\d.]+)'
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
                self.clip_num,
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
            # no transition data
            # this is for basic cuts
            (
                self.clip_num,
                self.reel,
                self.channel_code,
                self.transition_type,
                self.source_tc_in,
                self.source_tc_out,
                self.record_tc_in,
                self.record_tc_out
            ) = fields

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


class CommentHandler(object):
    # this is the for that all comment 'id' tags take
    regex_template = r'\*?\s*{id}:?\s*(?P<comment_body>.*)'

    # this should be a map of all known comments that we can read
    # 'FROM CLIP' or 'FROM FILE' is a required comment to link media
    # An exception is raised if both 'FROM CLIP' and 'FROM FILE' are found
    # needs to be ordered so that FROM CLIP NAME gets matched before FROM CLIP
    comment_id_map = collections.OrderedDict([
        ('FROM CLIP NAME', 'clip_name'),
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


def _expand_transitions(timeline):
    """Convert clips with metadata/transition == 'D' into OTIO transitions."""

    tracks = timeline.tracks
    remove_list = []
    replace_list = []
    append_list = []
    for track in tracks:
        track_iter = iter(track)
        # avid inserts an extra clip for the source
        prev_prev = None
        prev = None
        clip = next(track_iter, None)
        next_clip = next(track_iter, None)
        while clip is not None:
            transition_type = clip.metadata.get('cmx_3600', {}).get(
                'transition',
                'C'
            )

            if transition_type == 'C':
                # nothing to do, continue to the next iteration of the loop
                prev_prev = prev
                prev = clip
                clip = next_clip
                next_clip = next(track_iter, None)
                continue
            if transition_type not in ['D']:
                raise EDLParseError(
                    "Transition type '{}' not supported by the CMX EDL reader "
                    "currently.".format(transition_type)
                )

            transition_duration = clip.duration()

            # EDL doesn't have enough data to know where the cut point was, so
            # this arbitrarily puts it in the middle of the transition
            pre_cut = math.floor(transition_duration.value / 2)
            post_cut = transition_duration.value - pre_cut
            mid_tran_cut_pre_duration = opentime.RationalTime(
                pre_cut,
                transition_duration.rate
            )
            mid_tran_cut_post_duration = opentime.RationalTime(
                post_cut,
                transition_duration.rate
            )

            # expand the previous
            expansion_clip = None
            if prev and not prev_prev:
                expansion_clip = prev
            elif prev_prev:
                expansion_clip = prev_prev
                if prev:
                    remove_list.append((track, prev))

            _extend_source_range_duration(expansion_clip, mid_tran_cut_pre_duration)

            # rebuild the clip as a transition
            new_trx = schema.Transition(
                name=clip.name,
                # only supported type at the moment
                transition_type=schema.TransitionTypes.SMPTE_Dissolve,
                metadata=clip.metadata
            )
            new_trx.in_offset = mid_tran_cut_pre_duration
            new_trx.out_offset = mid_tran_cut_post_duration

            #                   in     from  to
            replace_list.append((track, clip, new_trx))

            # expand the next_clip
            if next_clip:
                sr = next_clip.source_range
                next_clip.source_range = opentime.TimeRange(
                    sr.start_time - mid_tran_cut_post_duration,
                    sr.duration + mid_tran_cut_post_duration
                )
            else:
                fill = schema.Gap(
                    source_range=opentime.TimeRange(
                        duration=mid_tran_cut_post_duration,
                        start_time=opentime.RationalTime(
                            0,
                            transition_duration.rate
                        )
                    )
                )
                append_list.append((track, fill))

            prev = clip
            clip = next_clip
            next_clip = next(track_iter, None)

    for (track, from_clip, to_transition) in replace_list:
        track[track.index(from_clip)] = to_transition

    for (track, clip_to_remove) in list(set(remove_list)):
        # if clip_to_remove in track:
        track.remove(clip_to_remove)

    for (track, clip) in append_list:
        track.append(clip)

    return timeline


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
    result = _expand_transitions(result)
    return result


def write_to_string(input_otio, rate=None, style='avid', reelname_len=8):
    # TODO: We should have convenience functions in Timeline for this?
    # also only works for a single video track at the moment

    video_tracks = [t for t in input_otio.tracks
                    if t.kind == schema.TrackKind.Video]
    audio_tracks = [t for t in input_otio.tracks
                    if t.kind == schema.TrackKind.Audio]

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
            elif isinstance(child, schema.Gap):
                # Gaps are represented as missing record timecode, no event
                # needed.
                pass

        content = "TITLE: {}\n\n".format(title) if title else ''

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


def _flip_windows_slashes(path):
    return re.sub(r'\\', '/', path)


def _reel_from_clip(clip, reelname_len):
    if isinstance(clip, schema.Gap):
        return 'BL'

    elif clip.metadata.get('cmx_3600', {}).get('reel'):
        return clip.metadata.get('cmx_3600').get('reel')

    _reel = clip.name or 'AX'

    if isinstance(clip.media_reference, schema.ExternalReference):
        _reel = clip.media_reference.name or os.path.basename(
            clip.media_reference.target_url
        )

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
