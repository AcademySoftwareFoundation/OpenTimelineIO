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

import unittest
from xml.etree import ElementTree as et

import opentimelineio as otio
from opentimelineio.exceptions import AdapterDoesntSupportFunctionError


class TestMLTAdapter(unittest.TestCase):
    def test_single_clip(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            )
        )

        tree = et.fromstring(otio.adapters.write_to_string(clip1, 'mlt_xml'))
        producer_e = tree.find('./producer/[@id="{}"]'.format(clip1.name))

        self.assertIsNotNone(producer_e)
        self.assertEqual(producer_e.attrib['id'], clip1.name)

        playlist_e = tree.find('./playlist/[@id="playlist0"]')
        entry_e = playlist_e.find('./entry/[@producer="{}"]'.format(clip1.name))

        self.assertEqual(entry_e.attrib['producer'], clip1.name)
        self.assertEqual(
            float(entry_e.attrib['in']),
            clip1.source_range.start_time.value
        )
        self.assertEqual(
            float(entry_e.attrib['out']),
            clip1.source_range.end_time_inclusive().value
        )

    def test_single_track(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            )
        )

        track = otio.schema.Track('video1')
        track.append(clip1)

        tree = et.fromstring(otio.adapters.write_to_string(track, 'mlt_xml'))
        producer_e = tree.find('./producer/[@id="{}"]'.format(clip1.name))

        self.assertIsNotNone(producer_e)
        self.assertEqual(producer_e.attrib['id'], clip1.name)

        playlist_e = tree.find('./playlist/[@id="video1"]')
        self.assertIsNotNone(playlist_e)

        entry_e = playlist_e.find('./entry/[@producer="{}"]'.format(clip1.name))
        self.assertEqual(entry_e.attrib['producer'], clip1.name)
        self.assertEqual(
            float(entry_e.attrib['in']),
            clip1.source_range.start_time.value
        )
        self.assertEqual(
            float(entry_e.attrib['out']),
            clip1.source_range.end_time_inclusive().value
        )

    def test_pass_unsupported_object(self):
        stack = otio.schema.Stack('stack1')

        with self.assertRaises(ValueError) as err:
            et.fromstring(otio.adapters.write_to_string(stack, 'mlt_xml'))

        self.assertEqual(
            "Passed OTIO item must be Timeline, Track or Clip. "
            "Not {}".format(type(stack)),
            str(err.exception)
        )

    def test_external_reference(self):
        path = '/some/path/to/media_file.mov'
        clip_with_media_ref = otio.schema.Clip(
            name='clip_with_media_ref',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url=path,
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 30),
                    otio.opentime.RationalTime(100, 30)
                )
            )
        )

        clip2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            )
        )

        track = otio.schema.Track()
        track.append(clip_with_media_ref)
        track.append(clip2)

        tree = et.fromstring(otio.adapters.write_to_string(track, 'mlt_xml'))

        producer1_e = tree.find(
            './producer/[@id="{}"]'.format(clip_with_media_ref.name)
        )
        property_text = producer1_e.findtext('property', path)
        self.assertIsNotNone(property_text)
        self.assertEqual(float(producer1_e.attrib['in']), 0)
        self.assertEqual(float(producer1_e.attrib['out']), 99)

        # Producers with no external reference get clip.name as "path"
        producer2_e = tree.find('./producer/[@id="{}"]'.format(clip2.name))
        property2_text = producer2_e.findtext('property', clip2.name)
        self.assertIsNotNone(property2_text)
        self.assertIsNone(producer2_e.attrib.get('in'))
        self.assertIsNone(producer2_e.attrib.get('out'))

    def test_image_sequence(self):
        clip1 = otio.schema.Clip(
            name='imageseq',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(10, 30),
                otio.opentime.RationalTime(80, 30)
            ),
            media_reference=otio.schema.ImageSequenceReference(
                target_url_base='/path/to/files/',
                name_prefix='image.',
                start_frame=1001,
                frame_zero_padding=4,
                frame_step=1,
                name_suffix='.png',
                rate=30,
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 30),
                    otio.opentime.RationalTime(100, 30)
                )
            )
        )
        track = otio.schema.Track('images')
        track.append(clip1)

        tree = et.fromstring(otio.adapters.write_to_string(track, 'mlt_xml'))

        producer_e = tree.find('./producer/[@id="imageseq"]')
        self.assertIsNotNone(producer_e)

        abstract_url = '/path/to/files/image.%04d.png?begin=1001'
        self.assertEqual(
            producer_e.find('./property/[@name="resource"]').text,
            abstract_url
        )
        self.assertEqual(
            producer_e.find('./property/[@name="mlt_service"]').text,
            'pixbuf'
        )

    def test_de_duplication_of_producers(self):
        clipname = 'clip'
        clip1 = otio.schema.Clip(
            name=clipname,
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            )
        )

        clip2 = otio.schema.Clip(
            name=clipname,
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            )
        )

        same_but_different_name = 'clip1'
        clip3 = otio.schema.Clip(
            name=same_but_different_name,
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url='/path/one/to/clip.mov'
            )
        )

        clip4 = otio.schema.Clip(
            name=same_but_different_name,
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url='/path/two/to/clip.mov'
            )
        )
        clip5 = otio.schema.Clip(
            name=same_but_different_name,
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url='/path/two/to/clip.mov'
            )
        )

        track = otio.schema.Track()
        track.append(clip1)
        track.append(clip2)
        track.append(clip3)
        track.append(clip4)
        track1 = otio.schema.Track('audio1', kind=otio.schema.TrackKind.Audio)
        track1.append(clip5)

        timeline = otio.schema.Timeline()
        timeline.tracks.append(track)
        timeline.tracks.append(track1)

        tree = et.fromstring(otio.adapters.write_to_string(timeline, 'mlt_xml'))

        producers_noref = tree.findall('./producer/[@id="{}"]'.format(clipname))
        self.assertEqual(len(producers_noref), 1)

        producers_ref = tree.findall(
            './producer/[@id="{}"]'.format(same_but_different_name)
        )

        self.assertEqual(len(producers_ref), 2)
        self.assertEqual(
            producers_ref[0].attrib['id'],
            producers_ref[1].attrib['id']
        )
        self.assertIsNotNone(
            tree.findtext('property', '/path/one/to/clip.mov')
        )
        self.assertIsNotNone(
            tree.findtext('property', '/path/two/to/clip.mov')
        )

    def test_timeline_with_tracks(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        clip2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        clip3 = otio.schema.Clip(
            name='clip3',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        gap1 = otio.schema.Gap(
            name='gap1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        gap2 = otio.schema.Gap(
            name='gap2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        timeline = otio.schema.Timeline()
        track1 = otio.schema.Track('video1')
        track2 = otio.schema.Track('video2')
        timeline.tracks.append(track1)
        timeline.tracks.append(track2)

        track1.append(clip1)
        track1.append(gap1)
        track1.append(clip2)

        track2.append(gap2)
        track2.append(clip3)

        tree = et.fromstring(
            otio.adapters.write_to_string(timeline, 'mlt_xml')
        )

        playlists = tree.findall('./playlist')
        tracks = tree.findall('./tractor/multitrack/track')

        # Check for background and the two tracks == 3
        self.assertEqual(len(playlists), 3)
        self.assertEqual(len(tracks), 3)

        track1_e = tree.find('./playlist/[@id="video1"]')

        self.assertEqual(track1_e[0].attrib['producer'], clip1.name)
        self.assertEqual(
            float(track1_e[0].attrib['in']),
            clip1.source_range.start_time.value
        )
        self.assertEqual(
            float(track1_e[0].attrib['out']),
            clip1.source_range.end_time_inclusive().value
        )
        self.assertEqual(track1_e[1].tag, 'blank')
        self.assertEqual(
            float(track1_e[1].attrib['length']),
            gap1.duration().value
        )
        self.assertEqual(track1_e[2].attrib['producer'], clip2.name)
        self.assertEqual(
            float(track1_e[2].attrib['in']),
            clip2.source_range.start_time.value
        )
        self.assertEqual(
            float(track1_e[2].attrib['out']),
            clip2.source_range.end_time_inclusive().value
        )

        track2_e = tree.find('./playlist/[@id="video2"]')
        self.assertEqual(track2_e[0].tag, 'blank')
        self.assertEqual(
            float(track2_e[0].attrib['length']),
            gap2.duration().value
        )
        self.assertEqual(track2_e[1].attrib['producer'], clip3.name)
        self.assertEqual(
            float(track2_e[1].attrib['in']),
            clip3.source_range.start_time.value
        )
        self.assertEqual(
            float(track2_e[1].attrib['out']),
            clip3.source_range.end_time_inclusive().value
        )

    def test_nested_timeline(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        clip2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        timeline1 = otio.schema.Timeline(name='timeline1')
        track1 = otio.schema.Track('video1')
        track1.append(clip1)
        timeline1.tracks.append(track1)

        nested_stack = otio.schema.Stack(name='nested')
        nested_stack.append(clip2)

        track1.append(nested_stack)

        tree = et.fromstring(
            otio.adapters.write_to_string(timeline1, 'mlt_xml')
        )

        playlists = tree.findall('./playlist')
        self.assertEqual(len(playlists), 3)

        nested = tree.find('.playlist/[@id="nested"]')
        nested_clip = nested[0]

        self.assertIsNotNone(nested)
        self.assertEqual(
            float(nested_clip.attrib['out']),
            clip2.source_range.end_time_inclusive().value
        )

        tracks = tree.findall('./tractor/multitrack/track')
        self.assertEqual(tracks[0].attrib['producer'], 'background')
        self.assertEqual(tracks[1].attrib['producer'], 'video1')

        self.assertIsNotNone(nested.find('./entry/[@producer="clip2"]'))

        # Future support for effects applied to nested tracks
        # nested_example_path = os.path.abspath(
        #     os.path.join(
        #         '..',
        #         '..',
        #         '..',
        #         'tests',
        #         'sample_data',
        #         'nested_example.otio'
        #     )
        # )
        #
        # t = otio.adapters.read_from_file(nested_example_path)
        # tree = et.fromstring(
        #     otio.adapters.write_to_string(t, 'mlt_xml')
        # )
        # print et.tostring(tree)

    def test_video_fade_in(self):
        # beginning of timeline
        fade_in1 = otio.schema.Transition(
            name='fadeIn',
            in_offset=otio.opentime.RationalTime(0, 30),
            out_offset=otio.opentime.RationalTime(30, 30)
        )

        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        track1 = otio.schema.Track('faded_beginning')
        track1.append(fade_in1)
        track1.append(clip1)

        tree = et.fromstring(
            otio.adapters.write_to_string(track1, 'mlt_xml')
        )

        tractor1_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            float(tractor1_e.attrib['out']),
            fade_in1.out_offset.value - 1
        )
        self.assertIsNotNone(tractor1_e)

        tracks1 = tractor1_e.findall('./track')
        self.assertEqual(tracks1[0].attrib['producer'], 'solid_black')
        self.assertEqual(
            tracks1[1].attrib['producer'],
            'clip1_transition_post'
        )

        playlist1_e = tree.find('./playlist/[@id="faded_beginning"]')
        self.assertIsNotNone(playlist1_e)
        self.assertEqual(
            playlist1_e[0].attrib['producer'],
            'transition_tractor0'
        )
        self.assertEqual(
            playlist1_e[1].attrib['producer'],
            'clip1'
        )
        self.assertEqual(
            float(playlist1_e[1].attrib['in']),
            30
        )

        # further in
        gap1 = otio.schema.Gap(
            name='gap1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        fade_in2 = otio.schema.Transition(
            name='fadeIn',
            in_offset=otio.opentime.RationalTime(0, 30),
            out_offset=otio.opentime.RationalTime(30, 30)
        )

        clip2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        track2 = otio.schema.Track('faded_indented')
        track2.append(gap1)
        track2.append(fade_in2)
        track2.append(clip2)

        tree = et.fromstring(
            otio.adapters.write_to_string(track2, 'mlt_xml')
        )

        tractor2_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            float(tractor2_e.attrib['out']),
            fade_in1.out_offset.value - 1
        )
        self.assertIsNotNone(tractor2_e)

        tracks2 = tractor2_e.findall('./track')
        self.assertEqual(tracks2[0].attrib['producer'], 'solid_black')
        self.assertEqual(
            tracks2[1].attrib['producer'],
            'clip2_transition_post'
        )

        playlist2_e = tree.find('./playlist/[@id="faded_indented"]')
        self.assertIsNotNone(playlist2_e)
        self.assertEqual(playlist2_e[0].tag, 'blank')
        self.assertEqual(
            playlist2_e[1].attrib['producer'],
            'transition_tractor0'
        )
        self.assertEqual(
            playlist2_e[2].attrib['producer'],
            'clip2'
        )
        self.assertEqual(
            float(playlist2_e[2].attrib['in']),
            30
        )

        # Useless fade
        fade_in3 = otio.schema.Transition(
            name='fadeIn',
            in_offset=otio.opentime.RationalTime(0, 30),
            out_offset=otio.opentime.RationalTime(30, 30)
        )
        track3 = otio.schema.Track('faded_useless')
        track3.append(fade_in3)
        tree = et.fromstring(
            otio.adapters.write_to_string(track3, 'mlt_xml')
        )

        tractor3_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            tractor3_e[0].attrib['producer'],
            tractor3_e[1].attrib['producer']
        )

    def test_video_fade_out(self):
        # beginning of timeline (useless)
        fade_out1 = otio.schema.Transition(
            name='fadeOut',
            in_offset=otio.opentime.RationalTime(30, 30),
            out_offset=otio.opentime.RationalTime(0, 30)
        )

        track1 = otio.schema.Track('fadeout_useless')
        track1.append(fade_out1)

        tree = et.fromstring(
            otio.adapters.write_to_string(track1, 'mlt_xml')
        )

        tractor1_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            tractor1_e[0].attrib['producer'],
            tractor1_e[1].attrib['producer']
        )

        # Regular fade out
        fade_out2 = otio.schema.Transition(
            name='fadeOut',
            in_offset=otio.opentime.RationalTime(30, 30),
            out_offset=otio.opentime.RationalTime(0, 30)
        )

        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        track2 = otio.schema.Track('fadeout')
        track2.append(clip1)
        track2.append(fade_out2)

        tree = et.fromstring(
            otio.adapters.write_to_string(track2, 'mlt_xml')
        )

        tractor2_e = tree.find('./tractor/[@id="tractor0"]')

        tracks = tractor2_e.findall('./multitrack/track')
        self.assertEqual(tracks[1].attrib['producer'], 'fadeout')

        transition_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            transition_e[0].attrib['producer'],
            'clip1_transition_pre'
        )
        self.assertEqual(
            float(transition_e[0].attrib['in']),
            clip1.source_range.duration.value - fade_out2.in_offset.value
        )

        playlist_e = tree.find('./playlist/[@id="fadeout"]')
        self.assertEqual(
            float(playlist_e[0].attrib['out']),
            float(transition_e[0].attrib['in']) - 1
        )

    def test_video_dissolve(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            )
        )

        clip2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        dissolve1 = otio.schema.Transition(
            name='dissolve',
            in_offset=otio.opentime.RationalTime(30, 30),
            out_offset=otio.opentime.RationalTime(0, 30)
        )

        clip3 = otio.schema.Clip(
            name='clip3',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        clip4 = otio.schema.Clip(
            name='clip4',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(30, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        dissolve2 = otio.schema.Transition(
            name='dissolve',
            in_offset=otio.opentime.RationalTime(30, 30),
            out_offset=otio.opentime.RationalTime(0, 30)
        )

        track1 = otio.schema.Track('dissolve')
        track1.append(clip1)
        track1.append(dissolve1)
        track1.append(clip2)

        tree = et.fromstring(
            otio.adapters.write_to_string(track1, 'mlt_xml')
        )

        transition1_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            transition1_e[0].attrib['producer'],
            'clip1_transition_pre'
        )
        self.assertEqual(
            transition1_e[1].attrib['producer'],
            'clip2_transition_post'
        )

        # Clip2 doesn't have enough media to cover the dissolve and has
        # negative values
        self.assertEqual(
            float(transition1_e[1].attrib['in']),
            -30.
        )

        track2 = otio.schema.Track('dissolve')
        track2.append(clip3)
        track2.append(dissolve2)
        track2.append(clip4)

        tree = et.fromstring(
            otio.adapters.write_to_string(track2, 'mlt_xml')
        )

        transition2_e = tree.find('./tractor/[@id="transition_tractor0"]')
        self.assertEqual(
            transition2_e[0].attrib['producer'],
            'clip3_transition_pre'
        )
        self.assertEqual(
            transition2_e[1].attrib['producer'],
            'clip4_transition_post'
        )

        self.assertEqual(
            float(transition2_e[1].attrib['in']),
            0.
        )

        # Video tracks dissolve with "luma" service
        service = transition2_e.find(
            './transition/property/[@name="mlt_service"]'
        )
        self.assertEqual(service.text, 'luma')

    def test_audio_dissolve(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        clip2 = otio.schema.Clip(
            name='clip2',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(30, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        dissolve1 = otio.schema.Transition(
            name='dissolve',
            in_offset=otio.opentime.RationalTime(30, 30),
            out_offset=otio.opentime.RationalTime(0, 30)
        )

        track1 = otio.schema.Track(
            'dissolve',
            kind=otio.schema.TrackKind.Audio
        )
        track1.append(clip1)
        track1.append(dissolve1)
        track1.append(clip2)

        tree = et.fromstring(
            otio.adapters.write_to_string(track1, 'mlt_xml')
        )
        transition1_e = tree.find('./tractor/[@id="transition_tractor0"]')

        # Audio tracks dissolve with "mix" service
        service = transition1_e.find(
            './transition/property/[@name="mlt_service"]'
        )
        self.assertEqual(service.text, 'mix')

    def test_time_warp(self):
        path = '/some/path/to/media_file.mov'

        # Speedup
        clip_with_speedup1 = otio.schema.Clip(
            name='clip_with_speedup',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url=path,
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 30),
                    otio.opentime.RationalTime(100, 30)
                )
            )
        )
        clip_with_speedup1.effects.append(
            otio.schema.LinearTimeWarp(
                time_scalar=2.
            )
        )

        track1 = otio.schema.Track('speedup')
        track1.append(clip_with_speedup1)

        tree = et.fromstring(
            otio.adapters.write_to_string(track1, 'mlt_xml')
        )

        self.assertIsNotNone(
            tree.find('./producer/[@id="clip_with_speedup"]')
        )

        # The adapter creates a new producer with the speed adjustment
        producer_e = tree.find('./producer/[@id="2.0:clip_with_speedup"]')
        self.assertIsNotNone(
            producer_e
        )
        self.assertEqual(
            producer_e.find('./property/[@name="mlt_service"]').text,
            'timewarp'
        )

        playlist1_e = tree.find('.playlist/[@id="speedup"]')
        self.assertEqual(
            playlist1_e[0].attrib['producer'],
            '2.0:clip_with_speedup'
        )

        # Slowdown
        clip_with_slowdown1 = otio.schema.Clip(
            name='clip_with_slowdown',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url=path,
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 30),
                    otio.opentime.RationalTime(100, 30)
                )
            )
        )
        clip_with_slowdown1.effects.append(
            otio.schema.LinearTimeWarp(
                time_scalar=-2.
            )
        )

        track2 = otio.schema.Track('speedup')
        track2.append(clip_with_slowdown1)

        tree = et.fromstring(
            otio.adapters.write_to_string(track2, 'mlt_xml')
        )

        # The adapter creates a new producer with the speed adjustment
        self.assertIsNotNone(
            tree.find('./producer/[@id="-2.0:clip_with_slowdown"]')
        )

    def test_freeze_frame(self):
        path = '/some/path/to/media_file.mov'
        clip_with_freeze1 = otio.schema.Clip(
            name='clip_with_freeze',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(100, 30)
            ),
            media_reference=otio.schema.ExternalReference(
                target_url=path,
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 30),
                    otio.opentime.RationalTime(100, 30)
                )
            )
        )
        clip_with_freeze1.effects.append(
            otio.schema.FreezeFrame()
        )

        track1 = otio.schema.Track('speedup')
        track1.append(clip_with_freeze1)

        tree = et.fromstring(
            otio.adapters.write_to_string(track1, 'mlt_xml')
        )

        # The adapter creates a new producer with "freeze0.0" suffix where
        # 0.0 is based on the source_range.start_time.value
        producer_e = tree.find(
            './producer/[@id="clip_with_freeze_freeze{}"]'
            .format(clip_with_freeze1.source_range.start_time.value)
        )
        self.assertIsNotNone(
            producer_e
        )

        self.assertEqual(
            producer_e.find('./property/[@name="mlt_service"]').text,
            'hold'
        )

    def test_ignoring_generator_reference(self):
        generator_clip1 = otio.schema.Clip(
            name='generator_clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(50, 30)
            ),
            media_reference=otio.schema.GeneratorReference(
                name='colorbars',
                generator_kind='SMPTEBars',
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, 30),
                    otio.opentime.RationalTime(50, 30)
                )
            )
        )
        track = otio.schema.Track('gen')
        track.append(generator_clip1)

        tree = et.fromstring(
            otio.adapters.write_to_string(track, 'mlt_xml')
        )

        producer_e = tree.find('./producer/[@id="colorbars"]')
        self.assertIsNotNone(producer_e)

    def test_passing_adapter_arguments(self):
        clip1 = otio.schema.Clip(
            name='clip1',
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(500, 30)
            )
        )

        track = otio.schema.Track('video')
        track.append(clip1)

        tree = et.fromstring(
            otio.adapters.write_to_string(
                track,
                'mlt_xml',
                width='1920',
                height='1080'
            )
        )

        profile_e = tree.find('./profile')
        self.assertIsNotNone(
            profile_e
        )
        self.assertEqual(int(profile_e.attrib['width']), 1920)

    def test_raise_error_mlt_on_read(self):
        with self.assertRaises(AdapterDoesntSupportFunctionError) as err:
            otio.adapters.read_from_file('bogus.mlt')

        self.assertEqual(
            "Sorry, mlt_xml doesn't support read_from_file.",
            str(err.exception)
        )
