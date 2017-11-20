#
# Copyright 2017 Pixar Animation Studios
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
# https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki/How-to-Write-an-OpenTimelineIO-Adapter

# TODO: Flesh out Attribute Handler
# TODO: Add line numbers to errors and warnings
# TODO: currently tracks with linked audio/video will lose their linkage when
#       read into OTIO.

import os
import re
import math
import collections

import opentimelineio as otio


class EDLParseError(otio.exceptions.OTIOError):
    pass


# these are all CMX_3600 transition codes
# the wipe is written in regex format because it is W### where the ### is
# a 'wipe code'
# @TODO: not currently read by the transition code
transition_regex_map = {
    'C': 'cut',
    'D': 'dissolve',
    'W\d{3}': 'wipe',
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


class EDLParser(object):
    def __init__(self, edl_string, rate=24):
        self.timeline = otio.schema.Timeline()

        # Start with no tracks. They will be added as we encounter them.
        # This dict maps a track name (e.g "A2" or "V") to an OTIO Track.
        self.tracks_by_name = {}

        self.parse_edl(edl_string, rate=rate)

        # TODO: Sort the tracks V, then A1,A2,etc.

    def add_clip(self, line, comments, rate=24):
        comment_handler = CommentHandler(comments)
        clip_handler = ClipHandler(line, comment_handler.handled, rate=rate)
        if comment_handler.unhandled:
            clip_handler.clip.metadata.setdefault("cmx_3600", {})
            clip_handler.clip.metadata['cmx_3600'].setdefault("comments", [])
            clip_handler.clip.metadata['cmx_3600']['comments'] += (
                comment_handler.unhandled
            )

        # each edit point between two clips is a transition. the default is a
        # cut in the edl format the transition codes are for the transition
        # into the clip
        self.add_transition(
            clip_handler,
            clip_handler.transition_type,
            clip_handler.transition_data
        )

        tracks = self.tracks_for_channel(clip_handler.channel_code)
        for track in tracks:
            track.append(clip_handler.clip)

    def guess_kind_for_track_name(self, name):
        if name.startswith("V"):
            return otio.schema.TrackKind.Video
        if name.startswith("A"):
            return otio.schema.TrackKind.Audio
        return otio.schema.TrackKind.Video

    def tracks_for_channel(self, channel_code):
        # Expand channel shorthand into a list of track names.
        if channel_code in channel_map:
            track_names = channel_map[channel_code]
        else:
            track_names = [channel_code]

        # Create any channels we don't already have
        for track_name in track_names:
            if track_name not in self.tracks_by_name:
                track = otio.schema.Track(
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

        edl_lines = edl_string.splitlines()
        while edl_lines:
            # a basic for loop wont work cleanly since we need to look ahead at
            # array elements to determine what type of 'event' we are looking
            # at
            line = edl_lines.pop(0)
            line = line.strip()

            if not line:
                continue

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
                    if re.match('^\D', edl_lines[0]):
                        comments.append(edl_lines.pop(0))
                    else:
                        break
                self.add_clip(line_1, comments)
                self.add_clip(line_2, comments)

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
                    if re.match('^\D', edl_lines[0]):
                        comments.append(edl_lines.pop(0))
                    else:
                        break

                self.add_clip(line, comments, rate=rate)

            else:
                raise EDLParseError('Unknown event type')


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
        if self.reel == 'BL':
            # TODO make this an explicit path
            # this is the only special tape name code we care about
            # AX exists but means nothing in our context. We aren't using tapes
            clip = otio.schema.Gap()
        else:
            clip = otio.schema.Clip()
            clip.name = str(self.clip_num)

            if 'media_reference' in comment_data:
                clip.media_reference = otio.media_reference.External()
                clip.media_reference.target_url = comment_data[
                    'media_reference'
                ]
            else:
                clip.media_reference = otio.media_reference.MissingReference()

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
                        r'\('+triple+'\)\s*\('+triple+'\)\s*\('+triple+'\)',
                        asc_sop
                    )
                    if m:
                        floats = [float(g) for g in m.groups()]
                        slope = [floats[0], floats[1], floats[2]]
                        offset = [floats[3], floats[4], floats[5]]
                        power = [floats[6], floats[7], floats[8]]
                    else:
                        raise EDLParseError(
                            'Invalid ASC_SOP found: {}'.format(asc_sop)
                            )

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

            if 'locator' in comment_data:
                # An example EDL locator line looks like this:
                # * LOC: 01:00:01:14 RED     ANIM FIX NEEDED
                # We get the part after "LOC: " as the comment_data entry
                # Given the fixed-width nature of these, we could be more
                # strict about the field widths, but there are many
                # variations of EDL, so if we are lenient then maybe we
                # can handle more of them? Only real-world testing will
                # determine this for sure...
                m = re.match(
                    r'(\d\d:\d\d:\d\d:\d\d)\s+(\w*)\s+(.*)',
                    comment_data["locator"]
                )
                if m:
                    marker = otio.schema.Marker()
                    marker.marked_range = otio.opentime.TimeRange(
                        start_time=otio.opentime.from_timecode(
                            m.group(1),
                            self.edl_rate
                        ),
                        duration=otio.opentime.RationalTime()
                    )

                    # always write the source value into metadata, in case it
                    # is not a valid enum somehow.
                    color_parsed_from_file = m.group(2)

                    marker.metadata = {
                        "cmx_3600": {
                            "color": color_parsed_from_file
                        }
                    }

                    # @TODO: if it is a valid
                    if hasattr(
                        otio.schema.MarkerColor,
                        color_parsed_from_file.upper()
                    ):
                        marker.color = color_parsed_from_file.upper()
                    else:
                        marker.color = otio.schema.MarkerColor.RED

                    marker.name = m.group(3)
                    clip.markers.append(marker)
                else:
                    # TODO: Should we report this as a warning somehow?
                    pass

        clip.source_range = otio.opentime.range_from_start_end_time(
            otio.opentime.from_timecode(self.source_tc_in, self.edl_rate),
            otio.opentime.from_timecode(self.source_tc_out, self.edl_rate)
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


class CommentHandler(object):
    # this is the for that all comment 'id' tags take
    regex_template = '\*\s*{id}:?\s+(?P<comment_body>.*)'

    # this should be a map of all known comments that we can read
    # 'FROM CLIP' is a required comment to link media
    # needs to be ordered so that FROM CLIP NAME gets matched before FROM CLIP
    comment_id_map = collections.OrderedDict([
            ('FROM CLIP NAME', 'clip_name'),
            ('FROM CLIP', 'media_reference'),
            ('LOC', 'locator'),
            ('ASC_SOP', 'asc_sop'),
            ('ASC_SAT', 'asc_sat'),
        ]
    )

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
                self.handled[comment_type] = match.group(
                    'comment_body'
                ).strip()
                break
        else:
            stripped = comment.lstrip('*').strip()
            if stripped:
                self.unhandled.append(stripped)


def expand_transitions(timeline):
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
            mid_tran_cut_pre_duration = otio.opentime.RationalTime(
                pre_cut,
                transition_duration.rate
            )
            mid_tran_cut_post_duration = otio.opentime.RationalTime(
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

            expansion_clip.source_range.duration += mid_tran_cut_pre_duration

            # rebuild the clip as a transition
            new_trx = otio.schema.Transition(
                name=clip.name,
                # only supported type at the moment
                transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
                metadata=clip.metadata
            )
            new_trx.in_offset = mid_tran_cut_pre_duration
            new_trx.out_offset = mid_tran_cut_post_duration

            #                   in     from  to
            replace_list.append((track, clip, new_trx))

            # expand the next_clip
            if next_clip:
                next_clip.source_range.start_time -= mid_tran_cut_post_duration
                next_clip.source_range.duration += mid_tran_cut_post_duration
            else:
                fill = otio.schema.Gap(
                    source_range=otio.opentime.TimeRange(
                        duration=mid_tran_cut_post_duration,
                        start_time=otio.opentime.RationalTime(
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


def read_from_string(input_str, rate=24):
    parser = EDLParser(input_str, rate=rate)
    result = parser.timeline
    result = expand_transitions(result)
    return result


def write_to_string(input_otio):
    # TODO: We should have convenience functions in Timeline for this?
    # also only works for a single video track at the moment
    video_tracks = [t for t in input_otio.tracks
                    if t.kind == otio.schema.TrackKind.Video]
    audio_tracks = [t for t in input_otio.tracks
                    if t.kind == otio.schema.TrackKind.Audio]

    if len(video_tracks) != 1:
        raise otio.exceptions.NotSupportedError(
            "Only a single video track is supported, got: {}".format(
                len(video_tracks)
            )
        )

    if len(audio_tracks) > 2:
        raise otio.exceptions.NotSupportedError(
            "No more than 2 audio tracks are supported."
        )
    # if audio_tracks:
    #     raise otio.exceptions.NotSupportedError(
    #         "No audio tracks are currently supported."
    #     )

    lines = []

    lines.append("TITLE: {}".format(input_otio.name))
    # TODO: We should try to detect the frame rate and output an
    # appropriate "FCM: NON-DROP FRAME" etc here.
    lines.append("")

    edit_number = 1

    track = input_otio.tracks[0]
    for i, clip in enumerate(track):
        source_tc_in = otio.opentime.to_timecode(
            clip.source_range.start_time,
            clip.source_range.start_time.rate
        )
        source_tc_out = otio.opentime.to_timecode(
            clip.source_range.end_time_exclusive(),
            clip.source_range.end_time_exclusive().rate
        )

        range_in_track = track.range_of_child_at_index(i)
        record_tc_in = otio.opentime.to_timecode(
            range_in_track.start_time,
            range_in_track.start_time.rate
        )
        record_tc_out = otio.opentime.to_timecode(
            range_in_track.end_time_exclusive(),
            range_in_track.end_time_exclusive().rate
        )

        reel = "AX"
        name = None
        url = None

        if clip.media_reference:
            if isinstance(clip.media_reference, otio.schema.Gap):
                reel = "BL"
            elif hasattr(clip.media_reference, 'target_url'):
                url = clip.media_reference.target_url
        else:
            url = clip.name

        name = clip.name

        kind = "V" if track.kind == otio.schema.TrackKind.Video else "A"

        lines.append(
            "{:03d}  {:8} {:5} C        {} {} {} {}".format(
                edit_number,
                reel,
                kind,
                source_tc_in,
                source_tc_out,
                record_tc_in,
                record_tc_out
            )
        )

        if name:
            # Avid Media Composer outputs two spaces before the
            # clip name so we match that.
            lines.append("* FROM CLIP NAME:  {}".format(name))
        if url:
            lines.append("* FROM CLIP: {}".format(url))

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
            timecode = otio.opentime.to_timecode(
                marker.marked_range.start_time,
                marker.marked_range.start_time.rate
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

        lines.append("")
        edit_number += 1

    text = "\n".join(lines)
    return text
