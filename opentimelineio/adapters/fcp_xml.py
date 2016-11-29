import os
from urlparse import urlparse
import math
from xml.etree import cElementTree
from xml.dom import minidom

import opentimelineio as otio

META_NAMESPACE = 'fcp_xml'  # namespace to use for metadata

MEDIA_REFERENCES = {}  # {file-id: otio.media_reference.External}
CLIP_REFERENCES = {}  # {media-url: cElementTree.Element(clip)}
SEQUENCE_RATE = 30  # rate of the sequence being parsed


# ---------
# utilities
# ---------

def _sub_element(parent, tag, attrib=None, text=''):
    elem = cElementTree.SubElement(parent, tag, **attrib or {})
    elem.text = text
    return elem


def _get_single_sequence(tree):
    sequences = tree.findall('.//sequence')
    if len(sequences) > 1:
        raise NotImplementedError('Multiple sequences are not supported')
    return sequences[0]


def _make_indented_string(string):
    # most of the parsing in this adapter is done with cElementTree because it
    # is simpler and faster. However, the string representation it returns is
    # far from elegant. Therefor we feed it through minidom to provide an xml
    # with indentations.
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

def _parse_rate(rate):
    # rate is encoded as a timebase (int) which can be drop-frame
    base = float(rate.find('./timebase').text)
    if rate.find('./ntsc').text == 'TRUE':
        base *= .999
    return base


def _parse_media_reference(file_e):
    url = file_e.find('./pathurl').text
    rate = _parse_rate(file_e.find('./rate'))
    duration = int(file_e.find('./duration').text)

    available_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(0, rate),
        duration=otio.opentime.RationalTime(duration, rate)
    )

    return otio.media_reference.External(target_url=url,
                                         available_range=available_range)


def _parse_clip_item(clip_item):
    file_id = clip_item.find('./file').attrib['id']
    in_frame = int(clip_item.find('./in').text)
    out_frame = int(clip_item.find('./out').text)

    media_reference = MEDIA_REFERENCES.get(file_id, None)
    ref_rate = media_reference.available_range.start_time.rate

    metadata = {META_NAMESPACE: {
        'description': clip_item.find('./logginginfo/description').text,
        'scene': clip_item.find('./logginginfo/scene').text,
        'shottake': clip_item.find('./logginginfo/shottake').text,
        'lognote': clip_item.find('./logginginfo/lognote').text
    }
    }

    if media_reference is not None:
        in_frame -= media_reference.available_range.start_time.value

    source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(in_frame, ref_rate),
        duration=otio.opentime.RationalTime(out_frame - in_frame, ref_rate)
    )

    clip = otio.schema.Clip(media_reference=media_reference,
                            source_range=source_range)
    clip.metadata = metadata
    return clip


def _parse_track(track_e, kind):
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
                duration=otio.opentime.RationalTime(fill_time, SEQUENCE_RATE))
            track.append(otio.schema.Filler(source_range=filler_range))

        # finally add the clip-item itself
        track.append(_parse_clip_item(clip_item))

    return track


def _parse_marker(marker):
    marker_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(
            int(marker.find('./in').text), SEQUENCE_RATE))
    metadata = {META_NAMESPACE: {'comment': marker.find('./comment').text}}
    return otio.schema.Marker(name=marker.find('./name').text,
                              range=marker_range,
                              metadata=metadata)


def _parse_sequence(sequence):
    global SEQUENCE_RATE
    SEQUENCE_RATE = _parse_rate(sequence.find('./rate'))

    timeline = otio.schema.Timeline(name=sequence.find('./name').text)
    timeline.global_start_time = otio.opentime.RationalTime(0, SEQUENCE_RATE)

    video_tracks = sequence.findall('.//video/track')
    audio_tracks = sequence.findall('.//audio/track')
    markers = sequence.findall('.//marker')

    timeline.tracks.extend([_parse_track(t, otio.schema.SequenceKind.Video)
                            for t in video_tracks])
    timeline.tracks.extend([_parse_track(t, otio.schema.SequenceKind.Audio)
                            for t in audio_tracks
                            if _is_primary_audio_channel(t)])
    timeline.tracks.markers.extend([_parse_marker(m) for m in markers])
    return timeline


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
    _sub_element(rate_e, 'timebase', text=str(int(rate)))
    _sub_element(rate_e, 'ntsc', text='FALSE' if rate == time.rate
    else 'TRUE')
    return rate_e


def _build_clip(n, media_reference):
    clip_e = cElementTree.Element('clip', id='masterclip-%d' % n)

    available_range = media_reference.available_range
    url = urlparse(media_reference.target_url)

    _sub_element(clip_e, 'masterclipid', text='masterclip-%d' % n)
    _sub_element(clip_e, 'ismasterclip', text='TRUE')
    _sub_element(clip_e, 'duration', text=str(available_range.duration.value))
    clip_e.append(_build_rate(available_range))
    _sub_element(clip_e, 'name', text=os.path.basename(url.path))

    file_e = _sub_element(clip_e, 'file', attrib={'id': 'file-%d' % n})
    _sub_element(file_e, 'name', text=os.path.basename(url.path))
    file_e.append(_build_rate(available_range))
    _sub_element(file_e, 'duration', text=str(available_range.duration.value))
    _sub_element(file_e, 'pathurl', text=media_reference.target_url)

    # we need to flag the file reference with the content types, otherwise it
    # will not get recognized
    file_media_e = _sub_element(file_e, 'media')

    content_types = []
    if not os.path.splitext(url.path)[1].lower() in ('.wav', '.aaf', '.mp3'):
        content_types.append('video')
    content_types.append('audio')

    media = _sub_element(clip_e, 'media')
    for kind in content_types:
        _sub_element(file_media_e, kind)
        kind_e = _sub_element(media, kind)
        track_e = _sub_element(kind_e, 'track')
        clip_item_e = _sub_element(track_e, 'clipitem')
        _sub_element(clip_item_e, 'masterclipid', text='masterclip-%d' % n)
        _sub_element(clip_item_e, 'name', text=os.path.basename(url.path))
        clip_item_e.append(_build_rate(available_range))
        _sub_element(clip_item_e, 'file', attrib={'id': 'file-%d' % n})

    return clip_e


def _build_clip_item(clip_item, timeline_range):
    clip_item_e = cElementTree.Element('clipitem',
                                       frameBlend='FALSE')

    clip_ref_e = CLIP_REFERENCES.get(clip_item.media_reference.target_url)
    url = urlparse(clip_item.media_reference.target_url)

    _sub_element(clip_item_e, 'name', text=os.path.basename(url.path))
    _sub_element(clip_item_e, 'masterclipid', text=clip_ref_e.attrib['id'])
    _sub_element(clip_item_e, 'duration',
                 text=str(int(clip_item.source_range.duration.value)))
    _sub_element(clip_item_e, 'start',
                 text=str(int(timeline_range.start_time.value)))
    _sub_element(clip_item_e, 'end',
                 text=str(int(timeline_range.end_time().value)))
    _sub_element(clip_item_e, 'in',
                 text=str(int(clip_item.source_range.start_time.value)))
    _sub_element(clip_item_e, 'out',
                 text=str(int(clip_item.source_range.end_time().value)))
    _sub_element(clip_item_e, 'file',
                 attrib={'id': clip_ref_e.find('./file').attrib['id']})

    metadata = clip_item.metadata.get(META_NAMESPACE, None)
    if metadata:
        logginginfo = _sub_element(clip_item_e, 'logginginfo')
        for k, v in metadata.items():
            _sub_element(logginginfo, k, text=v)

    clip_item_e.append(_build_rate(clip_item.media_reference.available_range))

    return clip_item_e


def _build_track(track):
    track_e = cElementTree.Element('track')

    for n, item in enumerate(track):
        if isinstance(item, otio.schema.Filler):
            continue
        timeline_range = track.range_of_child_at_index(n)
        track_e.append(_build_clip_item(item, timeline_range))

    return track_e


def _build_marker(marker):
    marker_e = cElementTree.Element('marker')

    comment = marker.metadata.get(META_NAMESPACE, {}).get('comment', '')

    _sub_element(marker_e, 'comment', text=comment)
    _sub_element(marker_e, 'name', text=marker.name)
    _sub_element(marker_e, 'in', text=str(int(marker.range.start_time.value)))
    _sub_element(marker_e, 'out', text='-1')

    return marker_e


def _build_sequence(timeline):
    sequence_e = cElementTree.Element('sequence', id='sequence-0')
    _sub_element(sequence_e, 'name', text=timeline.name)
    _sub_element(sequence_e, 'duration',
                 text=str(int(timeline.duration().value)))
    sequence_e.append(_build_rate(timeline.global_start_time))

    media_e = _sub_element(sequence_e, 'media')
    video_e = _sub_element(media_e, 'video')
    audio_e = _sub_element(media_e, 'audio')

    for track in timeline.tracks:
        if track.kind == otio.schema.SequenceKind.Video:
            video_e.append(_build_track(track))
        elif track.kind == otio.schema.SequenceKind.Audio:
            audio_e.append(_build_track(track))

    for marker in timeline.tracks.markers:
        sequence_e.append(_build_marker(marker))

    return sequence_e


# --------------------
# adapter requirements
# --------------------

def read_from_string(input_str):
    global MEDIA_REFERENCES

    tree = cElementTree.fromstring(input_str)
    sequence = _get_single_sequence(tree)

    MEDIA_REFERENCES = dict((f.attrib.get('id'), _parse_media_reference(f))
                            for f in tree.findall('.//file')
                            if f.find('./pathurl') is not None)

    timeline = _parse_sequence(sequence)
    MEDIA_REFERENCES = {}

    return timeline


def write_to_string(input_otio):
    global CLIP_REFERENCES

    tree_e = cElementTree.Element('xmeml', version="4")
    project_e = _sub_element(tree_e, 'project')
    _sub_element(project_e, 'name', text=input_otio.name)
    children_e = _sub_element(project_e, 'children')

    media_references = [c.media_reference for t in input_otio.tracks
                        for c in t if isinstance(c, otio.schema.Clip)
                        and c.media_reference is not None]
    unique_media_references = dict((x.target_url, x)
                                   for x in media_references).values()
    CLIP_REFERENCES = dict((r.target_url, _build_clip(n, r))
                           for n, r in enumerate(unique_media_references))

    children_e.extend(CLIP_REFERENCES.values())
    children_e.append(_build_sequence(input_otio))

    CLIP_REFERENCES = {}

    string = cElementTree.tostring(tree_e, encoding="UTF-8", method="xml")
    return _make_indented_string(string)
