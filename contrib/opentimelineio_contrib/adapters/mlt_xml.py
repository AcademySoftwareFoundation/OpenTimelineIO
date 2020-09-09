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

"""
The MLT adapter currently only supports writing simplified mlt xml files
geared towards use with the "melt" command line video editor.
The motivation for writing this adapter was playback of timeline's or
rendering of mini cut's for instance. Not for parsing project files for
applications based on MLT such as kdenlive, Shotcut etc.
There actually is an adapter for kdenlive files available in OTIO.

Therefore, reading of mlt files is not supported at the moment.
This is also partly due to the flexible nature of the MLT format making it a
bit hard to write a solid parser based on etree.

If someone wants to implement parsing/reading of mlt files feel free to do so.
You might want to use the python-mlt bindings available for a more robust
parser, but that adds a third-party dependency to the adapter.

For more info on the MLT visit the website: https://www.mltframework.org/
"""

import opentimelineio as otio
from copy import deepcopy
from xml.dom import minidom
from xml.etree import ElementTree as et

# MLT root tag
root = et.Element('mlt')

# Store media references or clips as producers
producers = {'audio': {}, 'video': {}}

# Store playlists so they appear in order
playlists = []

# Store transitions for indexing
transitions = []


def create_property(name, text=None, attrib=None):
    property_e = et.Element('property', name=name)
    if text is not None:
        property_e.text = str(text)

    if attrib:
        property_e.attrib.update(attrib)

    return property_e


def create_solid(color, length):
    color_e = et.Element(
        'producer',
        title='color',
        id='solid_{c}'.format(c=color),
        attrib={'in': '0', 'out': str(length - 1)}
        )

    color_e.append(create_property('length', length))
    color_e.append(create_property('eof', 'pause'))
    color_e.append(create_property('resource', color))
    color_e.append(create_property('mlt_service', 'color'))

    return color_e


def get_producer(otio_clip, video_track=True):
    target_url = None
    producer_e = None
    is_sequence = False

    if isinstance(otio_clip, (otio.schema.Gap, otio.schema.Transition)):
        # Create a solid producer
        producer_e = create_solid(
            '0x000000FF',
            otio_clip.duration().value
        )

        id_ = producer_e.attrib['id']

        # Add producer here since resource test below will fail.
        producers['video'].setdefault(id_, producer_e)

        # store producer in order list for insertion later
        producers.setdefault('producer_order_', []).append(producer_e)

    else:
        id_ = otio_clip.name

    if hasattr(otio_clip, 'media_reference') and otio_clip.media_reference:
        id_ = otio_clip.media_reference.name or otio_clip.name

        if hasattr(otio_clip.media_reference, 'target_url'):
            target_url = otio_clip.media_reference.target_url

        elif hasattr(otio_clip.media_reference, 'abstract_target_url'):
            is_sequence = True
            target_url = otio_clip.media_reference.abstract_target_url(
                '%0{}d'.format(
                    otio_clip.media_reference.frame_zero_padding
                )
            )
            target_url += '?begin={}'.format(
                otio_clip.media_reference.start_frame
            )

    if producer_e is None:
        producer_e = et.Element(
            'producer',
            id=id_
        )

    sub_key = 'video'
    if not video_track:
        sub_key = 'audio'

    # We keep track of audio and video producers to avoid duplicates
    producer = producers[sub_key].setdefault(
        id_,
        producer_e
    )

    if not target_url:
        target_url = id_

    property_e = producer.find('./property/[@name="resource"]')
    if property_e is None:
        resource = create_property(name='resource', text=target_url)
        producer.append(resource)

        if is_sequence:
            producer.append(create_property(name='mlt_service', text='pixbuf'))

        # store producer in order list for insertion later
        producers.setdefault('producer_order_', []).append(producer)

    return producer


def get_in_out_from_transition(transition):
    in_ = 0
    out_ = 0

    if transition.name == 'kFadeIn':
        in_ = transition.in_offset.value
        out_ = transition.out_offset.value

    elif transition.name == 'kDissolve':
        in_ = transition.in_offset.value
        out_ = transition.out_offset.value

    elif transition.name == 'kFadeOut':
        in_ = transition.out_offset.value
        out_ = transition.in_offset.value

    return in_, out_


def create_transition(trans_track, name):
    item_a, transition, item_b = trans_track

    dur = transition.duration().value - 1

    tractor_e = et.Element(
        'tractor',
        id=name,
        attrib={
            'in': '0',
            'out': str(dur)
        }
    )

    producer_a = get_producer(item_a)
    if isinstance(item_a, otio.schema.Transition):
        a_in, a_out = get_in_out_from_transition(transition)

    else:
        if isinstance(item_b, otio.schema.Gap):
            a_in = 0
            a_out = item_b.duration().value - 1

        else:
            a_in = item_a.trimmed_range().start_time.value
            a_out = a_in + item_a.trimmed_range().duration.value - 1

    track_a = et.Element(
        'track',
        producer=producer_a.attrib['id'],
        attrib={
            'in': str(a_in),
            'out': str(a_out)
        }
    )

    producer_b = get_producer(item_b)
    if isinstance(item_b, otio.schema.Transition):
        b_in, b_out = get_in_out_from_transition(transition)

    else:
        if isinstance(item_b, otio.schema.Gap):
            b_in = 0
            b_out = item_b.duration().value - 1

        else:
            b_in = item_b.trimmed_range().start_time.value
            b_out = b_in + item_b.trimmed_range().duration.value - 1

    track_b = et.Element(
        'track',
        producer=producer_b.attrib['id'],
        attrib={
            'in': str(b_in),
            'out': str(b_out)
        }
    )

    tractor_e.append(track_a)
    tractor_e.append(track_b)

    trans_e = et.Element(
        'transition',
        id='transition_{}'.format(name),
        out=str(dur)
    )
    trans_e.append(create_property('a_track', 0))
    trans_e.append(create_property('b_track', 1))
    trans_e.append(create_property('factory'))
    trans_e.append(create_property('mlt_service', 'luma'))

    tractor_e.append(trans_e)

    return tractor_e


def create_entry(producer, in_, out_):
    clip_e = et.Element(
        'entry',
        producer=producer.attrib['id'],
        attrib={
            'in': str(in_),
            'out': str(out_)
        }
    )

    return clip_e


def create_clip(item, producer):
    in_ = item.trimmed_range().start_time.value
    out_ = in_ + item.trimmed_range().duration.value

    clip_e = create_entry(producer, in_, out_)

    return clip_e


def create_blank(item):
    blank_e = et.Element(
        'blank',
        length=str(item.source_range.duration.value)
    )

    return blank_e


def apply_timewarp(item, item_e, effect):
    if item_e is None:
        return

    orig_producer_e = get_producer(item)
    producer_e = deepcopy(orig_producer_e)
    id_ = None

    if effect.effect_name == 'FreezeFrame':
        id_ = '{}_freeze{}'.format(
            producer_e.attrib['id'],
            item.source_range.start_time.value
        )

        producer_e.attrib['id'] = id_
        producer_e.append(create_property('mlt_service', 'hold'))
        producer_e.append(create_property(
            'frame',
            str(item.source_range.start_time.value))
        )

    elif effect.effect_name == 'LinearTimeWarp':
        id_ = ':'.join([str(effect.time_scalar), item_e.attrib.get('producer')])
        producer_e.attrib['id'] = id_
        producer_e.append(create_property('mlt_service', 'timewarp'))
        resource_e = producer_e.find('./property/[@name="resource"]')
        resource_e.text = ':'.join([str(effect.time_scalar), resource_e.text])

    if id_ not in producers['video']:
        producers['video'][id_] = producer_e
        producers['producer_order_'].append(producer_e)

    item_e.attrib['producer'] = id_


def create_background_track(tracks, parent):
    length = tracks.duration().value
    bg_e = create_solid('black', length)

    # Add producer to list
    producer_e = producers['video'].setdefault(bg_e.attrib['id'], bg_e)

    # store producer in order list for insertion later
    producers.setdefault('producer_order_', []).append(producer_e)

    playlist_e = et.Element(
        'playlist',
        id='background'
    )
    playlists.append(playlist_e)

    playlist_e.append(create_entry(bg_e, 0, length - 1))

    parent.append(
        et.Element('track', producer=playlist_e.attrib['id'])
    )


def assemble_track(track, track_index, parent):
    playlist_e = et.Element(
        'playlist',
        id=track.name or 'playlist{}'.format(track_index)
    )
    playlists.append(playlist_e)

    element_type = 'track'
    if parent.tag == 'playlist':
        element_type = 'entry'

    parent.append(
        et.Element(element_type, producer=playlist_e.attrib['id'])
    )

    # Used to check if we need to add audio elements or not
    is_audio_track = False
    if hasattr(track, 'kind'):
        is_audio_track = track.kind == 'Audio'

    # iterate over items in track
    expanded_track = otio.algorithms.track_with_expanded_transitions(track)
    for item in expanded_track:
        item_e = None

        if isinstance(item, otio.schema.Clip):
            producer_e = get_producer(item)

            if is_audio_track:
                # TODO consider using resource.text
                # Skip adding duplicate audio clips for matching video
                if producer_e.attrib['id'] in producers['video']:
                    continue

            item_e = create_clip(item, producer_e)
            playlist_e.append(item_e)

        elif isinstance(item, otio.schema.Gap):
            item_e = create_blank(item)
            playlist_e.append(item_e)

        elif isinstance(item, tuple):
            transition_e = create_transition(
                item,
                'transition_tractor{}'.format(len(transitions))
            )
            transitions.append(transition_e)

            playlist_e.append(
                et.Element(
                    'entry',
                    producer=transition_e.attrib['id'],
                    attrib={
                        'in': transition_e.attrib['in'],
                        'out': transition_e.attrib['out']
                    }
                )
            )

            # Continue as there's no need to preform the tests below
            continue

        elif 'Stack' in item.schema_name():
            assemble_track(item, track_index, playlist_e)

        # Check for time effects on item
        for effect in item.effects:
            if isinstance(effect, otio.schema.TimeEffect):
                apply_timewarp(item, item_e, effect)


def assemble_timeline(tracks, level=0):
    tractor_e = et.Element('tractor', id='tractor{}'.format(level))
    multitrack_e = et.SubElement(
        tractor_e,
        'multitrack',
        attrib={'id': 'multitrack{}'.format(level)}
    )

    root.append(tractor_e)

    create_background_track(tracks, multitrack_e)

    for track_index, track in enumerate(tracks):
        assemble_track(track, track_index, multitrack_e)


def write_to_string(input_otio):
    if isinstance(input_otio, otio.schema.Timeline):
        tracks = input_otio.tracks

    elif isinstance(input_otio, otio.schema.Track):
        stack = otio.schema.Stack()
        stack.children.append(input_otio)
        tracks = stack.children

    elif isinstance(input_otio, otio.schema.Stack):
        tracks = input_otio.children

    elif isinstance(input_otio, otio.schema.Clip):
        tmp_track = otio.schema.Track()
        tmp_track.append(input_otio)
        stack = otio.schema.Stack()
        stack.children.append(tmp_track)

        tracks = stack.children

    else:
        raise ValueError(
            "Passed OTIO item must be Timeline, Track, Stack or Clip. "
            "Not {}".format(type(input_otio))
        )

    assemble_timeline(tracks)

    # Add producers to root
    for producer in producers['producer_order_']:
        root.insert(0, producer)

    # Add transition tractors
    for transition in transitions:
        root.insert(-1, transition)

    # Add playlists to root
    for playlist in playlists:
        root.insert(-1, playlist)

    tree = minidom.parseString(et.tostring(root, 'utf-8'))

    return tree.toprettyxml(indent="    ")
