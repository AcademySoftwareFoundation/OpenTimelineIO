# MIT License
#
# Copyright (c) 2018 Daniel Flehner Heen (Storm Studios)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import shlex
from subprocess import call, Popen, PIPE
from xml.dom import minidom
from xml.etree import cElementTree as et

import opentimelineio as otio


GOT_MELT = False
MELT_BIN = os.getenv('OTIO_MELT_BIN') or 'melt'
try:
    GOT_MELT = call(MELT_BIN, stderr=PIPE, stdout=PIPE) == 0

except OSError:
    # Looks like we don't have melt in PATH or OTIO_MELT_PATH.
    # Some features like file analysis are unavailable
    pass

# Supported MLT XML styles.
# Could include Shotcut, kdenlive etc. in the future.
VALID_MLT_STYLES = ['mlt']

# Holders of elements
_profile_e = None
_producers = []
_playlists = []
_tracks = []
_tractors = []
_transitions = []


def _get_source_info(path):
    if not GOT_MELT:
        return None

    cmd = '{exe} "{path}" -consumer xml'.format(exe=MELT_BIN, path=path)
    proc = Popen(shlex.split(cmd), stdout=PIPE)
    proc.wait()
    raw_str = re.sub('[\n\r\t]|\s{4}', '', proc.stdout.read())
    raw_data = et.fromstring(raw_str)
    producer_e = raw_data.find('producer')

    global _profile_e
    if _profile_e is None:
        _profile_e = raw_data.find('profile')

    return producer_e


def _pretty_print_xml(root_e):
    tree = minidom.parseString(et.tostring(root_e, 'utf-8'))

    return tree.toprettyxml(indent="    ")


def _create_property(name, value=None):
    property_e = et.Element('property', name=name)
    if value is not None:
        property_e.text = str(value)

    return property_e


def _create_playlist(id):
    return et.Element('playlist', id=id)  # lint:ok


def _producer_lookup(_id):
    if isinstance(_id, otio.core.SerializableObject):
        key = 'title'
        value = _id.name

    else:
        key = 'id'
        value = str(_id)

    for p in iter(_producers):
        if p.attrib[key] == value:
            return p

    return None


def _create_producer(otio_item):
    media_reference = otio_item.media_reference
    url = ''
    _id = 'producer{n}'.format(n=len(_producers))

    if isinstance(media_reference, otio.schema.ExternalReference):
        a_range = otio_item.available_range()

        url = otio_item.media_reference.target_url
        # Some adapters store target_url as, well url but MLT doesn't like it.
        if 'localhost' in url:
            url = url.replace('localhost', '')

        producer_e = _producer_lookup(_id)

        if producer_e is not None:
            return producer_e

    else:
        a_range = otio_item.source_range

    producer_e = et.Element(
                        'producer',
                        id=_id,  # lint:ok
                        title=otio_item.name
                        )

    if not GOT_MELT:
        _in = str(a_range.start_time.value)
        _out = str(a_range.start_time.value + a_range.duration.value - 1)

        producer_e.attrib.update({'in': _in, 'out': _out})
        property_e = _create_property('resource', url)
        producer_e.append(property_e)

    else:
        properties = _get_source_info(url).findall('property')
        producer_e.extend(properties)

    for effect in otio_item.effects:
        if isinstance(effect, otio.schema.TimeEffect):
            url = '{ts}:{url}'.format(ts=effect.time_scalar, url=url)
            property_e.text = url
            producer_e.append(_create_property('mlt_service', 'timewarp'))
            break

    # TODO: Check if oito_item has audio and apply a property for that
    # a_property_e = _create_property('audio_track', num_audio_tracks)
    # prducer_e.append(a_property_e)

    _producers.append(producer_e)

    return producer_e


def _create_entry(producer_id, clip_item):
    if isinstance(clip_item, otio.core.SerializableObject):
        source_range = clip_item.source_range
        inpoint = source_range.start_time.value
        outpoint = inpoint + source_range.duration.value - 1

    else:
        inpoint = int(clip_item.attrib['in'])
        outpoint = int(clip_item.attrib['out'])

    entry_data = {
        'producer': producer_id,
        'in': str(inpoint),
        'out': str(outpoint)
        }
    entry_e = et.Element(
                    'entry',
                    **entry_data
                    )

    return entry_e


def _is_color_producer(producer):
    for prop in producer:
        if 'name' in prop.attrib and prop.attrib['name'] == 'mlt_service':
            return prop.text in ['color', 'colour']

    return False


def _get_transition_type(item_a, item_b=None):
    if isinstance(item_a, otio.schema.Transition):
        _in = item_a.in_offset.value
        _out = item_a.out_offset.value

        if _in and _out:
            return 'dissolve'

        elif _in and not _out:
            return 'fade_out'

        elif not _in and _out:
            return 'fade_in'

    elif item_b is not None:
        if _is_color_producer(item_a):
            return 'fade_in'

        elif _is_color_producer(item_b):
            return 'fade_out'

        elif not _is_color_producer(item_a) and not _is_color_producer(item_b):
            return 'dissolve'

        else:
            return 'unknown'


def _create_color_producer(color, length):
    color_e = _producer_lookup('producer')
    if color_e:
        return color_e

    color_e = et.Element(
                    'producer',
                    title='color',
                    id='producer{n}'.format(n=len(_producers)),
                    **{'in': '0', 'out': str(length - 1)}
                    )
    color_e.append(_create_property('length', length))
    color_e.append(_create_property('eof', 'pause'))
    color_e.append(_create_property('resource', color))
    color_e.append(_create_property('mlt_service', 'color'))
    _producers.append(color_e)

    return color_e


def _create_transition(otio_item, clip_num, track, playlist, audio=False):
    _in = otio_item.in_offset.value
    _out = otio_item.out_offset.value
    _duration = _in + _out

    tractor_e = et.Element(
                    'tractor',
                    id='tractor{n}'.format(n=len(_tractors)),
                    **{'in': '0', 'out': str(_duration - 1)}
                    )

    transition_type = _get_transition_type(otio_item)

    if transition_type == 'dissolve':
        producer_a = _producer_lookup(track[clip_num - 1])
        entry_a = playlist[clip_num - 1]
        next_clip = track[clip_num + 1]

        producer_a_in = int(entry_a.attrib['out']) - _in

        producer_b = _producer_lookup(next_clip)
        if producer_b is None:
            producer_b = _create_producer(track[clip_num + 1])

        producer_b_in = next_clip.source_range.start_time.value

    elif transition_type == 'fade_out':
        prev_clip = track[clip_num - 1]
        producer_a = _producer_lookup(prev_clip)
        producer_a_in = (
            prev_clip.source_range.start_time.value +
            prev_clip.source_range.duration.value
            ) - _in

        producer_b = _create_color_producer('black', _duration)
        producer_b_in = 0

    elif transition_type == 'fade_in':
        producer_a = _create_color_producer('black', _duration)
        producer_a_in = 0

        next_clip = track[clip_num + 1]
        producer_b = _producer_lookup(next_clip)

        if producer_b is None:
            producer_b = _create_producer(next_clip)

        producer_b_in = next_clip.source_range.start_time.value - _in

    track_a_e = et.Element(
        'track',
        producer=producer_a.attrib['id'],
        **{'in': str(producer_a_in), 'out': str(producer_a_in + _duration - 1)}
        )

    tractor_e.append(track_a_e)

    track_b_e = et.Element(
        'track',
        producer=producer_b.attrib['id'],
        **{'in': str(producer_b_in), 'out': str(producer_b_in + _duration - 1)}
        )

    tractor_e.append(track_b_e)

    trans_e = et.Element(
                    'transition',
                    id='transition{n}'.format(n=len(_transitions)),
                    out=str(_duration - 1)
                    )

    trans_e.append(_create_property('a_track', '0'))
    trans_e.append(_create_property('b_track', '1'))
    trans_e.append(_create_property('factory', 'loader'))

    mixer = 'luma'
    if audio:
        mixer = 'mix'
    trans_e.append(_create_property('mlt_service', mixer))

    tractor_e.append(trans_e)
    _tractors.append(tractor_e)

    return tractor_e


def _create_blank(otio_item):
    length = otio_item.duration().value

    return et.Element('blank', length=str(length))


def _create_background_track(input_otio):
    length = int(input_otio.tracks.duration().value)
    bg_e = _create_color_producer('black', length)
    bg_playlist_e = _create_playlist(id='background')

    bg_playlist_e.append(_create_entry(bg_e.attrib['id'], bg_e))
    _playlists.append(bg_playlist_e)

    bg_track_e = et.Element('track', producer=bg_playlist_e.get('id'))
    _tracks.append(bg_track_e)


def _get_track(tractor_id, producer_id):
    tractor = None
    for tractor in _tractors:
        if tractor.attrib['id'] == tractor_id:
            break

    if tractor:
        for track in tractor:
            if track.attrib['producer'] == producer_id:
                return track

    return None


def write_to_string(input_otio, style='mlt'):
    # Check for valid style argument
    if style not in VALID_MLT_STYLES:
        raise otio.exceptions.NotSupportedError(
            "The MLT style '{}' is not supported.".format(
                style
            )
        )

    # Add a black background
    _create_background_track(input_otio)

    # Iterate over tracks
    for tracknum, track in enumerate(input_otio.tracks):
        audio = False
        if track.kind == otio.schema.TrackKind.Audio:
            audio = True

        playlist_e = _create_playlist(
                                id=track.name or 'V{n}'.format(n=tracknum + 1)
                                )

        for clip_num, clip_item in enumerate(track):

            if isinstance(clip_item, otio.schema.Clip):
                producer_e = _producer_lookup(clip_item)
                if producer_e is None:
                    producer_e = _create_producer(clip_item)

                entry_e = _create_entry(producer_e.attrib['id'], clip_item)

                # Check if last item was a transition to compensate inpoint
                if isinstance(track[clip_num - 1], otio.schema.Transition):
                    transition = track[clip_num - 1]
                    transition_type = _get_transition_type(transition)
                    if transition_type in ['fade_in', 'dissolve']:

                        # Get tractor for prev transition
                        tractor_id = playlist_e[-1].attrib['producer']
                        producer_id = producer_e.attrib['id']
                        track_e = _get_track(tractor_id, producer_id)

                        # Trim entry inpoint
                        entry_e.attrib['in'] = str(
                                                int(track_e.attrib['out']) + 1
                                                )

                playlist_e.append(entry_e)

            elif isinstance(clip_item, otio.schema.Gap):
                blank_e = _create_blank(clip_item)
                playlist_e.append(blank_e)

            elif isinstance(clip_item, otio.schema.Transition):
                transition_e = _create_transition(
                                            clip_item,
                                            clip_num,
                                            track,
                                            playlist_e,
                                            audio=audio
                                            )

                # Adjust outpoint of prev element when fading out
                transition_type = _get_transition_type(clip_item)
                if transition_type in ['fade_out', 'dissolve']:
                    adjust = 1
                    if transition_type == 'dissolve':
                        adjust = 0

                    # prev out adjust
                    prev_element = playlist_e[-1]
                    producer_id = prev_element.attrib['producer']
                    tractor_id = transition_e.attrib['id']
                    track_e = _get_track(tractor_id, producer_id)
                    prev_element.attrib['out'] = str(
                                            int(track_e.attrib['in']) - adjust
                                            )

                _transitions.append(transition_e)
                playlist_e.append(
                        _create_entry(transition_e.attrib['id'], transition_e)
                        )

        _playlists.append(playlist_e)

        track_e = et.Element('track', producer=playlist_e.get('id'))
        _tracks.append(track_e)

    # Build XML
    root_e = et.Element('mlt')
    global _profile_e
    if _profile_e is not None:
        root_e.append(_profile_e)

    root_e.extend(_producers)
    root_e.extend(_transitions)
    root_e.extend(_playlists)
    tractor_e = et.SubElement(
                            root_e,
                            'tractor',
                            id='tractor{n}'.format(n=len(_tractors))
                            )
    tractor_e.extend(_tracks)

    return _pretty_print_xml(root_e)


def _get_playlist(playlist_id):
    for playlist in _playlists:
        if playlist_id == playlist.attrib['id']:
            return playlist

    return None


def _add_gap(entry_e, rate):
    _dur = int(entry_e.attrib['length'])

    gap = otio.schema.Gap(
        source_range=otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, rate),
            duration=otio.opentime.RationalTime(_dur, rate)
            )
        )

    return gap


def _get_rate(mlt_e):
    rate = None
    profile_e = mlt_e.find('profile')
    if profile_e:
        fps_num = int(profile_e.attrib['frame_rate_num'])
        fps_den = int(profile_e.attrib['frame_rate_den'])
        rate = round(float(fps_num) / float(fps_den), 2)

    elif _producers:
        for prod in _producers:
            for prop in prod:
                if prop.attrib['name'].endswith('frame_rate'):
                    if prop.text.isdigit():
                        rate = int(prop.text)

                    else:
                        rate = float(prop.text)

                    break

    if rate is None:
        # Fallback to 24 or 1?
        rate = 24

    return rate


def _get_producer(producer_id):
    for producer in _producers:
        if producer_id == producer.attrib['id']:
            return producer

    return None


def _get_tractor(tractor_id):
    for tractor in _tractors:
        if tractor_id == tractor.attrib['id']:
            return tractor

    return None


def _get_media_path(producer_e):
    for prop in producer_e:
        if prop.attrib['name'] == 'resource':
            return prop.text

    return None


def _add_transition(tractor_e, rate):
    track_a, track_b = tractor_e.findall('track')
    producer_a = _get_producer(track_a.attrib['producer'])
    producer_b = _get_producer(track_b.attrib['producer'])
    dur_a = int(track_a.attrib['out']) - int(track_a.attrib['in']) + 1
    dur_b = int(track_b.attrib['out']) - int(track_b.attrib['in']) + 1

    transition_type = _get_transition_type(producer_a, producer_b)

    if transition_type == 'fade_in':
        in_offset = otio.opentime.RationalTime(0, rate)
        out_offset = otio.opentime.RationalTime(dur_b, rate)

    elif transition_type == 'dissolve':
        in_offset = otio.opentime.RationalTime(dur_a // 2, rate)
        out_offset = otio.opentime.RationalTime(dur_b // 2, rate)

    elif transition_type == 'fade_out':
        in_offset = otio.opentime.RationalTime(dur_a, rate)
        out_offset = otio.opentime.RationalTime(0, rate)

    oito_transition = otio.schema.Transition(
                                        in_offset=in_offset,
                                        out_offset=out_offset
                                        )

    return oito_transition


def _add_clip(entry_e, rate):
    _in = int(entry_e.attrib['in'])
    _out = int(entry_e.attrib['out']) + 1
    _duration = _out - _in

    source_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(_in, rate),
        duration=otio.opentime.RationalTime(_duration, rate)
        )

    producer_e = _get_producer(entry_e.attrib['producer'])

    if not 'in' in producer_e.attrib:
        length_e = [p for p in producer_e if p.attrib['name'] == 'length'][-1]
        producer_in = 0
        producer_out = int(length_e.text) + 1
        producer_duration = producer_out - producer_in

    else:
        producer_in = int(producer_e.attrib['in'])
        producer_out = int(producer_e.attrib['out']) + 1
        producer_duration = producer_out - producer_in

    available_range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(producer_in, rate),
        duration=otio.opentime.RationalTime(producer_duration, rate)
        )

    media_reference = otio.schema.ExternalReference(
        target_url=_get_media_path(producer_e),
        available_range=available_range
        )

    clip = otio.schema.Clip(
        name=producer_e.attrib.get('title'),
        source_range=source_range,
        media_reference=media_reference
        )

    return clip


def read_from_string(input_str):
    # Hack to please etree.findall() being picky about indents
    stripped_str = re.sub('^/s+', '', input_str)

    mlt_e = et.fromstring(stripped_str)

    _producers.extend(mlt_e.findall('producer'))
    _tractors.extend(mlt_e.findall('tractor'))
    _playlists.extend(mlt_e.findall('playlist'))

    rate = _get_rate(mlt_e)
    timeline = otio.schema.Timeline()

    # Assume last tracktor is main timeline
    timeline_e = _tractors[-1]

    for track in timeline_e:
        playlist_id = track.attrib['producer']
        otio_track = otio.schema.Track(name=playlist_id)

        playlist_e = _get_playlist(playlist_id)

        if playlist_id == 'background':
            # Ignore background track as it's only useful for mlt
            if len(playlist_e) == 1:
                continue

        for entrynum, entry_e in enumerate(playlist_e):
            if entry_e.tag == 'blank':
                gap = _add_gap(entry_e, rate)
                otio_track.append(gap)

            elif entry_e.tag == 'entry':
                producer_id = entry_e.attrib['producer']
                if 'tractor' in producer_id:
                    tractor_e = _get_tractor(producer_id)
                    transition = _add_transition(tractor_e, rate)

                    otio_track.append(transition)

                    transition_type = _get_transition_type(transition)

                    if entrynum == 0:
                        continue

                    # Adjust source_range if needed
                    prev_item = otio_track[entrynum - 1]
                    if not isinstance(prev_item, otio.schema.Gap):
                        in_offset = transition.in_offset
                        prev_item.source_range.start_time -= in_offset
                        prev_item.source_range.duration += in_offset

                        if transition_type in ['dissolve']:
                            prev_item.source_range.duration += in_offset

                elif 'producer' in producer_id:
                    clip = _add_clip(entry_e, rate)
                    otio_track.append(clip)
                    if entrynum == 0:
                        continue

                    # Adjust source_range if needed
                    prev_item = otio_track[entrynum - 1]
                    if isinstance(prev_item, otio.schema.Transition):
                        in_offset = prev_item.in_offset
                        out_offset = prev_item.out_offset
                        if transition_type != 'fade_in':
                            clip.source_range.start_time -= out_offset
                            clip.source_range.duration += (
                                                    in_offset + out_offset
                                                    )

        timeline.tracks.append(otio_track)

    return timeline
    #TODO Handle exceptions, cleanup etc.
    #TODO Audio, ->OTIO check for audio streams i producer and make parallel
    #TODO  tracks to match video.
    #TODO Audio, ->OTIO when only audio. Create clip in audio track.
    # Create Audio and Video tracks in parallell for producers with two streams
    # properties to look for:
    # meta.media.nb_streams, meta.media.1.stream.type -> video/audio
    # audio_index -1 is not active? 0, 1 stream index
    # video_index -----------"---------------------