#
# Copyright 2017 Pixar Animation Studios
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

"""Test final cut pro xml."""

# python
import os
import tempfile
import unittest
import collections
from xml.etree import cElementTree

import opentimelineio as otio
from opentimelineio.exceptions import CannotComputeAvailableRangeError

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
FCP7_XML_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "premiere_example.xml")
SIMPLE_XML_PATH = os.path.join(SAMPLE_DATA_DIR, "sample_just_track.xml")
HIERO_XML_PATH = os.path.join(SAMPLE_DATA_DIR, "hiero_xml_export.xml")


class AdaptersFcp7XmlTest(unittest.TestCase, otio.test_utils.OTIOAssertions):

    def __init__(self, *args, **kwargs):
        super(AdaptersFcp7XmlTest, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def test_read(self):
        timeline = otio.adapters.read_from_file(FCP7_XML_EXAMPLE_PATH)

        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 8)

        video_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Video
        ]
        audio_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Audio
        ]

        self.assertEqual(len(video_tracks), 4)
        self.assertEqual(len(audio_tracks), 4)

        video_clip_names = (
            (None, 'sc01_sh010_anim.mov'),
            (
                None,
                'sc01_sh010_anim.mov',
                None,
                'sc01_sh020_anim.mov',
                'sc01_sh030_anim.mov',
                'Cross Dissolve',
                None,
                'sc01_sh010_anim'
            ),
            (None, 'test_title'),
            (
                None,
                'sc01_master_layerA_sh030_temp.mov',
                'Cross Dissolve',
                'sc01_sh010_anim.mov'
            )
        )

        for n, track in enumerate(video_tracks):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        audio_clip_names = (
            (None, 'sc01_sh010_anim.mov', None, 'sc01_sh010_anim.mov'),
            (None, 'sc01_placeholder.wav', None, 'sc01_sh010_anim'),
            (None, 'track_08.wav'),
            (None, 'sc01_master_layerA_sh030_temp.mov', 'sc01_sh010_anim.mov')
        )

        for n, track in enumerate(audio_tracks):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                audio_clip_names[n]
            )

        video_clip_durations = (
            ((536, 30.0), (100, 30.0)),
            (
                (13, 30.0),
                (100, 30.0),
                (52, 30.0),
                (157, 30.0),
                (235, 30.0),
                ((19, 30.0), (0, 30.0)),
                (79, 30.0),
                (320, 30.0)
            ),
            ((15, 30.0), (941, 30.0)),
            ((956, 30.0), (208, 30.0), ((12, 30.0), (13, 30.0)), (82, 30.0))
        )

        for t, track in enumerate(video_tracks):
            for c, clip in enumerate(track):
                if isinstance(clip, otio.schema.Transition):
                    self.assertEqual(
                        clip.in_offset,
                        otio.opentime.RationalTime(
                            *video_clip_durations[t][c][0]
                        )
                    )
                    self.assertEqual(
                        clip.out_offset,
                        otio.opentime.RationalTime(
                            *video_clip_durations[t][c][1]
                        )
                    )
                else:
                    self.assertEqual(
                        clip.source_range.duration,
                        otio.opentime.RationalTime(*video_clip_durations[t][c])
                    )

        audio_clip_durations = (
            ((13, 30.0), (100, 30.0), (423, 30.0), (100, 30.0), (423, 30.0)),
            (
                (335, 30.0),
                (170, 30.0),
                (131, 30.0),
                (294, 30.0),
                (34, 30.0),
                (124, 30.0)
            ),
            ((153, 30.0), (198, 30.0)),
            ((956, 30.0), (221, 30.0), (94, 30.0))
        )

        for t, track in enumerate(audio_tracks):
            for c, clip in enumerate(track):
                self.assertEqual(
                    clip.source_range.duration,
                    otio.opentime.RationalTime(*audio_clip_durations[t][c])
                )

        timeline_marker_names = ('My MArker 1', 'dsf', None)

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(marker.name, timeline_marker_names[n])

        timeline_marker_start_times = ((113, 30.0), (492, 30.0), (298, 30.0))

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(
                marker.marked_range.start_time,
                otio.opentime.RationalTime(*timeline_marker_start_times[n])
            )

        timeline_marker_comments = ('so, this happened', 'fsfsfs', None)

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(
                marker.metadata.get('fcp_xml', {}).get('comment'),
                timeline_marker_comments[n]
            )

        clip_with_marker = video_tracks[1][4]
        clip_marker = clip_with_marker.markers[0]
        self.assertEqual(clip_marker.name, None)
        self.assertEqual(
            clip_marker.marked_range.start_time,
            otio.opentime.RationalTime(73, 30.0)
        )
        self.assertEqual(
            clip_marker.metadata.get('fcp_xml', {}).get('comment'),
            None
        )

    def test_backreference_generator_read(self):
        with open(SIMPLE_XML_PATH, 'r') as fo:
            text = fo.read()

        adapt_mod = otio.adapters.from_name('fcp_xml').module()

        tree = cElementTree.fromstring(text)
        track = adapt_mod._get_top_level_tracks(tree)[0]

        # make sure that element_map gets populated by the function calls in
        # the way we want
        element_map = collections.defaultdict(dict)

        self.assertEqual(adapt_mod._parse_rate(track, element_map), 30.0)
        self.assertEqual(track, element_map["all_elements"]["sequence-1"])
        self.assertEqual(adapt_mod._parse_rate(track, element_map), 30.0)
        self.assertEqual(track, element_map["all_elements"]["sequence-1"])
        self.assertEqual(len(element_map["all_elements"].keys()), 1)

    def test_backreference_generator_write(self):

        adapt_mod = otio.adapters.from_name('fcp_xml').module()

        class dummy_obj(object):
            def __init__(self):
                self.attrib = {}

        @adapt_mod._backreference_build("test")
        def dummy_func(item, br_map):
            return dummy_obj()

        br_map = collections.defaultdict(dict)
        result_first = dummy_func("foo", br_map)
        self.assertNotEqual(br_map['test'], result_first)
        result_second = dummy_func("foo", br_map)
        self.assertNotEqual(result_first, result_second)

    def test_roundtrip_mem2disk2mem(self):
        timeline = otio.schema.Timeline('test_timeline')
        timeline.tracks.name = 'test_timeline'

        video_reference = otio.schema.ExternalReference(
                target_url="/var/tmp/test1.mov",
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(value=100, rate=24.0),
                    otio.opentime.RationalTime(value=1000, rate=24.0)
                )
            )
        audio_reference = otio.schema.ExternalReference(
                target_url="/var/tmp/test1.wav",
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(value=0, rate=24.0),
                    otio.opentime.RationalTime(value=1000, rate=24.0)
                )
            )

        v0 = otio.schema.Track(kind=otio.schema.track.TrackKind.Video)
        v1 = otio.schema.Track(kind=otio.schema.track.TrackKind.Video)

        timeline.tracks.extend([v0, v1])

        a0 = otio.schema.Track(kind=otio.schema.track.TrackKind.Audio)

        timeline.tracks.append(a0)

        v0.extend(
            [
                otio.schema.Clip(
                    name='test_clip1',
                    media_reference=video_reference,
                    source_range=otio.opentime.TimeRange(
                        otio.opentime.RationalTime(value=112, rate=24.0),
                        otio.opentime.RationalTime(value=40, rate=24.0)
                    )
                ),
                otio.schema.Gap(
                    source_range=otio.opentime.TimeRange(
                        duration=otio.opentime.RationalTime(
                            value=60,
                            rate=24.0
                        )
                    )
                ),
                otio.schema.Clip(
                    name='test_clip2',
                    media_reference=video_reference,
                    source_range=otio.opentime.TimeRange(
                        otio.opentime.RationalTime(value=123, rate=24.0),
                        otio.opentime.RationalTime(value=260, rate=24.0)
                    )
                )
            ]
        )

        v1.extend([
            otio.schema.Gap(
                source_range=otio.opentime.TimeRange(
                    duration=otio.opentime.RationalTime(value=500, rate=24.0)
                )
            ),
            otio.schema.Clip(
                name='test_clip3',
                media_reference=video_reference,
                source_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(value=112, rate=24.0),
                    otio.opentime.RationalTime(value=55, rate=24.0)
                )
            )
        ])

        a0.extend([
            otio.schema.Gap(
                source_range=otio.opentime.TimeRange(
                    duration=otio.opentime.RationalTime(value=10, rate=24.0)
                )
            ),
            otio.schema.Clip(
                name='test_clip4',
                media_reference=audio_reference,
                source_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(value=152, rate=24.0),
                    otio.opentime.RationalTime(value=248, rate=24.0)
                )
            )
        ])

        timeline.tracks.markers.append(
            otio.schema.Marker(
                name='test_timeline_marker',
                marked_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(123, 24.0)
                ),
                metadata={'fcp_xml': {'comment': 'my_comment'}}
            )
        )

        v1[1].markers.append(
            otio.schema.Marker(
                name='test_clip_marker',
                marked_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(125, 24.0)
                ),
                metadata={'fcp_xml': {'comment': 'my_comment'}}
            )
        )

        result = otio.adapters.write_to_string(
            timeline,
            adapter_name='fcp_xml'
        )
        new_timeline = otio.adapters.read_from_string(
            result,
            adapter_name='fcp_xml'
        )

        self.assertJsonEqual(new_timeline, timeline)

    def test_roundtrip_disk2mem2disk(self):
        timeline = otio.adapters.read_from_file(FCP7_XML_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".xml", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)
        result = otio.adapters.read_from_file(tmp_path)

        original_json = otio.adapters.write_to_string(timeline, 'otio_json')
        output_json = otio.adapters.write_to_string(result, 'otio_json')
        self.assertMultiLineEqual(original_json, output_json)

        self.assertIsOTIOEquivalentTo(timeline, result)

        # But the xml text on disk is not identical because otio has a subset
        # of features to xml and we drop all the nle specific preferences.
        with open(FCP7_XML_EXAMPLE_PATH, "r") as original_file:
            with open(tmp_path, "r") as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())

    def test_hiero_flavored_xml(self):
        timeline = otio.adapters.read_from_file(HIERO_XML_PATH)
        self.assertTrue(len(timeline.tracks), 1)
        self.assertTrue(timeline.tracks[0].name == 'Video 1')

        clips = [c for c in timeline.tracks[0].each_clip()]
        self.assertTrue(len(clips), 2)

        self.assertTrue(clips[0].name == 'A160C005_171213_R0MN')
        self.assertTrue(clips[1].name == '/')

        self.assertTrue(
                isinstance(
                    clips[0].media_reference,
                    otio.schema.ExternalReference
                    )
                )

        self.assertTrue(
                isinstance(
                    clips[1].media_reference,
                    otio.schema.MissingReference
                    )
                )

        source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(1101071, 24),
            duration=otio.opentime.RationalTime(1055, 24)
            )
        self.assertTrue(clips[0].source_range == source_range)

        available_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(1101071, 24),
            duration=otio.opentime.RationalTime(1055, 24)
            )
        self.assertTrue(clips[0].available_range() == available_range)

        with self.assertRaises(CannotComputeAvailableRangeError):
            clips[1].available_range()

        # Test serialization
        tmp_path = tempfile.mkstemp(suffix=".xml", text=True)[1]
        otio.adapters.write_to_file(timeline, tmp_path)

        # Similar to the test_roundtrip_disk2mem2disk above
        # the track name element among others will not be present in a new xml.
        with open(HIERO_XML_PATH, "r") as original_file:
            with open(tmp_path, "r") as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())


if __name__ == '__main__':
    unittest.main()
