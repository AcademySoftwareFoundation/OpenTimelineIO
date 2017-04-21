# OpenTimelineIO CMX 3600 EDL Adapter
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

import opentimelineio as otio

# these are all CMX_3600 transition codes
# the wipe is written in regex format because it is W### where the ### is
# a 'wipe code'
transition_regex_map = {
    'C': 'cut',
    'D': 'dissolve',
    'W\d{3}': 'wipe',
    'KB': 'key_background',
    'K': 'key_foreground',
    'KO': 'key_overlay'
}

# these are the channel assignments I could find. CMX_3600 is supposed to
# accommodate up to 4 audio tracks i could not find codes for using A3 and A4
channel_map = {'A': ['A1'],
               'A2': ['A2'],
               'AA': ['A1', 'A2'],
               'V': ['V'],
               'B': ['V', 'A1'],
               'A2/V': ['V', 'A2'],
               'AA/V': ['V', 'A1', 'A2']}


class EdlParser(object):

    def __init__(self, edl_string):
        self.timeline = otio.schema.Timeline()
        # V, A1, A2, A3, and A4 are named specifically
        # they can be easily called using the channel_map above
        self.V = otio.schema.Sequence()
        self.V.kind = "Video"
        self.A1 = otio.schema.Sequence()
        self.A1.kind = "Audio"
        self.A2 = otio.schema.Sequence()
        self.A2.kind = "Audio"

        self._parse_edl(edl_string)

        self.timeline.tracks.append(self.V)
        if self.A1:
            self.timeline.tracks.append(self.A1)
        if self.A2:
            self.timeline.tracks.append(self.A2)

    def _add_clip(self, line, comments):
        comment_handler = CommentHandler(comments)
        clip_handler = ClipHandler(line, comment_handler.handled)
        if comment_handler.unhandled:
            clip_handler.clip.metadata.setdefault("cmx_3600", {})
            clip_handler.clip.metadata['cmx_3600'].setdefault("comments", [])
            clip_handler.clip.metadata['cmx_3600'][
                'comments'] += comment_handler.unhandled
        # each edit point between two clips is a transition. the default is a
        # cut in the edl format the transition codes are for the transition
        # into the clip
        self._add_transition(
            clip_handler,
            clip_handler.transition_type,
            clip_handler.transition_data
        )

        try:
            for channel in channel_map[clip_handler.channel_code]:
                getattr(self, channel).append(clip_handler.clip)
        except KeyError as e:
            raise RuntimeError('unknown channel code {0}'.format(e))

    def _add_transition(self, clip_handler, transition, data):
        if transition not in ['C']:
            md = clip_handler.clip.metadata.setdefault("cmx_3600", {})
            md["transition"] = transition

    def _parse_edl(self, edl_string):
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

            elif line.startswith('TITLE:'):
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
                    raise RuntimeError(
                        'both audio and video delay declared after SPLIT.')
                if not (audio_delay or video_delay):
                    raise RuntimeError(
                        'either audio or video delay declared after SPLIT.')

                line_1 = edl_lines.pop(0)
                line_2 = edl_lines.pop(0)

                comments = []
                while edl_lines:
                    if re.match('^\D', edl_lines[0]):
                        comments.append(edl_lines.pop(0))
                    else:
                        break
                self._add_clip(line_1, comments)
                self._add_clip(line_2, comments)

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

                self._add_clip(line, comments)

            else:
                raise RuntimeError('Unknown event type')


class ClipHandler(object):

    def __init__(self, line, comment_data):
        self._edit_num = None
        self.reel = None
        self.channel_code = None
        self.edl_rate = 24
        self.transition_id = None
        self.transition_data = None
        self._source_tc_in = None
        self._source_tc_out = None
        self._record_tc_in = None
        self._record_tc_out = None

        self._parse(line)
        self.clip = self._make_clip(comment_data)

    def _make_clip(self, comment_data):
        if self.reel == 'BL':
            # TODO make this an explicit path
            # this is the only special tape name code we care about
            # AX exists but means nothing in our context. We aren't using tapes
            clip = otio.schema.Filler()
        else:
            clip = otio.schema.Clip()

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
                    comment_data["locator"])
                if m:
                    marker = otio.schema.Marker()
                    marker.marked_range = otio.opentime.TimeRange(
                        start_time=otio.opentime.from_timecode(
                            m.group(1),
                            self.edl_rate
                        ),
                        duration=otio.opentime.RationalTime()
                    )
                    # TODO: Should we elevate color to a property of Marker?
                    # It seems likely that it will be present in many formats..
                    marker.metadata = {"cmx_3600": {"color": m.group(2)}}
                    marker.name = m.group(3)
                    clip.markers.append(marker)
                else:
                    # TODO: Should we report this as a warning somehow?
                    pass

        clip.source_range = otio.opentime.range_from_start_end_time(
            otio.opentime.from_timecode(self._source_tc_in, self.edl_rate),
            otio.opentime.from_timecode(self._source_tc_out, self.edl_rate)
        )

        return clip

    def _parse(self, line):
        fields = tuple(e.strip() for e in line.split() if e.strip())
        field_count = len(fields)

        if field_count == 9:
            # has transition data
            # this is for edits with timing or other needed info
            # transition data for D and W*** transitions is a n integer that
            # denotes frame count
            # i haven't figured out how the key transitions (K, KB, KO) work
            (self.clip_num,
             self._reel,
             self.channel_code,
             self.transition_type,
             self.transition_data,
             self._source_tc_in,
             self._source_tc_out,
             self._record_tc_in,
             self._record_tc_out) = fields

        elif field_count == 8:
            # no transition data
            # this is for basic cuts
            (self.clip_num,
             self._reel,
             self.channel_code,
             self.transition_type,
             self._source_tc_in,
             self._source_tc_out,
             self._record_tc_in,
             self._record_tc_out) = fields

        else:
            raise RuntimeError(
                'incorrect number of fields [{0}] in form statement: {1}'
                ''.format(field_count, line))


class CommentHandler(object):
    # this is the for that all comment 'id' tags take
    _regex_template = '\*?\s*{id}:'
    # this should be a map of all known comments that we can read
    # 'FROM CLIP' is a required comment to link media
    comment_id_map = {
        'FROM CLIP': 'media_reference',
        'FROM CLIP NAME': 'clip_name',
        'LOC': 'locator'
    }

    def __init__(self, comments):
        self.handled = {}
        self.unhandled = []
        for comment in comments:
            self._parse(comment)

    def _parse(self, comment):
        for comment_id, comment_type in self.comment_id_map.items():
            regex = self._regex_template.format(id=comment_id)
            if re.match(regex, comment):
                self.handled[comment_type] = comment.split(':', 1)[1].strip()
                break
        else:
            stripped = comment.lstrip('*').strip()
            if stripped:
                self.unhandled.append(stripped)


def _expand_transitions(timeline):
    """ Convert clips with metadata/transition == 'D' into OTIO transitions.
    """

    tracks = timeline.tracks
    remove_list = []
    replace_list = []
    for track in tracks:
        track_iter = iter(track)
        # avid inserts an extra clip for the source
        prev_prev = None
        prev = None
        clip = next(track_iter, None)
        next_clip = next(track_iter, None)
        while clip is not None:
            transition_type = clip.metadata.get('cmx_3600',{}).get('transition', 'C')
            if transition_type == 'C':
                # nothing to do, continue to the next iteration of the loop
                prev_prev = prev
                prev = clip
                clip = next_clip
                next_clip = next(track_iter, None)
                continue
            if transition_type not in ['D']:
                raise RuntimeError(
                    "Transition type '{}' not supported by the CMX EDL reader "
                    "currently.".format(transition_type)
                )

            transition_duration = clip.duration()

            # EDL doesn't have enough data to know where the cut point was, so
            # this arbitrarily puts it in the middle of the transition
            transition_duration.value = math.floor(transition_duration.value/2)

            # expand the previous
            expansion_clip = None
            if prev and not prev_prev:
                expansion_clip = prev
            elif prev_prev:
                expansion_clip = prev_prev
                if prev:
                    remove_list.append((track, prev))

            expansion_clip.source_range.duration += transition_duration

            # rebuild the clip as a transition
            new_trx = otio.schema.Transition(
                name=clip.name,
                # only supported type at the moment
                transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
                metadata=clip.metadata
            )
            new_trx.in_offset = transition_duration
            new_trx.out_offset = transition_duration


            #                   in     from  to
            replace_list.append((track, clip, new_trx))

            # expand the next_clip
            if next_clip:
                next_clip.source_range.start_time -= transition_duration
                next_clip.source_range.duration += transition_duration

            prev = clip
            clip = next_clip
            next_clip = next(track_iter, None)

    for (track, from_clip, to_transition) in replace_list:
        track[track.index(from_clip)] = to_transition
    
    for (track, clip_to_remove) in remove_list:
        track.pop(track.index(clip_to_remove))

    return timeline

def read_from_string(input_str):
    parser = EdlParser(input_str)
    result = parser.timeline
    result = _expand_transitions(result)
    return result


def write_to_string(input_otio):
    # TODO: We should have convenience functions in Timeline for this?
    # also only works for a single video track at the moment
    video_tracks = list(filter(lambda t: t.kind == "Video", input_otio.tracks))
    audio_tracks = list(filter(lambda t: t.kind == "Audio", input_otio.tracks))

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
    edl_rate = 24
    lines.append("")

    edit_number = 1

    track = input_otio.tracks[0]
    for i, clip in enumerate(track):
        source_tc_in = otio.opentime.to_timecode(
            clip.source_range.start_time,
            edl_rate
        )
        source_tc_out = otio.opentime.to_timecode(
            clip.source_range.end_time_exclusive(),
            edl_rate
        )

        range_in_track = track.range_of_child_at_index(i)
        record_tc_in = otio.opentime.to_timecode(
            range_in_track.start_time,
            edl_rate
        )
        record_tc_out = otio.opentime.to_timecode(
            range_in_track.end_time_exclusive(),
            edl_rate
        )

        reel = "AX"
        name = None
        url = None

        if clip.media_reference:
            if isinstance(clip.media_reference, otio.schema.Filler):
                reel = "BL"
            elif hasattr(clip.media_reference, 'target_url'):
                url = clip.media_reference.target_url
        else:
            url = clip.name

        name = clip.name

        kind = "V" if track.kind == "Video" else "A"

        lines.append(
            "{:03d}  {:8} {:5} C        {} {} {} {}".format(
                edit_number,
                reel,
                kind,
                source_tc_in,
                source_tc_out,
                record_tc_in,
                record_tc_out))

        if name:
            # Avid Media Composer outputs two spaces before the
            # clip name so we match that.
            lines.append("* FROM CLIP NAME:  {}".format(name))
        if url:
            lines.append("* FROM CLIP: {}".format(url))

        # Output any markers on this clip
        for marker in clip.markers:
            timecode = otio.opentime.to_timecode(
                marker.marked_range.start_time,
                edl_rate
            )
  
            color = ""
            meta = marker.metadata.get("cmx_3600")
            if meta and meta.get("color"):
                color = meta.get("color").upper()
            comment = marker.name.upper()
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
