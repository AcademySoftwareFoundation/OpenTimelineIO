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

__doc__ = """OpenTimelineIO Final Cut Pro 7 XML Adapter."""

import os
import math
import functools
import collections
from xml.etree import cElementTree
from xml.dom import minidom

# deal with renaming of default library from python 2 / 3
try:
    import urlparse as urllib_parse
except ImportError:
    import urllib.parse as urllib_parse

import opentimelineio as otio

META_NAMESPACE = 'fcp_xml'  # namespace to use for metadata


# ---------
# utilities
# ---------

def _url_to_path(url):
    parsed = urllib_parse.urlparse(url)
    return parsed.path


def _populate_element_map(elem, element_map):
    if 'id' in elem.attrib and list(elem):
        element_map[elem.tag].setdefault(elem.attrib['id'], elem)
    for sub_elem in elem:
        _populate_element_map(sub_elem, element_map)


def _resolved_backreference(elem, tag, element_map):
    if 'id' in elem.attrib:
        elem = element_map[tag].setdefault(elem.attrib['id'], elem)

    return elem


def _populate_backreference_map(item, br_map):
    if isinstance(item, otio.media_reference.MediaReference):
        tag = 'file'
    elif isinstance(item, otio.schema.Sequence):
        tag = 'sequence'
    else:
        tag = None

    if isinstance(item, otio.media_reference.External):
        item_hash = hash(str(item.target_url))
    elif isinstance(item, otio.media_reference.MissingReference):
        item_hash = 'missing_ref'
    else:
        item_hash = item.__hash__()

    # skip unspecified tags
    if tag is not None:
        br_map[tag].setdefault(item_hash,
                               1 if not br_map[tag] else
                               max(br_map[tag].values()) + 1)

    # populate children
    if isinstance(item, otio.schema.Timeline):
        for sub_item in item.tracks:
            _populate_backreference_map(sub_item, br_map)
    elif isinstance(item, (otio.schema.Clip,
                           otio.schema.Gap,
                           otio.schema.Transition)):
        pass
    else:
        for sub_item in item:
            _populate_backreference_map(sub_item, br_map)


def _backreference_build(tag):
    # We can also encode these back-references if an item is accessed multiple
    # times. To do this we store an id attribute on the element. For back-
    # references we then only need to return an empty element of that type with
    # the id we logged before

    def singleton_decorator(func):
        @functools.wraps(func)
        def wrapper(item, *args, **kwargs):
            br_map = args[-1]
            if isinstance(item, otio.media_reference.External):
                item_hash = hash(str(item.target_url))
            elif isinstance(item, otio.media_reference.MissingReference):
                item_hash = 'missing_ref'
            else:
                item_hash = item.__hash__()
            item_id = br_map[tag].get(item_hash, None)
            if item_id is not None:
                return cElementTree.Element(tag,
                                            id='{}-{}'.format(tag, item_id))
            item_id = br_map[tag].setdefault(item_hash,
                                             1 if not br_map[tag] else
                                             max(br_map[tag].values()) + 1)
            elem = func(item, *args, **kwargs)
            elem.attrib['id'] = '{}-{}'.format(tag, item_id)
            return elem

        return wrapper

    return singleton_decorator


def _insert_new_sub_element(into_parent, tag, attrib=None, text=''):
    elem = cElementTree.SubElement(into_parent, tag, **attrib or {})
    elem.text = text
    return elem


def _get_top_level_sequences(elem):
    top_level_sequences = elem.findall('./sequence')
    for sub_elem in elem:
        if sub_elem.tag in ('sequence', 'clip'):
            continue
        top_level_sequences.extend(_get_top_level_sequences(sub_elem))
    return top_level_sequences


def _make_pretty_string(tree_e):
    # most of the parsing in this adapter is done with cElementTree because it
    # is simpler and faster. However, the string representation it returns is
    # far from elegant. Therefor we feed it through minidom to provide an xml
    # with indentations.
    string = cElementTree.tostring(tree_e, encoding="UTF-8", method="xml")
    dom = minidom.parseString(string)
    return dom.toprettyxml(indent='    ')


def _is_primary_audio_channel(track):
    # audio may be structured in stereo where each channel occupies a separate
    # track. Some xml logic combines these into a single track upon import.
    # Here we check whether we`re dealing with the first audio channel
    return (
        track.attrib.get('currentExplodedTrackIndex', '0') == '0'
        or track.attrib.get('totalExplodedTrackCount', '1') == '1'
    )


def _get_transition_cut_point(transition_item):
    alignment = transition_item.find('./alignment').text
    start = int(transition_item.find('./start').text)
    end = int(transition_item.find('./end').text)

    if alignment in ('end', 'end-black'):
        return end
    elif alignment in ('start', 'start-black'):
        return start
    elif alignment in ('center',):
        return int((start + end) / 2)
    else:
        return int((start + end) / 2)


# -----------------------
# parsing single sequence
# -----------------------

def _parse_rate(elem, element_map):
    elem = _resolved_backreference(elem, 'all_elements', element_map)

    rate = elem.find('./rate')
    # rate is encoded as a timebase (int) which can be drop-frame
    base = float(rate.find('./timebase').text)
    if rate.find('./ntsc').text == 'TRUE':
        base *= .999
    return base


def _parse_media_reference(file_e, element_map):
    file_e = _resolved_backreference(file_e, 'file', element_map)

    url = file_e.find('./pathurl').text
    file_rate = _parse_rate(file_e, element_map)
    timecode_rate = _parse_rate(file_e.find('./timecode'), element_map)
    timecode_frame = int(file_e.find('./timecode/frame').text)
    duration_e = file_e.find('./duration')
    duration = int(duration_e.text) if duration_e is not None else 0

    available_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(timecode_frame, timecode_rate),
        duration=otio.opentime.RationalTime(duration, file_rate)
    )

    return otio.media_reference.External(
        target_url=url.strip(),
        available_range=available_range
    )


def _parse_clip_item_without_media(clip_item, sequence_rate,
                                   transition_offsets, element_map):
    markers = clip_item.findall('./marker')
    rate = _parse_rate(clip_item, element_map)

    # transition offsets are provided in timeline rate. If they deviate they
    # need to be rescaled to clip item rate
    context_transition_offsets = [
        transition_offsets[0].rescaled_to(rate),
        transition_offsets[1].rescaled_to(rate)
    ]

    in_frame = int(clip_item.find('./in').text) + \
        int(round(context_transition_offsets[0].value))
    out_frame = int(clip_item.find('./out').text) - \
        int(round(context_transition_offsets[1].value))

    source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(in_frame, sequence_rate),
        duration=otio.opentime.RationalTime(out_frame - in_frame,
                                            sequence_rate)
    )

    name_item = clip_item.find('name')
    if name_item is not None:
        name = name_item.text
    else:
        name = None

    clip = otio.schema.Clip(name=name, source_range=source_range)
    clip.markers.extend(
        [_parse_marker(m, rate) for m in markers])
    return clip


def _parse_clip_item(clip_item, transition_offsets, element_map):
    markers = clip_item.findall('./marker')

    media_reference = _parse_media_reference(
        clip_item.find('./file'),
        element_map
    )
    src_rate = _parse_rate(clip_item.find('./file'), element_map)

    # transition offsets are provided in timeline rate. If they deviate they
    # need to be rescaled to clip item rate
    context_transition_offsets = [
        transition_offsets[0].rescaled_to(src_rate),
        transition_offsets[1].rescaled_to(src_rate)
    ]

    in_frame = int(clip_item.find('./in').text) + \
        int(round(context_transition_offsets[0].value))
    out_frame = int(clip_item.find('./out').text) - \
        int(round(context_transition_offsets[1].value))
    timecode = media_reference.available_range.start_time

    # source_start in xml is taken relative to the start of the media, whereas
    # we want the absolute start time, taking into account the timecode
    source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(in_frame, src_rate) + timecode,
        duration=otio.opentime.RationalTime(out_frame - in_frame, src_rate)
    )

    # get the clip name from the media reference if not defined on the clip
    name_item = clip_item.find('name')
    if name_item is not None:
        name = name_item.text
    else:
        url_path = _url_to_path(media_reference.target_url)
        name = os.path.basename(url_path)

    clip = otio.schema.Clip(name=name,
                            media_reference=media_reference,
                            source_range=source_range)
    clip.markers.extend([_parse_marker(m, src_rate) for m in markers])

    return clip


def _parse_transition_item(transition_item, sequence_rate):
    start = int(transition_item.find('./start').text)
    end = int(transition_item.find('./end').text)
    cut_point = _get_transition_cut_point(transition_item)
    metadata = {META_NAMESPACE: {
        'effectid': transition_item.find('./effect/effectid').text,
    }}

    transition = otio.schema.Transition(
        name=transition_item.find('./effect/name').text,
        transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
        in_offset=otio.opentime.RationalTime(cut_point - start, sequence_rate),
        out_offset=otio.opentime.RationalTime(end - cut_point, sequence_rate),
        metadata=metadata
    )
    return transition


def _parse_sequence_item(sequence_item, transition_offsets, element_map):
    sequence = _parse_sequence(sequence_item.find('./sequence'), element_map)
    source_rate = _parse_rate(sequence_item.find('./sequence'), element_map)

    # transition offsets are provided in timeline rate. If they deviate they
    # need to be rescaled to clip item rate
    context_transition_offsets = [
        transition_offsets[0].rescaled_to(source_rate),
        transition_offsets[1].rescaled_to(source_rate)
    ]

    in_frame = int(sequence_item.find('./in').text) + \
        int(round(context_transition_offsets[0].value, 0))
    out_frame = int(sequence_item.find('./out').text) - \
        int(round(context_transition_offsets[1].value))

    sequence.source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(in_frame, source_rate),
        duration=otio.opentime.RationalTime(out_frame - in_frame, source_rate)
    )
    return sequence


def _parse_item(track_item, sequence_rate, transition_offsets, element_map):
    # depending on the content of the clip-item, we return either a clip, a
    # stack or a transition.
    if track_item.tag == 'transitionitem':
        return _parse_transition_item(track_item, sequence_rate)

    file_e = track_item.find('./file')
    if file_e is not None:
        file_e = _resolved_backreference(file_e, 'file', element_map)

    if file_e is not None:
        if file_e.find('./pathurl') is None:
            return _parse_clip_item_without_media(
                track_item, sequence_rate, transition_offsets, element_map)
        else:
            return _parse_clip_item(
                track_item, transition_offsets, element_map)
    elif track_item.find('./sequence') is not None:
        return _parse_sequence_item(
            track_item, transition_offsets, element_map)

    raise TypeError('Type of clip item is not supported {item_id}'.format(
                    item_id=track_item.attrib['id']))


def _parse_track(track_e, kind, rate, element_map):
    track = otio.schema.Sequence(kind=kind)
    track_items = [item for item in track_e
                   if item.tag in ('clipitem', 'transitionitem')]

    if not track_items:
        return track

    last_clip_end = 0
    for track_item in track_items:
        clip_item_index = list(track_e).index(track_item)
        start = int(track_item.find('./start').text)
        end = int(track_item.find('./end').text)

        # start time and end time on the timeline can be set to -1. This means
        # that there is a transition at that end of the clip-item. So the time
        # on the timeline has to be taken from that object.
        transition_offsets = [otio.opentime.RationalTime(),
                              otio.opentime.RationalTime()]
        if track_item.tag == 'clipitem':
            if start == -1:
                in_transition = list(track_e)[clip_item_index - 1]
                start = _get_transition_cut_point(in_transition)
                transition_offsets[0] = otio.opentime.RationalTime(
                    start - int(in_transition.find('./start').text), rate)
            if end == -1:
                out_transition = list(track_e)[clip_item_index + 1]
                end = _get_transition_cut_point(out_transition)
                transition_offsets[1] = otio.opentime.RationalTime(
                    int(out_transition.find('./end').text) - end, rate)

        # see if we need to add a gap before this clip-item
        gap_time = start - last_clip_end
        last_clip_end = end
        if gap_time > 0:
            gap_range = otio.opentime.TimeRange(
                duration=otio.opentime.RationalTime(gap_time, rate))
            track.append(otio.schema.Gap(source_range=gap_range))

        # finally add the track-item itself
        track.append(_parse_item(track_item, rate,
                                 transition_offsets, element_map))

    return track


def _parse_marker(marker, rate):
    marker_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(
            int(marker.find('./in').text), rate))
    metadata = {META_NAMESPACE: {'comment': marker.find('./comment').text}}
    return otio.schema.Marker(name=marker.find('./name').text,
                              marked_range=marker_range,
                              metadata=metadata)


def _parse_sequence(sequence, element_map):
    sequence = _resolved_backreference(sequence, 'sequence', element_map)

    sequence_rate = _parse_rate(sequence, element_map)

    video_tracks = sequence.findall('./media/video/track')
    audio_tracks = sequence.findall('./media/audio/track')
    markers = sequence.findall('./marker')

    stack = otio.schema.Stack(name=sequence.find('./name').text)

    stack.extend(
        [_parse_track(
            t, otio.schema.SequenceKind.Video, sequence_rate, element_map
         )
         for t in video_tracks])
    stack.extend(
        [_parse_track(
            t, otio.schema.SequenceKind.Audio, sequence_rate, element_map
         )
         for t in audio_tracks
         if _is_primary_audio_channel(t)])
    stack.markers.extend([_parse_marker(m, sequence_rate) for m in markers])

    return stack


def _parse_timeline(sequence, element_map):
    sequence = _resolved_backreference(sequence, 'sequence', element_map)
    sequence_rate = _parse_rate(sequence, element_map)
    timeline = otio.schema.Timeline(name=sequence.find('./name').text)
    timeline.global_start_time = otio.opentime.RationalTime(0, sequence_rate)
    timeline.tracks = _parse_sequence(sequence, element_map)
    return timeline


def _parse_collection(sequences, element_map):
    collection = otio.schema.SerializeableCollection(name='sequences')
    collection.extend([_parse_timeline(s, element_map) for s in sequences])
    return collection


# ------------------------
# building single sequence
# ------------------------

def _build_rate(time):
    rate = math.ceil(time.rate)

    rate_e = cElementTree.Element('rate')
    _insert_new_sub_element(rate_e, 'timebase', text=str(int(rate)))
    _insert_new_sub_element(rate_e, 'ntsc',
                            text='FALSE' if rate == time.rate else 'TRUE')
    return rate_e


def _build_item_timings(item_e, item, timeline_range, transition_offsets,
                        timecode):
    # source_start is absolute time taking into account the timecode of the
    # media. But xml regards the source in point from the start of the media.
    # So we subtract the media timecode.
    source_start = item.source_range.start_time - timecode
    source_end = item.source_range.end_time_exclusive() - timecode
    start = '{:.0f}'.format(timeline_range.start_time.value)
    end = '{:.0f}'.format(timeline_range.end_time_exclusive().value)

    if transition_offsets[0] is not None:
        start = '-1'
        source_start -= transition_offsets[0]
    if transition_offsets[1] is not None:
        end = '-1'
        source_end += transition_offsets[1]

    _insert_new_sub_element(
        item_e, 'duration',
        text='{:.0f}'.format(item.source_range.duration.value)
    )
    _insert_new_sub_element(item_e, 'start',
                            text=start)
    _insert_new_sub_element(item_e, 'end',
                            text=end)
    _insert_new_sub_element(item_e, 'in',
                            text='{:.0f}'.format(source_start.value))
    _insert_new_sub_element(item_e, 'out',
                            text='{:.0f}'.format(source_end.value))


@_backreference_build('file')
def _build_empty_file(media_ref, source_start, br_map):
    file_e = cElementTree.Element('file')
    file_e.append(_build_rate(source_start))
    file_media_e = _insert_new_sub_element(file_e, 'media')
    _insert_new_sub_element(file_media_e, 'video')

    return file_e


@_backreference_build('file')
def _build_file(media_reference, br_map):
    file_e = cElementTree.Element('file')

    available_range = media_reference.available_range
    url_path = _url_to_path(media_reference.target_url)

    _insert_new_sub_element(file_e, 'name', text=os.path.basename(url_path))
    file_e.append(_build_rate(available_range.start_time))
    _insert_new_sub_element(
        file_e, 'duration',
        text='{:.0f}'.format(available_range.duration.value))
    _insert_new_sub_element(file_e, 'pathurl', text=media_reference.target_url)

    # timecode
    timecode = available_range.start_time
    timecode_e = _insert_new_sub_element(file_e, 'timecode')
    timecode_e.append(_build_rate(timecode))
    # TODO: This assumes the rate on the start_time is the framerate
    _insert_new_sub_element(
        timecode_e,
        'string',
        text=otio.opentime.to_timecode(timecode, rate=timecode.rate)
    )
    _insert_new_sub_element(
        timecode_e, 'frame', text='{:.0f}'.format(timecode.value)
    )
    display_format = 'DF' if (math.ceil(timecode.rate) == 30
                              and math.ceil(timecode.rate) != timecode.rate) \
        else 'NDF'
    _insert_new_sub_element(timecode_e, 'displayformat', text=display_format)

    # we need to flag the file reference with the content types, otherwise it
    # will not get recognized
    file_media_e = _insert_new_sub_element(file_e, 'media')
    content_types = []
    if not os.path.splitext(url_path)[1].lower() in ('.wav', '.aac', '.mp3'):
        content_types.append('video')
    content_types.append('audio')

    for kind in content_types:
        _insert_new_sub_element(file_media_e, kind)

    return file_e


def _build_transition_item(transition_item, timeline_range, transition_offsets,
                           br_map):
    transition_e = cElementTree.Element('transitionitem')
    _insert_new_sub_element(
        transition_e, 'start',
        text='{:.0f}'.format(timeline_range.start_time.value)
    )
    _insert_new_sub_element(
        transition_e, 'end',
        text='{:.0f}'.format(timeline_range.end_time_exclusive().value)
    )

    if not transition_item.in_offset.value:
        _insert_new_sub_element(transition_e, 'alignment', text='start-black')
    elif not transition_item.out_offset.value:
        _insert_new_sub_element(transition_e, 'alignment', text='end-black')
    else:
        _insert_new_sub_element(transition_e, 'alignment', text='center')
    # todo support 'start' and 'end' alignment

    transition_e.append(_build_rate(timeline_range.start_time))

    effectid = transition_item.metadata.get(META_NAMESPACE, {}).get(
        'effectid', 'Cross Dissolve')

    effect_e = _insert_new_sub_element(transition_e, 'effect')
    _insert_new_sub_element(effect_e, 'name', text=transition_item.name)
    _insert_new_sub_element(effect_e, 'effectid', text=effectid)
    _insert_new_sub_element(effect_e, 'effecttype', text='transition')
    _insert_new_sub_element(effect_e, 'mediatype', text='video')

    return transition_e


def _build_clip_item_without_media(clip_item, timeline_range,
                                   transition_offsets, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')
    start_time = clip_item.source_range.start_time

    _insert_new_sub_element(clip_item_e, 'name', text=clip_item.name)
    clip_item_e.append(_build_rate(start_time))
    clip_item_e.append(
        _build_empty_file(clip_item.media_reference, start_time, br_map)
    )
    clip_item_e.extend([_build_marker(m) for m in clip_item.markers])
    timecode = otio.opentime.RationalTime(0, timeline_range.start_time.rate)

    _build_item_timings(clip_item_e, clip_item, timeline_range,
                        transition_offsets, timecode)

    return clip_item_e


def _build_clip_item(clip_item, timeline_range, transition_offsets, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    # set the clip name from the media reference if not defined on the clip
    if clip_item.name is not None:
        name = clip_item.name
    else:
        url_path = _url_to_path(clip_item.media_reference.target_url)
        name = os.path.basename(url_path)

    _insert_new_sub_element(clip_item_e, 'name',
                            text=name)
    clip_item_e.append(_build_file(clip_item.media_reference, br_map))
    if clip_item.media_reference.available_range:
        clip_item_e.append(_build_rate(
            clip_item.media_reference.available_range.start_time))
    clip_item_e.extend([_build_marker(m) for m in clip_item.markers])

    if clip_item.media_reference.available_range:
        timecode = clip_item.media_reference.available_range.start_time

        _build_item_timings(clip_item_e, clip_item, timeline_range,
                            transition_offsets, timecode)

    return clip_item_e


def _build_sequence_item(sequence, timeline_range, transition_offsets, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    _insert_new_sub_element(clip_item_e, 'name',
                            text=os.path.basename(sequence.name))

    sequence_e = _build_sequence(sequence, timeline_range, br_map)

    clip_item_e.append(_build_rate(sequence.source_range.start_time))
    clip_item_e.extend([_build_marker(m) for m in sequence.markers])
    clip_item_e.append(sequence_e)
    timecode = otio.opentime.RationalTime(0, timeline_range.start_time.rate)

    _build_item_timings(clip_item_e, sequence, timeline_range,
                        transition_offsets, timecode)

    return clip_item_e


def _build_item(item, timeline_range, transition_offsets, br_map):
    if isinstance(item, otio.schema.Transition):
        return _build_transition_item(item, timeline_range, transition_offsets,
                                      br_map)
    elif isinstance(item, otio.schema.Clip):
        if isinstance(item.media_reference,
                      otio.media_reference.MissingReference):
            return _build_clip_item_without_media(item, timeline_range,
                                                  transition_offsets, br_map)
        else:
            return _build_clip_item(item, timeline_range, transition_offsets,
                                    br_map)
    elif isinstance(item, otio.schema.Stack):
        return _build_sequence_item(item, timeline_range, transition_offsets,
                                    br_map)
    else:
        raise ValueError('Unsupported item: ' + str(item))


def _build_track(track, sequence_rate, br_map):
    track_e = cElementTree.Element('track')

    for n, item in enumerate(track):
        if isinstance(item, otio.schema.Gap):
            continue

        transition_offsets = [None, None]
        previous_item = track[n - 1] if n > 0 else None
        next_item = track[n + 1] if n + 1 < len(track) else None
        if not isinstance(item, otio.schema.Transition):
            # find out if this item has any neighboring transition
            if isinstance(previous_item, otio.schema.Transition):
                if previous_item.out_offset.value:
                    transition_offsets[0] = previous_item.in_offset
                else:
                    transition_offsets[0] = None
            if isinstance(next_item, otio.schema.Transition):
                if next_item.in_offset.value:
                    transition_offsets[1] = next_item.out_offset
                else:
                    transition_offsets[1] = None

        timeline_range = track.range_of_child_at_index(n)
        timeline_range = otio.opentime.TimeRange(
            timeline_range.start_time.rescaled_to(sequence_rate),
            timeline_range.duration.rescaled_to(sequence_rate)
        )
        track_e.append(
            _build_item(item, timeline_range, transition_offsets, br_map)
        )

    return track_e


def _build_marker(marker):
    marker_e = cElementTree.Element('marker')

    comment = marker.metadata.get(META_NAMESPACE, {}).get('comment', '')
    marked_range = marker.marked_range

    _insert_new_sub_element(marker_e, 'comment', text=comment)
    _insert_new_sub_element(marker_e, 'name', text=marker.name)
    _insert_new_sub_element(
        marker_e, 'in',
        text='{:.0f}'.format(marked_range.start_time.value)
    )
    _insert_new_sub_element(marker_e, 'out', text='-1')

    return marker_e


@_backreference_build('sequence')
def _build_sequence(stack, timeline_range, br_map):
    sequence_e = cElementTree.Element('sequence')
    _insert_new_sub_element(sequence_e, 'name', text=stack.name)
    _insert_new_sub_element(
        sequence_e, 'duration',
        text='{:.0f}'.format(timeline_range.duration.value)
    )
    sequence_e.append(_build_rate(timeline_range.start_time))
    sequence_rate = timeline_range.start_time.rate

    media_e = _insert_new_sub_element(sequence_e, 'media')
    video_e = _insert_new_sub_element(media_e, 'video')
    audio_e = _insert_new_sub_element(media_e, 'audio')

    for track in stack:
        if track.kind == otio.schema.SequenceKind.Video:
            video_e.append(_build_track(track, sequence_rate, br_map))
        elif track.kind == otio.schema.SequenceKind.Audio:
            audio_e.append(_build_track(track, sequence_rate, br_map))

    for marker in stack.markers:
        sequence_e.append(_build_marker(marker))

    return sequence_e


def _build_collection(collection, br_map):
    sequences = []
    for item in collection:
        if not isinstance(item, otio.schema.Timeline):
            continue

        timeline_range = otio.opentime.TimeRange(
            start_time=item.global_start_time,
            duration=item.duration()
        )
        sequences.append(_build_sequence(item.tracks, timeline_range, br_map))

    return sequences


# --------------------
# adapter requirements
# --------------------

def read_from_string(input_str):
    tree = cElementTree.fromstring(input_str)

    # element_map encodes the backreference context
    element_map = collections.defaultdict(dict)
    _populate_element_map(tree, element_map)

    top_level_sequences = _get_top_level_sequences(tree)

    if len(top_level_sequences) == 1:
        return _parse_timeline(top_level_sequences[0], element_map)
    elif len(top_level_sequences) > 1:
        return _parse_collection(top_level_sequences, element_map)
    else:
        raise ValueError('No top-level sequences found')


def write_to_string(input_otio):
    tree_e = cElementTree.Element('xmeml', version="4")
    project_e = _insert_new_sub_element(tree_e, 'project')
    _insert_new_sub_element(project_e, 'name', text=input_otio.name)
    children_e = _insert_new_sub_element(project_e, 'children')

    br_map = collections.defaultdict(dict)
    _populate_backreference_map(input_otio, br_map)

    if isinstance(input_otio, otio.schema.Timeline):
        timeline_range = otio.opentime.TimeRange(
            start_time=input_otio.global_start_time,
            duration=input_otio.duration()
        )
        children_e.append(
            _build_sequence(input_otio.tracks, timeline_range, br_map)
        )
    elif isinstance(input_otio, otio.schema.SerializeableCollection):
        children_e.extend(
            _build_collection(input_otio, br_map)
        )

    return _make_pretty_string(tree_e)
