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

from xml.dom import minidom
from xml.etree import cElementTree as et

import opentimelineio as otio


# Holders of elements
_producers = []
_playlists = []
_tracks = []
_tractors = []
_transitions = []


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

    _in = str(a_range.start_time.value)
    _out = str(a_range.start_time.value + a_range.duration.value - 1)

    producer_e = et.Element(
                        'producer',
                        id=_id,  # lint:ok
                        title=otio_item.name,
                        **{
                            'in': _in,
                            'out': _out
                            }
                        )

    property_e = _create_property('resource', url)
    producer_e.append(property_e)

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


def _get_transition_type(otio_item):
    if otio_item.in_offset.value and otio_item.out_offset.value:
        return 'dissolve'

    elif otio_item.in_offset.value and not otio_item.out_offset.value:
        return 'fade_in'

    elif otio_item.out_offset.value and not otio_item.in_offset.value:
        return 'fade_out'


def _create_color_producer(color, length):
    black_e = _producer_lookup('producer')
    if black_e:
        return black_e

    black_e = et.Element(
                    'producer',
                    title='color',
                    id='producer{n}'.format(n=len(_producers)),
                    **{'in': '0', 'out': str(length - 1)}
                    )
    black_e.append(_create_property('resource', color))
    black_e.append(_create_property('mlt_service', 'color'))
    _producers.append(black_e)

    return black_e


def _create_transition(otio_item, clip_num, track, playlist):
    _in = otio_item.in_offset.value
    _out = otio_item.out_offset.value
    _duration = _in + _out

    tractor_e = et.Element(
                    'tractor',
                    id='tractor{n}'.format(n=len(_tractors)),
                    **{
                        'in': '0',
                        'out': str(_duration - 1)
                        }
                    )

    transition_type = _get_transition_type(otio_item)

    if transition_type == 'dissolve':
        producer_a = _producer_lookup(track[clip_num - 1])
        entry_a = playlist[clip_num - 1]
        next_clip = track[clip_num + 1]

        producer_a_in = int(entry_a.attrib['out']) - _duration

        producer_b = _producer_lookup(next_clip)
        if producer_b is None:
            producer_b = _create_producer(track[clip_num + 1])

        producer_b_in = next_clip.source_range.start_time.value

    elif transition_type == 'fade_in':
        producer_b = _create_color_producer('#00000000', _duration)
        producer_b_in = 0

        prev_clip = track[clip_num - 1]
        producer_a = _producer_lookup(prev_clip)
        producer_a_in = prev_clip.source_range.start_time.value

    elif transition_type == 'fade_out':
        next_clip = track[clip_num + 1]
        producer_b = _producer_lookup(next_clip)
        producer_b_in = (
            next_clip.source_range.start_time.value +
            next_clip.source_range.duration.value
            ) - _duration

        if producer_b is None:
            producer_b = _create_producer(track[clip_num + 1])

        producer_a = _create_color_producer('#00000000', _duration)
        producer_a_in = 0

    track_a_e = et.Element(
                        'track',
                        producer=producer_a.attrib['id'],
                        **{
                            'in': str(producer_a_in),
                            'out': str(producer_a_in + _duration - 1)
                            }
                        )
    tractor_e.append(track_a_e)
    track_b_e = et.Element(
                        'track',
                        producer=producer_b.attrib['id'],
                        **{
                            'in': str(producer_b_in),
                            'out': str(producer_b_in + _duration - 1)
                            }
                        )
    tractor_e.append(track_b_e)

    trans_e = et.Element(
                    'transition',
                    id='transition{n}'.format(n=len(_transitions)),  # lint:ok
                    out=str(_duration)
                    )

    trans_e.append(_create_property('a_track', '0'))
    trans_e.append(_create_property('b_track', '1'))
    trans_e.append(_create_property('factory', 'loader'))
    trans_e.append(_create_property('mlt_service', 'luma'))

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


def write_to_string(input_otio):
    # Add a black background
    _create_background_track(input_otio)

    # Iterate over tracks
    for tracknum, track in enumerate(input_otio.tracks):
        # TODO Figure out how to handle audio tracks
        if track.kind == otio.schema.TrackKind.Audio:
            continue

        playlist_e = _create_playlist(
                                id=track.name or 'V{n}'.format(n=tracknum + 1)
                                )

        for clip_num, clip_item in enumerate(track):

            if isinstance(clip_item, otio.schema.Clip):
                producer_e = _producer_lookup(clip_item)
                if producer_e is None:
                    producer_e = _create_producer(clip_item)

                entry_e = _create_entry(producer_e.attrib['id'], clip_item)

                # Compensate for trasition
                if clip_num > 0:
                    prev_element = playlist_e[-1]
                    if prev_element.tag not in ['blank']:
                        if 'tractor' in prev_element.attrib['producer']:
                            trans_e = prev_element
                            old_in = int(entry_e.attrib['in'])
                            entry_e.attrib['in'] = str(
                                                old_in +
                                                int(trans_e.attrib['out']) + 1
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
                                            playlist_e
                                            )
                # Adjust in/out points to compensate for transition
                if not clip_num == 0:
                    prev_element = playlist_e[-1]
                    if prev_element.tag not in ['blank']:
                        old_out = int(prev_element.attrib['out'])
                        playlist_e[-1].attrib['out'] = str(
                                            old_out -
                                            int(transition_e.attrib['out']) - 1
                                            )

                _transitions.append(transition_e)
                playlist_e.append(
                        _create_entry(transition_e.attrib['id'], transition_e)
                        )

        _playlists.append(playlist_e)

        track_e = et.Element('track', producer=playlist_e.get('id'))
        _tracks.append(track_e)

    root_e = et.Element('mlt')
    if 'resolution' in input_otio.metadata:
        root_e.attrib.update(input_otio.metadata['resolution'])

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
