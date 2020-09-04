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


def create_color_producer(color, length):
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
    if isinstance(otio_clip, (otio.schema.Gap, otio.schema.Transition)):
        # Create a solid producer
        producer_e = create_color_producer('black', otio_clip.duration().value)

        id_ = producer_e.attrib['id']

    else:
        id_ = otio_clip.name

    if hasattr(otio_clip, 'media_reference') and otio_clip.media_reference:
        id_ = otio_clip.media_reference.name or otio_clip.name

        if hasattr(otio_clip.media_reference, 'target_url'):
            target_url = otio_clip.media_reference.target_url

        elif hasattr(otio_clip.media_reference, 'abstract_target_url'):
            target_url = otio_clip.media_reference.abstract_target_url(
                '%0{}d'.format(otio_clip.media_reference.frame_zero_padding)
            )

    sub_key = 'video'
    if not video_track:
        sub_key = 'audio'

    if producer_e is None:
        producer_e = et.Element(
            'producer',
            id=id_
        )

    producer = producers[sub_key].setdefault(
        id_,
        producer_e
    )

    if not target_url:
        target_url = id_

    property_e = producer.find('./property/[@name="resource"]')
    if property_e is None:
        resource = et.Element('property', name='resource')
        resource.text = target_url

        producer.append(resource)

        # store producer in order list for insertion later
        producers.setdefault('producer_order_', []).append(producer)

    return producer


def create_transition(trans_track, name):
    # <tractor id="tractor0" in="0" out="24">
    #   <track producer="producer0" in="115" out="139"/>
    #   <track producer="producer1" in="0" out="24"/>
    #   <transition id="transition0" out="24">
    #     <property name="a_track">0</property>
    #     <property name="b_track">1</property>
    #     <property name="factory">loader</property>
    #     <property name="mlt_service">luma</property>
    #   </transition>
    # </tractor>

    dur = sum(map(lambda i: i.duration().value, trans_track))
    tractor_e = et.Element(
        'tractor',
        id=name,
        attrib={
            'in': '0',
            'out': str(dur)
        }
    )
    item_a, transition, item_b = trans_track
    # item_a = trans_track[0]
    producer_a = get_producer(item_a)
    if isinstance(item_a, otio.schema.Transition):
        a_in = 0
        a_out = item_a.in_offset.value - 1

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

    # item_b = trans_track[-1]
    producer_b = get_producer(item_b)
    if isinstance(item_b, otio.schema.Transition):
        b_in = 0
        b_out = item_b.out_offset.value

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


def create_clip(item, producer):
    in_ = item.trimmed_range().start_time.value
    out_ = in_ + item.trimmed_range().duration.value

    clip_e = et.Element(
        'entry',
        producer=producer.attrib['id'],
        attrib={
            'in': str(in_),
            'out': str(out_)
        }
    )

    return clip_e


def create_blank(item):
    blank_e = et.Element(
        'blank',
        length=str(item.source_range.duration.value)
    )

    return blank_e


def assemble_track(track, track_index, parent):
    playlist_e = et.Element(
        'playlist',
        id=track.name or 'playlist{}'.format(track_index)
    )
    playlists.append(playlist_e)

    parent.append(
        et.Element('track', producer=playlist_e.attrib['id'])
    )

    # Used to check if we need to add audio elements or not
    is_audio_track = False
    if hasattr(track, 'kind'):
        is_audio_track = track.kind == 'Audio'

    # iterate over itmes in track
    expanded_track = otio.algorithms.track_with_expanded_transitions(track)
    for item in expanded_track:
        if isinstance(item, otio.schema.Clip):
            producer_e = get_producer(item)

            if is_audio_track:
                # TODO consider using resource.text
                # Skip adding duplicate audio clips for matching video
                if producer_e.attrib['id'] in producers['video']:
                    continue

            clip_e = create_clip(item, producer_e)
            playlist_e.append(clip_e)

        elif isinstance(item, otio.schema.Gap):
            blank_e = create_blank(item)
            playlist_e.append(blank_e)

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


def assemble_timeline(tracks, level=0):
    tractor_e = et.Element('tractor', id='tractor0')
    multitrack_e = et.SubElement(
        tractor_e,
        'multitrack',
        attrib={'id': 'multitrack{}'.format(level)}
    )

    root.append(tractor_e)

    for track_index, track in enumerate(tracks):
        assemble_track(track, track_index, multitrack_e)


def write_to_string(input_otio):
    if isinstance(input_otio, otio.schema.Timeline):
        tracks = input_otio.tracks

    elif isinstance(input_otio, otio.schema.Track, otio.schema.Stack):
        tracks = [input_otio]

    elif isinstance(input_otio, otio.schema.Clip):
        tmp_track = otio.schema.Track()
        tmp_track.append(input_otio)

        tracks = [tmp_track]

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
