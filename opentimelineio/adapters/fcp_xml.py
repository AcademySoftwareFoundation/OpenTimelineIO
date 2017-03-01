import os
import math
import functools
import collections
from xml.etree import cElementTree
from xml.dom import minidom

try:
    import urlparse
except ImportError:
    import urllib.parse

import opentimelineio as otio

META_NAMESPACE = 'fcp_xml'  # namespace to use for metadata


# ---------
# utilities
# ---------

def _url_to_path(url):
    try:
        parsed = urlparse.urlparse(url)
    except NameError:
        parsed = urllib.parse.urlparse(url)
    return parsed.path


def _resolved_backreference(elem, tag, element_map):
    if 'id' in elem.attrib:
        elem = element_map[tag].setdefault(elem.attrib['id'], elem)

    return elem


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
            else:
                item_hash = item.__hash__()
            item_id = br_map[tag].get(item_hash, None)
            if item_id is not None:
                return cElementTree.Element(tag, id='%s-%d' % (tag, item_id))
            item_id = br_map[tag].setdefault(item_hash,
                                             1 if not br_map[tag] else
                                             max(br_map[tag].values()) + 1)
            elem = func(item, *args, **kwargs)
            elem.attrib['id'] = '%s-%d' % (tag, item_id)
            return elem

        return wrapper

    return singleton_decorator


def _insert_new_sub_element(into_parent, tag, attrib=None, text=''):
    elem = cElementTree.SubElement(into_parent, tag, **attrib or {})
    elem.text = text
    return elem


def _get_single_sequence(tree):
    top_level_sequences = tree.findall('.//project/children/sequence') + \
                          tree.findall('./sequence')
    if len(top_level_sequences) > 1:
        raise NotImplementedError('Multiple sequences are not supported')
    return top_level_sequences[0]


def _make_pretty_string(tree_e):
    # most of the parsing in this adapter is done with cElementTree because it
    # is simpler and faster. However, the string representation it returns is
    # far from elegant. Therefor we feed it through minidom to provide an xml
    # with indentations.
    string = cElementTree.tostring(tree_e, encoding="UTF-8", method="xml")
    dom = minidom.parseString(string)
    return dom.toprettyxml(indent='    ', encoding='UTF-8')


def _is_primary_audio_channel(track):
    # audio may be structured in stereo where each channel occupies a separate
    # track. Some xml logic combines these into a single track upon import.
    # Here we check whether we`re dealing with the first audio channel
    return (
        track.attrib.get('currentExplodedTrackIndex', '0') == '0'
        or track.attrib.get('totalExplodedTrackCount', '1') == '1'
    )


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

    file_rate = _parse_rate(file_e, element_map)
    timecode_rate = _parse_rate(file_e.find('./timecode'), element_map)
    timecode_frame = int(file_e.find('./timecode/frame').text)
    url_e = file_e.find('./pathurl')

    if url_e is None:
        available_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(timecode_frame,
                                                  timecode_rate),
            duration=otio.opentime.RationalTime(5 * timecode_rate,
                                                timecode_rate)
        )
        return otio.media_reference.External(
            target_url=None,
            available_range=available_range
        )

    url = url_e.text
    duration = int(file_e.find('./duration').text)

    available_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(timecode_frame, timecode_rate),
        duration=otio.opentime.RationalTime(duration, file_rate)
    )

    return otio.media_reference.External(
        target_url=url.strip(),
        available_range=available_range
    )


def _parse_clip_item(clip_item, element_map):
    markers = clip_item.findall('./marker')

    media_reference = _parse_media_reference(
        clip_item.find('./file'),
        element_map
    )
    source_rate = _parse_rate(clip_item.find('./file'), element_map)

    # get the clip name from the media reference if not defined on the clip
    name_item = clip_item.find('name')
    if name_item is not None:
        name = name_item.text
    else:
        url_path = _url_to_path(media_reference.target_url)
        name = os.path.basename(url_path)

    clip = otio.schema.Clip(name=name,
                            media_reference=media_reference)
    clip.markers.extend(
        [_parse_marker(m, source_rate) for m in markers])
    return clip


def _parse_item(clip_item, element_map):
    # depending on the content of the clip-item, we return either a clip or a
    # stack. In either case we set the source range as well
    if clip_item.find('./file') is not None:
        item = _parse_clip_item(clip_item, element_map)
        source_rate = _parse_rate(clip_item.find('./file'), element_map)
        timecode = item.media_reference.available_range.start_time
    elif clip_item.find('./sequence') is not None:
        item = _parse_sequence(clip_item.find('./sequence'), element_map)
        source_rate = _parse_rate(clip_item.find('./sequence'), element_map)
        timecode = otio.opentime.RationalTime(0, source_rate)
    else:
        raise TypeError('Type of clip item is not supported %s' %
                        clip_item.attrib['id'])

    in_frame = int(clip_item.find('./in').text)
    out_frame = int(clip_item.find('./out').text)

    # source_start in xml is taken relative to the start of the media, whereas
    # we want the absolute start time, taking into account the timecode
    source_start = otio.opentime.RationalTime(in_frame, source_rate) + timecode
    source_range = otio.opentime.TimeRange(
        start_time=source_start,
        duration=otio.opentime.RationalTime(out_frame - in_frame, source_rate)
    )
    item.source_range = source_range

    return item


def _parse_track(track_e, kind, rate, element_map):
    track = otio.schema.Sequence(kind=kind)
    clip_items = track_e.findall('./clipitem')

    if not clip_items:
        return track

    last_clip_end = 0
    for clip_item in clip_items:
        clip_item_index = list(track_e).index(clip_item)
        start = int(clip_item.find('./start').text)
        end = int(clip_item.find('./end').text)

        # start time and end time on the timeline can be set to -1. This means
        # that there is a transition at that end of the clip-item. So the time
        # on the timeline has to be taken from that object.
        if start == -1:
            in_transition = list(track_e)[clip_item_index - 1]
            start = int(in_transition.find('./start').text)
        if end == -1:
            out_transition = list(track_e)[clip_item_index + 1]
            end = int(out_transition.find('./end').text)

        # see if we need to add a filler before this clip-item
        fill_time = start - last_clip_end
        last_clip_end = end
        if fill_time:
            filler_range = otio.opentime.TimeRange(
                duration=otio.opentime.RationalTime(fill_time, rate))
            track.append(otio.schema.Filler(source_range=filler_range))

        # finally add the clip-item itself
        track.append(_parse_item(clip_item, element_map))

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


@_backreference_build('file')
def _build_file(media_reference, br_map):
    file_e = cElementTree.Element('file')

    available_range = media_reference.available_range
    file_e.append(_build_rate(available_range.start_time))
    _insert_new_sub_element(file_e, 'duration',
                            text=str(available_range.duration.value))

    # timecode
    timecode = available_range.start_time
    timecode_e = _insert_new_sub_element(file_e, 'timecode')
    timecode_e.append(_build_rate(timecode))
    _insert_new_sub_element(timecode_e, 'string',
                            text=otio.opentime.to_timecode(timecode))
    _insert_new_sub_element(timecode_e, 'frame', text=str(int(timecode.value)))
    display_format = 'DF' if (math.ceil(timecode.rate) == 30
                              and math.ceil(timecode.rate) != timecode.rate) \
        else 'NDF'
    _insert_new_sub_element(timecode_e, 'displayformat', text=display_format)

    if media_reference.target_url is not None:
        url_path = _url_to_path(media_reference.target_url)

        _insert_new_sub_element(file_e, 'name',
                                text=os.path.basename(url_path))
        _insert_new_sub_element(file_e, 'pathurl',
                                text=media_reference.target_url)
    else:
        return file_e

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


def _build_clip_item(clip_item, br_map):
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
    clip_item_e.append(_build_rate(
        clip_item.media_reference.available_range.start_time))
    clip_item_e.extend([_build_marker(m) for m in clip_item.markers])

    return clip_item_e


def _build_sequence_item(sequence, timeline_range, br_map):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    _insert_new_sub_element(clip_item_e, 'name',
                            text=os.path.basename(sequence.name))

    sequence_e = _build_sequence(sequence, timeline_range, br_map)

    clip_item_e.append(_build_rate(sequence.source_range.start_time))
    clip_item_e.extend([_build_marker(m) for m in sequence.markers])
    clip_item_e.append(sequence_e)

    return clip_item_e


def _build_item(item, timeline_range, br_map):
    if isinstance(item, otio.schema.Clip):
        item_e = _build_clip_item(item, br_map)
        timecode = item.media_reference.available_range.start_time
    elif isinstance(item, otio.schema.Stack):
        item_e = _build_sequence_item(item, timeline_range, br_map)
        timecode = otio.opentime.RationalTime(0,
                                              timeline_range.start_time.rate)
    else:
        raise ValueError('Unsupported item: ' + str(item))

    # source_start is absolute time taking into account the timecode of the
    # media. But xml regards the source in point from the start of the media.
    # So we subtract the media timecode.
    source_start = item.source_range.start_time - timecode
    source_end = item.source_range.end_time() - timecode

    _insert_new_sub_element(item_e, 'duration',
                            text=str(int(item.source_range.duration.value)))
    _insert_new_sub_element(item_e, 'start',
                            text=str(int(timeline_range.start_time.value)))
    _insert_new_sub_element(item_e, 'end',
                            text=str(int(timeline_range.end_time().value)))
    _insert_new_sub_element(item_e, 'in',
                            text=str(int(source_start.value)))
    _insert_new_sub_element(item_e, 'out',
                            text=str(int(source_end.value)))
    return item_e


def _build_track(track, br_map):
    track_e = cElementTree.Element('track')

    for n, item in enumerate(track):
        if isinstance(item, otio.schema.Filler):
            continue
        timeline_range = track.range_of_child_at_index(n)
        track_e.append(_build_item(item, timeline_range, br_map))

    return track_e


def _build_marker(marker):
    marker_e = cElementTree.Element('marker')

    comment = marker.metadata.get(META_NAMESPACE, {}).get('comment', '')
    marked_range = marker.marked_range

    _insert_new_sub_element(marker_e, 'comment', text=comment)
    _insert_new_sub_element(marker_e, 'name', text=marker.name)
    _insert_new_sub_element(marker_e, 'in',
                            text=str(int(marked_range.start_time.value)))
    _insert_new_sub_element(marker_e, 'out', text='-1')

    return marker_e


@_backreference_build('sequence')
def _build_sequence(stack, timeline_range, br_map):
    sequence_e = cElementTree.Element('sequence')
    _insert_new_sub_element(sequence_e, 'name', text=stack.name)
    _insert_new_sub_element(sequence_e, 'duration',
                            text=str(int(timeline_range.duration.value)))
    sequence_e.append(_build_rate(timeline_range.start_time))

    media_e = _insert_new_sub_element(sequence_e, 'media')
    video_e = _insert_new_sub_element(media_e, 'video')
    audio_e = _insert_new_sub_element(media_e, 'audio')

    for track in stack:
        if track.kind == otio.schema.SequenceKind.Video:
            video_e.append(_build_track(track, br_map))
        elif track.kind == otio.schema.SequenceKind.Audio:
            audio_e.append(_build_track(track, br_map))

    for marker in stack.markers:
        sequence_e.append(_build_marker(marker))

    return sequence_e


# --------------------
# adapter requirements
# --------------------

def read_from_string(input_str):
    tree = cElementTree.fromstring(input_str)
    sequence = _get_single_sequence(tree)

    # element_map encodes the backreference context
    element_map = collections.defaultdict(dict)

    sequence_rate = _parse_rate(sequence, element_map)
    timeline = otio.schema.Timeline(name=sequence.find('./name').text)
    timeline.global_start_time = otio.opentime.RationalTime(0, sequence_rate)
    timeline.tracks = _parse_sequence(sequence, element_map)

    return timeline


def write_to_string(input_otio):
    tree_e = cElementTree.Element('xmeml', version="4")
    project_e = _insert_new_sub_element(tree_e, 'project')
    _insert_new_sub_element(project_e, 'name', text=input_otio.name)
    children_e = _insert_new_sub_element(project_e, 'children')

    timeline_range = otio.opentime.TimeRange(
        start_time=input_otio.global_start_time,
        duration=input_otio.duration()
    )

    br_map = collections.defaultdict(dict)
    children_e.append(
        _build_sequence(input_otio.tracks, timeline_range, br_map)
    )

    return _make_pretty_string(tree_e)
