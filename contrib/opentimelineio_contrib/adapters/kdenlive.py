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
import sys
from xml.etree import ElementTree as ET
from xml.dom import minidom
import opentimelineio as otio
try:
    from urllib.parse import urlparse, unquote
except ImportError:
    # Python 2
    from urlparse import urlparse
    from urllib import unquote


def read_property(element, name):
    """Decode an MLT item property
    which value is contained in a "property" XML element
    with matching "name" attribute"""
    return element.findtext("property[@name='{}']".format(name), '')


def time(clock, rate):
    """Decode an MLT time
    which is either a frame count or a timecode string
    after format hours:minutes:seconds.floatpart"""
    hms = [float(x) for x in clock.replace(',', '.').split(':')]
    if len(hms) > 1:
        smh = list(reversed(hms))
        hours = smh[2] if len(hms) > 2 else 0
        mins = smh[1]
        secs = smh[0]
        # unpick the same rounding/flooring from the clock function
        # (N.B.: code from the clock function mimicks what
        # I've seen from the mlt source code.
        # It's technically wrong. Or at least, I believe
        # it's written assuming an integer frame rate)
        f = (
            round(secs * rate)
            + int(mins * 60 * rate)
            + int(hours * 3600 * rate)
        )
    else:
        f = hms[0]
    return otio.opentime.RationalTime(f, rate)


def read_keyframes(kfstring, rate):
    """Decode MLT keyframes
    which are in a semicolon (;) separated list of time/value pair
    separated by = (linear interp) or ~= (spline) or |= (step)
    becomes a dict with RationalTime keys"""
    return dict((str(time(t, rate).value), v)
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
                    available_range = otio.opentime.TimeRange.range_from_start_end_time(
                        start_time=time(producer.get('in'), rate),
                        end_time_exclusive=(
                            time(producer.get('out'), rate)
                            + otio.opentime.RationalTime(1, rate)
                        ),
                    )
                    source_range = otio.opentime.TimeRange.range_from_start_end_time(
                        start_time=time(item.get('in'), rate),
                        end_time_exclusive=(
                            time(item.get('out'), rate)
                            + otio.opentime.RationalTime(1, rate)
                        ),
                    )
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
    frames = time.value
    hours = int(frames / (time.rate * 3600))
    frames -= int(hours * 3600 * time.rate)
    mins = int(frames / (time.rate * 60))
    frames -= int(mins * 60 * time.rate)
    secs = frames / time.rate
    return "%02d:%02d:%06.3f" % (hours, mins, secs)


def write_keyframes(kfdict):
    """Build a MLT keyframe string"""
    return ';'.join('{}={}'.format(t, v)
                    for t, v in kfdict.items())


def write_to_string(input_otio):
    """Write a timeline to Kdenlive project
    Re-creating the bin storing all used source clips
    and constructing the tracks"""
    if not isinstance(input_otio, otio.schema.Timeline) and len(input_otio) > 1:
        print('WARNING: Only one timeline supported, using the first one.')
        input_otio = input_otio[0]
    # Project header & metadata
    mlt = ET.Element(
        'mlt',
        dict(
            version="6.23.0",
            title=input_otio.name,
            LC_NUMERIC="C",
            producer="main_bin",
        ),
    )
    rate = input_otio.duration().rate
    (rate_num, rate_den) = {
        23.98: (24000, 1001),
        29.97: (30000, 1001),
        59.94: (60000, 1001)
    }.get(round(float(rate), 2), (int(rate), 1))
    ET.SubElement(
        mlt, 'profile',
        dict(
            description='HD 1080p {} fps'.format(rate),
            frame_rate_num=str(rate_num),
            frame_rate_den=str(rate_den),
            width='1920',
            height='1080',
            display_aspect_num='16',
            display_aspect_den='9',
            sample_aspect_num='1',
            sample_aspect_den='1',
            colorspace='709',
            progressive='1',
        ),
    )

    # Build media library, indexed by url
    main_bin = ET.Element('playlist', dict(id='main_bin'))
    write_property(main_bin, 'kdenlive:docproperties.decimalPoint', '.')
    write_property(main_bin, 'kdenlive:docproperties.version', '0.98')
    write_property(main_bin, 'xml_retain', '1')

    producer_count = 0

    # Build media library, indexed by url
    main_bin = ET.Element('playlist', dict(id='main_bin'))
    write_property(main_bin, 'kdenlive:docproperties.decimalPoint', '.')
    write_property(main_bin, 'kdenlive:docproperties.version', '0.98')
    write_property(main_bin, 'xml_retain', '1')
    media_prod = {}
    for clip in input_otio.each_clip():
        producer, producer_count = _make_producer(
            producer_count, clip, mlt, rate, media_prod
        )
        if producer is not None:
            producer_id = producer.get('id')
            kdenlive_id = read_property(producer, 'kdenlive:id')
            entry_in = producer.get('in')
            entry_out = producer.get('out')
            entry = ET.SubElement(
                main_bin, 'entry',
                {
                    'producer': producer_id,
                    'in': entry_in,
                    'out': entry_out,
                },
            )
            write_property(entry, 'kdenlive:id', kdenlive_id)

    # Substitute source clip to be referred to when meeting an unsupported clip
    unsupported = ET.SubElement(
        mlt, 'producer',
        {
            'id': 'unsupported',
            'in': '0',
            'out': '10000',
        },
    )
    write_property(unsupported, 'mlt_service', 'qtext')
    write_property(unsupported, 'family', 'Courier')
    write_property(unsupported, 'fgcolour', '#ff808080')
    write_property(unsupported, 'bgcolour', '#00000000')
    write_property(unsupported, 'text', 'Unsupported clip type')
    write_property(unsupported, 'kdenlive:id', '3')

    entry = ET.SubElement(
        main_bin, 'entry',
        dict(producer='unsupported'),
    )
    write_property(entry, 'kdenlive:id', '3')

    mlt.append(main_bin)

    # Background clip
    black = ET.SubElement(mlt, 'producer', {'id': 'black_track'})
    write_property(black, 'resource', 'black')
    write_property(black, 'mlt_service', 'color')

    # Timeline & tracks
    maintractor = ET.Element('tractor', {'global_feed': '1'})
    ET.SubElement(maintractor, 'track', {'producer': 'black_track'})

    for i, track in enumerate(input_otio.tracks):
        is_audio = track.kind == otio.schema.TrackKind.Audio

        tractor_id = 'tractor{}'.format(i)
        subtractor = ET.Element('tractor', dict(id=tractor_id))
        write_property(subtractor, 'kdenlive:track_name', track.name)

        ET.SubElement(
            maintractor, 'track', dict(producer=tractor_id)
        )

        playlist = _make_playlist(
            2 * i,
            "video" if is_audio else "audio",
            subtractor,
            mlt,
        )
        dummy_playlist = _make_playlist(2 * i + 1, "both", subtractor, mlt)

        if is_audio:
            write_property(subtractor, 'kdenlive:audio_track', '1')
            write_property(playlist, 'kdenlive:audio_track', '1')

        # Track playlist
        for item in track:
            if isinstance(item, otio.schema.Gap):
                ET.SubElement(
                    playlist, 'blank', dict(length=clock(item.duration()))
                )
            elif isinstance(item, otio.schema.Clip):
                producer_id = "unsupported"
                reset_range = otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(0),
                    duration=item.source_range.duration,
                )
                clip_in = reset_range.start_time
                clip_out = reset_range.end_time_inclusive()
                kdenlive_id = "3"
                if isinstance(item.media_reference,
                              otio.schema.ExternalReference):
                    key = _prod_key_from_item(item, is_audio)
                    producer_id, kdenlive_id = media_prod[
                        key
                    ]
                    speed = key[2]
                    if speed is None:
                        speed = 1
                    source_range = otio.opentime.TimeRange(
                        otio.opentime.RationalTime(
                            item.source_range.start_time.value / speed,
                            item.source_range.start_time.rate,
                        ),
                        item.source_range.duration,
                    )
                    clip_in = source_range.start_time
                    clip_out = source_range.end_time_inclusive()
                elif (
                    isinstance(item.media_reference,
                               otio.schema.GeneratorReference)
                    and item.media_reference.generator_kind == 'SolidColor'
                ):
                    producer_id, kdenlive_id = media_prod[
                        (
                            "color",
                            item.media_reference.parameters['color'],
                            None,
                            None,
                        )
                    ]

                entry = ET.SubElement(
                    playlist, 'entry',
                    {
                        'producer': producer_id,
                        'in': clock(clip_in),
                        'out': clock(clip_out),
                    },
                )
                write_property(entry, 'kdenlive:id', kdenlive_id)

                # Clip effects
                for effect in item.effects:
                    kid = effect.effect_name
                    if kid in ['fadein', 'fade_from_black']:
                        filt = ET.SubElement(
                            entry, 'filter',
                            {
                                "in": clock(clip_in),
                                "out": clock(clip_in + effect.metadata['duration']),
                            },
                        )
                        write_property(filt, 'kdenlive_id', kid)
                        write_property(filt, 'end', '1')
                        if kid == 'fadein':
                            write_property(filt, 'mlt_service', 'volume')
                            write_property(filt, 'gain', '0')
                        else:
                            write_property(filt, 'mlt_service', 'brightness')
                            write_property(filt, 'start', '0')
                    elif effect.effect_name in ['fadeout', 'fade_to_black']:
                        filt = ET.SubElement(
                            entry, 'filter',
                            {
                                "in": clock(clip_out - effect.metadata['duration']),
                                "out": clock(clip_out),
                            },
                        )
                        write_property(filt, 'kdenlive_id', kid)
                        write_property(filt, 'end', '0')
                        if kid == 'fadeout':
                            write_property(filt, 'mlt_service', 'volume')
                            write_property(filt, 'gain', '1')
                        else:
                            write_property(filt, 'mlt_service', 'brightness')
                            write_property(filt, 'start', '1')
                    elif effect.effect_name in ['volume', 'brightness']:
                        filt = ET.SubElement(entry, 'filter')
                        write_property(filt, 'kdenlive_id', kid)
                        write_property(filt, 'mlt_service', kid)
                        write_property(filt, 'level',
                                       write_keyframes(effect.metadata['keyframes']))

            elif isinstance(item, otio.schema.Transition):
                print('Transitions handling to be added')

        mlt.extend((playlist, dummy_playlist, subtractor))

    mlt.append(maintractor)

    return minidom.parseString(ET.tostring(mlt)).toprettyxml(
        encoding=sys.getdefaultencoding(),
    ).decode(sys.getdefaultencoding())


def _make_playlist(count, hide, subtractor, mlt):
    playlist_id = 'playlist{}'.format(count)
    playlist = ET.Element(
        'playlist',
        dict(id=playlist_id),
    )
    ET.SubElement(
        subtractor, 'track',
        dict(
            producer=playlist_id,
            hide=hide,
        ),
    )
    return playlist


def _decode_media_reference_url(url):
    return unquote(urlparse(url).path)


def _make_producer(count, item, mlt, frame_rate, media_prod, speed=None, is_audio=None):
    producer = None
    service, resource, effect_speed, _ = _prod_key_from_item(item, is_audio)
    if service and resource:
        producer_id = "producer{}".format(count)
        kdenlive_id = str(count + 4)  # unsupported starts with id 3

        key = (service, resource, speed, is_audio)
        # check not already in our library
        if key not in media_prod:
            # add ids to library
            media_prod[key] = producer_id, kdenlive_id
            producer = ET.SubElement(
                mlt, 'producer',
                {
                    'id': producer_id,
                    'in': clock(item.media_reference.available_range.start_time),
                    'out': clock(
                        item.media_reference.available_range.end_time_inclusive()
                    ),
                },
            )
            write_property(producer, 'global_feed', '1')
            duration = item.media_reference.available_range.duration.rescaled_to(
                frame_rate
            )
            if speed is not None:
                kdenlive_id = media_prod[(service, resource, None, None)][1]
                write_property(producer, 'mlt_service', "timewarp")
                write_property(producer, 'resource', ":".join((str(speed), resource)))
                write_property(producer, 'warp_speed', str(speed))
                write_property(producer, 'warp_resource', resource)
                write_property(producer, 'warp_pitch', "0")
                write_property(producer, 'set.test_audio', "0" if is_audio else "1")
                write_property(producer, 'set.test_image', "1" if is_audio else "0")
                start_time = otio.opentime.RationalTime(
                    round(
                        item.media_reference.available_range.start_time.value
                        / speed
                    ),
                    item.media_reference.available_range.start_time.rate,
                )
                duration = otio.opentime.RationalTime(
                    round(duration.value / speed),
                    duration.rate,
                )
                producer.set(
                    "out",
                    clock(
                        otio.opentime.TimeRange(
                            start_time,
                            duration,
                        ).end_time_inclusive()
                    ),
                )
            else:
                write_property(producer, 'mlt_service', service)
                write_property(producer, 'resource', resource)
                if item.name:
                    write_property(producer, 'kdenlive:clipname', item.name)
            write_property(
                producer, 'length',
                str(int(duration.value)),
            )
            write_property(producer, 'kdenlive:id', kdenlive_id)

            count += 1

        # create time warped version
        if speed is None and effect_speed is not None:
            # Make video resped producer
            _, count = _make_producer(
                count, item, mlt, frame_rate, media_prod, effect_speed, False
            )
            # Make audio resped producer
            _, count = _make_producer(
                count, item, mlt, frame_rate, media_prod, effect_speed, True
            )

    return producer, count


def _prod_key_from_item(item, is_audio):
    service = None
    resource = None
    speed = None
    if isinstance(
        item.media_reference,
        (otio.schema.ExternalReference, otio.schema.MissingReference),
    ):
        if isinstance(item.media_reference, otio.schema.ExternalReference):
            resource = _decode_media_reference_url(item.media_reference.target_url)
        elif isinstance(item.media_reference, otio.schema.MissingReference):
            resource = item.name

        ext_lower = os.path.splitext(resource)[1].lower()
        if ext_lower == ".kdenlive":
            service = "xml"
        elif ext_lower in (
            ".png", ".jpg", ".jpeg"
        ):
            service = "qimage"
        else:
            service = "avformat-novalidate"

        for effect in item.effects:
            if isinstance(effect, otio.schema.LinearTimeWarp):
                if speed is None:
                    speed = 1
                speed *= effect.time_scalar
    elif (
        isinstance(item.media_reference, otio.schema.GeneratorReference)
        and item.media_reference.generator_kind == 'SolidColor'
    ):
        service = 'color'
        resource = item.media_reference.parameters['color']
    return service, resource, speed, None if speed is None else is_audio


if __name__ == '__main__':
    timeline = read_from_string(
        open('tests/sample_data/kdenlive_example.kdenlive', 'r').read())
    print(str(timeline).replace('otio.schema', "\notio.schema"))
    xml = write_to_string(timeline)
    print(str(xml))
