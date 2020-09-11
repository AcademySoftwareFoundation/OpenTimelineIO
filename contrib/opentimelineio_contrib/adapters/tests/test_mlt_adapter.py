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


fade_in = otio.schema.Transition(
    name='fadeIn',
    in_offset=otio.opentime.RationalTime(0, 30),
    out_offset=otio.opentime.RationalTime(30, 30)
)

fade_out = otio.schema.Transition(
    name='fadeOut',
    in_offset=otio.opentime.RationalTime(30, 30),
    out_offset=otio.opentime.RationalTime(0, 30)
)


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

        self.assertIn(
            "Passed OTIO item must be Timeline, Track or Clip. "
            "Not {}".format(type(stack)),
            err.exception
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
        pass

    # TODO! implement better id handling in adapter and come back to this
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

        track = otio.schema.Track()
        track.append(clip1)
        track.append(clip2)

        tree = et.fromstring(otio.adapters.write_to_string(track, 'mlt_xml'))
        producers = tree.findall('./producer/[@id="{}"]'.format(clipname))
        self.assertEqual(len(producers), 1)

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

        tree = et.fromstring(otio.adapters.write_to_string(timeline, 'mlt_xml'))

    def test_nested_timeline(self):
        pass

    def test_nested_stack(self):
        pass

    def test_video_fade_in(self):
        pass

    def test_video_fade_out(self):
        pass

    def test_video_dissolve(self):
        pass

    def test_audio_dissolve(self):
        pass

    def test_time_warp(self):
        pass

    def test_freeze_frame(self):
        pass

    def test_ignoring_unsupported_objects(self):
        pass

    def test_passing_adapter_arguments(self):
        pass
