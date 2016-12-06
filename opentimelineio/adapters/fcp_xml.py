import os
import urlparse
import math
from collections import defaultdict
from xml.etree import cElementTree
from xml.dom import minidom

import opentimelineio as otio

META_NAMESPACE = 'fcp_xml'  # namespace to use for metadata

CLIP_REFERENCES = {}  # {media-url: cElementTree.Element(clip)}
ELEMENT_MAP = defaultdict(dict)
ID_MAP = defaultdict(dict)


# ---------
# utilities
# ---------

def _backreference_parse(tag):
    # Some elements in an xml can have an id. Sometimes a certain element with
    # the same id occurs multiple times in a file. In that case it is
    # back-reference to the earlier element. In that case we want to pass that
    # back-reference to the wrapped function
    global ELEMENT_MAP

    def singleton_decorator(func):
        def wrapper(elem, *args, **kwargs):
            elem = ELEMENT_MAP[tag].setdefault(elem.attrib['id'], elem)
            return func(elem, *args, **kwargs)

        return wrapper

    return singleton_decorator


def _backreference_build(tag):
    # We can also encode these back-references if an item is accessed multiple
    # times. To do this we store an id attribute on the element. For back-
    # references we then only need to return an empty element of that type with
    # the id we logged before
    global ID_MAP

    def singleton_decorator(func):
        def wrapper(item, *args, **kwargs):
            item_hash = item.__hash__()
            item_id = ID_MAP[tag].get(item_hash, None)
            if item_id is not None:
                return cElementTree.Element(tag, id='%s-%d' % (tag, item_id))
            item_id = ID_MAP[tag].setdefault(item_hash,
                                             max(ID_MAP[tag].values() +
                                                 [0]) + 1)
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

@_backreference_parse('all_elements')
def _parse_rate(elem):
    rate = elem.find('./rate')
    # rate is encoded as a timebase (int) which can be drop-frame
    base = float(rate.find('./timebase').text)
    if rate.find('./ntsc').text == 'TRUE':
        base *= .999
    return base


@_backreference_parse('file')
def _parse_media_reference(file_e):
    url = file_e.find('./pathurl').text
    rate = _parse_rate(file_e)
    duration = int(file_e.find('./duration').text)

    available_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(0, rate),
        duration=otio.opentime.RationalTime(duration, rate)
    )

    return otio.media_reference.External(target_url=url.strip(),
                                         available_range=available_range)


def _parse_clip_item(clip_item):
    markers = clip_item.findall('./marker')

    media_reference = _parse_media_reference(clip_item.find('./file'))
    source_rate = _parse_rate(clip_item.find('./file'))

    metadata = {META_NAMESPACE: {
        'description': clip_item.find('./logginginfo/description').text,
        'scene': clip_item.find('./logginginfo/scene').text,
        'shottake': clip_item.find('./logginginfo/shottake').text,
        'lognote': clip_item.find('./logginginfo/lognote').text
    }
    }

    clip = otio.schema.Clip(media_reference=media_reference)
    clip.markers.extend(
        [_parse_marker(m, source_rate) for m in markers])
    clip.metadata = metadata
    return clip


@_backreference_parse('clipitem')
def _parse_item(clip_item):
    # depending on the content of the clip-item, we return either a clip or a
    # stack. In either case we set the source range as well
    if clip_item.find('./file') is not None:
        item = _parse_clip_item(clip_item)
        source_rate = _parse_rate(clip_item.find('./file'))
    elif clip_item.find('./sequence') is not None:
        item = _parse_sequence(clip_item.find('./sequence'))
        source_rate = _parse_rate(clip_item.find('./sequence'))
    else:
        raise TypeError('Type of clip item is not supported %s' %
                        clip_item.attrib['id'])

    in_frame = int(clip_item.find('./in').text)
    out_frame = int(clip_item.find('./out').text)
    source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(in_frame, source_rate),
        duration=otio.opentime.RationalTime(out_frame - in_frame, source_rate)
    )
    item.source_range = source_range

    return item


def _parse_track(track_e, kind, rate):
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
        track.append(_parse_item(clip_item))

    return track


def _parse_marker(marker, rate):
    marker_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(
            int(marker.find('./in').text), rate))
    metadata = {META_NAMESPACE: {'comment': marker.find('./comment').text}}
    return otio.schema.Marker(name=marker.find('./name').text,
                              range=marker_range,
                              metadata=metadata)


@_backreference_parse('sequence')
def _parse_sequence(sequence):
    sequence_rate = _parse_rate(sequence)

    video_tracks = sequence.findall('./media/video/track')
    audio_tracks = sequence.findall('./media/audio/track')
    markers = sequence.findall('./marker')

    stack = otio.schema.Stack(name=sequence.find('./name').text)

    stack.extend(
        [_parse_track(t, otio.schema.SequenceKind.Video, sequence_rate)
         for t in video_tracks])
    stack.extend(
        [_parse_track(t, otio.schema.SequenceKind.Audio, sequence_rate)
         for t in audio_tracks
         if _is_primary_audio_channel(t)])
    stack.markers.extend([_parse_marker(m, sequence_rate) for m in markers])

    return stack


# ------------------------
# building single sequence
# ------------------------

def _build_rate(time):
    if isinstance(time, otio.opentime.TimeRange):
        time = time.start_time
    elif not isinstance(time, otio.opentime.RationalTime):
        raise ValueError('Invalid object passed: %s' % str(time))

    rate = math.ceil(time.rate)

    rate_e = cElementTree.Element('rate')
    _insert_new_sub_element(rate_e, 'timebase', text=str(int(rate)))
    _insert_new_sub_element(rate_e, 'ntsc',
                            text='FALSE' if rate == time.rate else 'TRUE')
    return rate_e


def _build_clip(n, media_reference):
    clip_e = cElementTree.Element('clip', id='masterclip-%d' % n)

    available_range = media_reference.available_range
    url = urlparse.urlparse(media_reference.target_url)

    _insert_new_sub_element(clip_e, 'masterclipid', text='masterclip-%d' % n)
    _insert_new_sub_element(clip_e, 'ismasterclip', text='TRUE')
    _insert_new_sub_element(clip_e, 'duration',
                            text=str(available_range.duration.value))
    clip_e.append(_build_rate(available_range))
    _insert_new_sub_element(clip_e, 'name', text=os.path.basename(url.path))

    file_e = _insert_new_sub_element(clip_e, 'file',
                                     attrib={'id': 'file-%d' % n})
    _insert_new_sub_element(file_e, 'name', text=os.path.basename(url.path))
    file_e.append(_build_rate(available_range))
    _insert_new_sub_element(file_e, 'duration',
                            text=str(available_range.duration.value))
    _insert_new_sub_element(file_e, 'pathurl', text=media_reference.target_url)

    # we need to flag the file reference with the content types, otherwise it
    # will not get recognized
    file_media_e = _insert_new_sub_element(file_e, 'media')

    content_types = []
    if not os.path.splitext(url.path)[1].lower() in ('.wav', '.aaf', '.mp3'):
        content_types.append('video')
    content_types.append('audio')

    media = _insert_new_sub_element(clip_e, 'media')
    for kind in content_types:
        _insert_new_sub_element(file_media_e, kind)
        kind_e = _insert_new_sub_element(media, kind)
        track_e = _insert_new_sub_element(kind_e, 'track')
        clip_item_e = _insert_new_sub_element(track_e, 'clipitem')
        _insert_new_sub_element(clip_item_e, 'masterclipid',
                                text='masterclip-%d' % n)
        _insert_new_sub_element(clip_item_e, 'name',
                                text=os.path.basename(url.path))
        clip_item_e.append(_build_rate(available_range))
        _insert_new_sub_element(clip_item_e, 'file',
                                attrib={'id': 'file-%d' % n})

    return clip_e


def _build_clip_item(clip_item):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    clip_ref_e = CLIP_REFERENCES.get(clip_item.media_reference.target_url)
    clip_ref_file_id = clip_ref_e.find('./file').attrib['id']
    url = urlparse.urlparse(clip_item.media_reference.target_url)

    _insert_new_sub_element(clip_item_e, 'name',
                            text=os.path.basename(url.path))
    _insert_new_sub_element(clip_item_e, 'masterclipid',
                            text=clip_ref_e.attrib['id'])
    _insert_new_sub_element(clip_item_e, 'file',
                            attrib={'id': clip_ref_file_id})

    metadata = clip_item.metadata.get(META_NAMESPACE, None)
    if metadata:
        logginginfo = _insert_new_sub_element(clip_item_e, 'logginginfo')
        for k, v in metadata.items():
            _insert_new_sub_element(logginginfo, k, text=v)

    clip_item_e.append(_build_rate(clip_item.media_reference.available_range))
    clip_item_e.extend([_build_marker(m) for m in clip_item.markers])

    return clip_item_e


def _build_sequence_item(sequence, timeline_range):
    clip_item_e = cElementTree.Element('clipitem', frameBlend='FALSE')

    _insert_new_sub_element(clip_item_e, 'name',
                            text=os.path.basename(sequence.name))

    metadata = sequence.metadata.get(META_NAMESPACE, None)
    if metadata:
        logginginfo = _insert_new_sub_element(clip_item_e, 'logginginfo')
        for k, v in metadata.items():
            _insert_new_sub_element(logginginfo, k, text=v)

    sequence_e = _build_sequence(sequence, timeline_range)

    clip_item_e.append(_build_rate(sequence.source_range))
    clip_item_e.extend([_build_marker(m) for m in sequence.markers])
    clip_item_e.append(sequence_e)

    return clip_item_e


def _build_item(item, timeline_range):
    if isinstance(item, otio.schema.Clip):
        item_e = _build_clip_item(item)
    elif isinstance(item, otio.schema.Stack):
        item_e = _build_sequence_item(item, timeline_range)
    else:
        raise ValueError('Unsupported item: ' + str(item))

    _insert_new_sub_element(item_e, 'duration',
                            text=str(int(item.source_range.duration.value)))
    _insert_new_sub_element(item_e, 'start',
                            text=str(int(timeline_range.start_time.value)))
    _insert_new_sub_element(item_e, 'end',
                            text=str(int(timeline_range.end_time().value)))
    _insert_new_sub_element(item_e, 'in',
                            text=str(int(item.source_range.start_time.value)))
    _insert_new_sub_element(item_e, 'out',
                            text=str(int(item.source_range.end_time().value)))
    return item_e


def _build_track(track):
    track_e = cElementTree.Element('track')

    for n, item in enumerate(track):
        if isinstance(item, otio.schema.Filler):
            continue
        timeline_range = track.range_of_child_at_index(n)
        track_e.append(_build_item(item, timeline_range))

    return track_e


def _build_marker(marker):
    marker_e = cElementTree.Element('marker')

    comment = marker.metadata.get(META_NAMESPACE, {}).get('comment', '')

    _insert_new_sub_element(marker_e, 'comment', text=comment)
    _insert_new_sub_element(marker_e, 'name', text=marker.name)
    _insert_new_sub_element(marker_e, 'in',
                            text=str(int(marker.range.start_time.value)))
    _insert_new_sub_element(marker_e, 'out', text='-1')

    return marker_e


@_backreference_build('sequence')
def _build_sequence(stack, timeline_range):
    sequence_e = cElementTree.Element('sequence')
    _insert_new_sub_element(sequence_e, 'name', text=stack.name)
    _insert_new_sub_element(sequence_e, 'duration',
                            text=str(int(timeline_range.duration.value)))
    sequence_e.append(_build_rate(timeline_range))

    media_e = _insert_new_sub_element(sequence_e, 'media')
    video_e = _insert_new_sub_element(media_e, 'video')
    audio_e = _insert_new_sub_element(media_e, 'audio')

    for track in stack:
        if track.kind == otio.schema.SequenceKind.Video:
            video_e.append(_build_track(track))
        elif track.kind == otio.schema.SequenceKind.Audio:
            audio_e.append(_build_track(track))

    for marker in stack.markers:
        sequence_e.append(_build_marker(marker))

    return sequence_e


# --------------------
# adapter requirements
# --------------------

def read_from_string(input_str):
    global ELEMENT_MAP

    tree = cElementTree.fromstring(input_str)
    sequence = _get_single_sequence(tree)

    ELEMENT_MAP = defaultdict(dict)
    sequence_rate = _parse_rate(sequence)
    timeline = otio.schema.Timeline(name=sequence.find('./name').text)
    timeline.global_start_time = otio.opentime.RationalTime(0, sequence_rate)
    timeline.tracks = _parse_sequence(sequence)
    ELEMENT_MAP = defaultdict(dict)

    return timeline


def write_to_string(input_otio):
    global CLIP_REFERENCES
    global ID_MAP

    tree_e = cElementTree.Element('xmeml', version="4")
    project_e = _insert_new_sub_element(tree_e, 'project')
    _insert_new_sub_element(project_e, 'name', text=input_otio.name)
    children_e = _insert_new_sub_element(project_e, 'children')

    media_references = [c.media_reference for t in input_otio.tracks
                        for c in t if isinstance(c, otio.schema.Clip)
                        and c.media_reference is not None]
    unique_media_references = dict((x.target_url, x)
                                   for x in media_references).values()

    ID_MAP = defaultdict(dict)
    CLIP_REFERENCES = dict((r.target_url, _build_clip(n, r))
                           for n, r in enumerate(unique_media_references))

    children_e.extend(CLIP_REFERENCES.values())

    timeline_range = otio.opentime.TimeRange(
        start_time=input_otio.global_start_time,
        duration=input_otio.duration()
    )

    children_e.append(_build_sequence(input_otio.tracks, timeline_range))

    CLIP_REFERENCES = {}
    ID_MAP = defaultdict(dict)

    return _make_pretty_string(tree_e)
