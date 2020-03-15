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

"""Kdenlive (MLT XML) Adapter."""
import re
import os
from xml.etree import ElementTree as ET
import opentimelineio as otio
import datetime


def read_property(element, name):
    """Decode an MLT item property
    which value is contained in a "property" XML element
    with matching "name" attribute"""
    return element.findtext("property[@name='{}']".format(name), '')


def time(clock, fps):
    """Decode an MLT time
    which is either a frame count or a timecode string
    after format hours:minutes:seconds.floatpart"""
    hms = [float(x) for x in clock.replace(',', '.').split(':')]
    f = 0
    m = fps if len(hms) > 1 else 1  # no delimiter, it is a frame number
    for x in reversed(hms):
        f = f + x * m
        m = m * 60
    return otio.opentime.RationalTime(round(f, 3), fps)


def read_keyframes(kfstring, rate):
    """Decode MLT keyframes
    which are in a semicolon (;) separated list of time/value pair
    separated by = (linear interp) or ~= (spline) or |= (step)
    becomes a dict with RationalTime keys"""
    return dict((time(t, rate), v)
                for (t, v) in re.findall('([^|~=;]*)[|~]?=([^;]*)', kfstring))


def read_from_string(input_str):
    """Read a Kdenlive project (MLT XML)
    Kdenlive uses a given MLT project layout, similar to Shotcut,
    combining a "main_bin" playlist to organize source media,
    and a "global_feed" tractor for timeline.
    (in Kdenlive 19.x, timeline tracks include virtual sub-track, unused for now)"""
    mlt, byid = ET.XMLID(input_str)
    profile = mlt.find('profile')
    rate = (float(profile.get('frame_rate_num'))
            / float(profile.get('frame_rate_den', 1)))
    timeline = otio.schema.Timeline(
        name=mlt.get('name', 'Kdenlive imported timeline'))

    maintractor = mlt.find("tractor[@global_feed='1']")
    for maintrack in maintractor.findall('track'):
        if maintrack.get('producer') == 'black_track':
            continue
        subtractor = byid[maintrack.get('producer')]
        track = otio.schema.Track(
            name=read_property(subtractor, 'kdenlive:track_name'))
        if bool(read_property(subtractor, 'kdenlive:audio_track')):
            track.kind = otio.schema.TrackKind.Audio
        else:
            track.kind = otio.schema.TrackKind.Video
        for subtrack in subtractor.findall('track'):
            playlist = byid[subtrack.get('producer')]
            for item in playlist.iter():
                if item.tag == 'blank':
                    gap = otio.schema.Gap(
                        duration=time(item.get('length'), rate))
                    track.append(gap)
                elif item.tag == 'entry':
                    producer = byid[item.get('producer')]
                    service = read_property(producer, 'mlt_service')
                    available_range = otio.opentime.TimeRange(
                        start_time=time(producer.get('in'), rate),
                        duration=time(producer.get('out'), rate)
                        - time(producer.get('in'), rate))
                    source_range = otio.opentime.TimeRange(
                        start_time=time(item.get('in'), rate),
                        duration=time(item.get('out'), rate)
                        - time(item.get('in'), rate))
                    # media reference clip
                    reference = None
                    if service in ['avformat', 'avformat-novalidate', 'qimage']:
                        reference = otio.schema.ExternalReference(
                            target_url=read_property(
                                producer, 'kdenlive:originalurl') or
                            read_property(producer, 'resource'),
                            available_range=available_range)
                    elif service == 'color':
                        reference = otio.schema.GeneratorReference(
                            generator_kind='SolidColor',
                            parameters={'color': read_property(producer, 'resource')},
                            available_range=available_range)
                    clip = otio.schema.Clip(
                        name=read_property(producer, 'kdenlive:clipname'),
                        source_range=source_range,
                        media_reference=reference or otio.schema.MissingReference())
                    for effect in item.findall('filter'):
                        kdenlive_id = read_property(effect, 'kdenlive_id')
                        if kdenlive_id in ['fadein', 'fade_from_black',
                                           'fadeout', 'fade_to_black']:
                            clip.effects.append(otio.schema.Effect(
                                effect_name=kdenlive_id,
                                metadata={'duration':
                                          time(effect.get('out'), rate)
                                          - time(effect.get('in',
                                                 producer.get('in')), rate)}))
                        elif kdenlive_id in ['volume', 'brightness']:
                            clip.effects.append(otio.schema.Effect(
                                effect_name=kdenlive_id,
                                metadata={'keyframes': read_keyframes(
                                    read_property(effect, 'level'), rate)}))
                    track.append(clip)
        timeline.tracks.append(track)

    for transition in maintractor.findall('transition'):
        kdenlive_id = read_property(transition, 'kdenlive_id')
        if kdenlive_id == 'wipe':
            timeline.tracks[int(read_property(transition, 'b_track')) - 1].append(
                otio.schema.Transition(
                    transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
                    in_offset=time(transition.get('in'), rate),
                    out_offset=time(transition.get('out'), rate)))

    return timeline


def write_property(element, name, value):
    """Store an MLT property
    value contained in a "property" sub element
    with defined "name" attribute"""
    property = ET.SubElement(element, 'property', {'name': name})
    property.text = value


def clock(time):
    """Encode time to an MLT timecode string
    after format hours:minutes:seconds.floatpart"""
    return str(datetime.timedelta(seconds=time.value / time.rate))


def write_keyframes(kfdict):
    """Build a MLT keyframe string"""
    return ';'.join('{}={}'.format(str(int(t.value))).format(v)
                    for t, v in kfdict.items())


def write_to_string(input_otio):
    """Write a timeline to Kdenlive project
    Re-creating the bin storing all used source clips
    and constructing the tracks"""
    if not isinstance(input_otio, otio.schema.Timeline) and len(input_otio) > 1:
        print('WARNING: Only one timeline supported, using the first one.')
        input_otio = input_otio[0]
    # Project header & metadata
    mlt = ET.Element('mlt', {
        'version': '6.16.0',
        'title': input_otio.name,
        'LC_NUMERIC': 'en_US.UTF-8',
        'producer': 'main_bin'})
    rate = input_otio.duration().rate
    (rate_num, rate_den) = {
        23.98: (24000, 1001),
        29.97: (30000, 1001),
        59.94: (60000, 1001)
    }.get(round(float(rate), 2), (int(rate), 1))
    ET.SubElement(mlt, 'profile', {
        'description': 'HD 1080p {} fps'.format(rate),
        'frame_rate_num': str(rate_num),
        'frame_rate_den': str(rate_den),
        'width': '1920',
        'height': '1080',
        'display_aspect_num': '16',
        'display_aspect_den': '9',
        'sample_aspect_num': '1',
        'sample_aspect_den': '1',
        'colorspace': '709',
        'progressive': '1'})

    # Build media library, indexed by url
    main_bin = ET.Element('playlist', {'id': 'main_bin'})
    write_property(main_bin, 'kdenlive:docproperties.decimalPoint', '.')
    write_property(main_bin, 'kdenlive:docproperties.version', '0.98')
    write_property(main_bin, 'xml_retain', '1')
    media_prod = {}
    for clip in input_otio.each_clip():
        service = None
        resource = None
        if isinstance(clip.media_reference, otio.schema.ExternalReference):
            resource = clip.media_reference.target_url
            service = 'qimage' if os.path.splitext(resource)[1].lower() \
                in ['.png', '.jpg', '.jpeg'] else 'avformat'
        elif isinstance(clip.media_reference, otio.schema.GeneratorReference) \
                and clip.media_reference.generator_kind == 'SolidColor':
            service = 'color'
            resource = clip.media_reference.parameters['color']
        if not (service and resource) or (resource in media_prod.keys()):
            continue
        producer = ET.SubElement(mlt, 'producer', {
            'id': 'producer{}'.format(len(media_prod)),
            'in': clock(clip.media_reference.available_range.start_time),
            'out': clock((clip.media_reference.available_range.start_time +
                          clip.media_reference.available_range.duration))})
        ET.SubElement(main_bin, 'entry',
                      {'producer': 'producer{}'.format(len(media_prod))})
        write_property(producer, 'mlt_service', service)
        write_property(producer, 'resource', resource)
        if clip.name:
            write_property(producer, 'kdenlive:clipname', clip.name)
        media_prod[resource] = producer

    # Substitute source clip to be referred to when meeting an unsupported clip
    unsupported = ET.SubElement(mlt, 'producer',
                                {'id': 'unsupported', 'in': '0', 'out': '10000'})
    write_property(unsupported, 'mlt_service', 'qtext')
    write_property(unsupported, 'family', 'Courier')
    write_property(unsupported, 'fgcolour', '#ff808080')
    write_property(unsupported, 'bgcolour', '#00000000')
    write_property(unsupported, 'text', 'Unsupported clip type')
    ET.SubElement(main_bin, 'entry', {'producer': 'unsupported'})
    mlt.append(main_bin)

    # Background clip
    black = ET.SubElement(mlt, 'producer', {'id': 'black_track'})
    write_property(black, 'resource', 'black')
    write_property(black, 'mlt_service', 'color')

    # Timeline & tracks
    maintractor = ET.Element('tractor', {'global_feed': '1'})
    ET.SubElement(maintractor, 'track', {'producer': 'black_track'})
    track_count = 0
    for track in input_otio.tracks:
        track_count = track_count + 1

        ET.SubElement(maintractor, 'track',
                      {'producer': 'tractor{}'.format(track_count)})
        subtractor = ET.Element('tractor', {'id': 'tractor{}'.format(track_count)})
        write_property(subtractor, 'kdenlive:track_name', track.name)

        ET.SubElement(subtractor, 'track', {
            'producer': 'playlist{}_1'.format(track_count),
            'hide': 'audio' if track.kind == otio.schema.TrackKind.Video
            else 'video'})
        ET.SubElement(subtractor, 'track', {
            'producer': 'playlist{}_2'.format(track_count),
            'hide': 'audio' if track.kind == otio.schema.TrackKind.Video
            else 'video'})
        playlist = ET.SubElement(mlt, 'playlist',
                                 {'id': 'playlist{}_1'.format(track_count)})
        playlist_ = ET.SubElement(mlt, 'playlist',
                                  {'id': 'playlist{}_2'.format(track_count)})
        if track.kind == otio.schema.TrackKind.Audio:
            write_property(subtractor, 'kdenlive:audio_track', '1')
            write_property(playlist, 'kdenlive:audio_track', '1')
            write_property(playlist_, 'kdenlive:audio_track', '1')

        # Track playlist
        for item in track:
            if isinstance(item, otio.schema.Gap):
                ET.SubElement(playlist, 'blank',
                              {'length': clock(item.duration())})
            elif isinstance(item, otio.schema.Clip):
                if isinstance(item.media_reference,
                              otio.schema.MissingReference):
                    resource = 'unhandled_type'
                if isinstance(item.media_reference,
                              otio.schema.ExternalReference):
                    resource = item.media_reference.target_url
                elif isinstance(item.media_reference,
                                otio.schema.GeneratorReference) \
                        and item.media_reference.generator_kind == 'SolidColor':
                    resource = item.media_reference.parameters['color']
                clip_in = item.source_range.start_time
                clip_out = item.source_range.duration + clip_in
                clip = ET.SubElement(playlist, 'entry', {
                    'producer': media_prod[resource].attrib['id']
                    if item.media_reference and
                    not item.media_reference.is_missing_reference
                    else 'unsupported',
                    'in': clock(clip_in), 'out': clock(clip_out)})
                # Clip effects
                for effect in item.effects:
                    kid = effect.effect_name
                    if kid in ['fadein', 'fade_from_black']:
                        filt = ET.SubElement(clip, 'filter', {
                            'in': clock(clip_in),
                            'out': clock(clip_in + effect.metadata['duration'])})
                        write_property(filt, 'kdenlive_id', kid)
                        write_property(filt, 'end', '1')
                        if kid == 'fadein':
                            write_property(filt, 'mlt_service', 'volume')
                            write_property(filt, 'gain', '0')
                        else:
                            write_property(filt, 'mlt_service', 'brightness')
                            write_property(filt, 'start', '0')
                    elif effect.effect_name in ['fadeout', 'fade_to_black']:
                        filt = ET.SubElement(clip, 'filter', {
                            'in': clock(clip_out - effect.metadata['duration']),
                            'out': clock(clip_out)})
                        write_property(filt, 'kdenlive_id', kid)
                        write_property(filt, 'end', '0')
                        if kid == 'fadeout':
                            write_property(filt, 'mlt_service', 'volume')
                            write_property(filt, 'gain', '1')
                        else:
                            write_property(filt, 'mlt_service', 'brightness')
                            write_property(filt, 'start', '1')
                    elif effect.effect_name in ['volume', 'brightness']:
                        filt = ET.SubElement(clip, 'filter')
                        write_property(filt, 'kdenlive_id', kid)
                        write_property(filt, 'mlt_service', kid)
                        write_property(filt, 'level',
                                       write_keyframes(effect.metadata['keyframes']))
            elif isinstance(item, otio.schema.Transition):
                print('Transitions handling to be added')
        mlt.append(subtractor)
    mlt.append(maintractor)

    return ET.tostring(mlt).decode()


if __name__ == '__main__':
    timeline = read_from_string(
        open('tests/sample_data/kdenlive_example.kdenlive', 'r').read())
    print(str(timeline).replace('otio.schema', "\notio.schema"))
    xml = write_to_string(timeline)
    print(str(xml).replace("><", ">\n<"))
