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

"""Test the AAF adapter."""

# python
import os
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "simple.aaf")


@unittest.skipIf(
    "OTIO_AAF_PYTHON_LIB" not in os.environ,
    "OTIO_AAF_PYTHON_LIB not set, required for the AAF adapter"
)
class AAFAdapterTest(unittest.TestCase):

    def test_aaf_read(self):
        aaf_path = EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(aaf_path)
        self.assertEqual(timeline.name, "OTIO TEST 1.Exported.01")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        self.assertEqual(
            timeline.duration(),
            otio.opentime.from_timecode("00:02:16:18", fps)
        )

        self.assertEqual(len(timeline.tracks), 1)
        video_track = timeline.tracks[0]
        self.assertEqual(len(video_track), 5)

        clips = list(timeline.each_clip())

        self.assertEqual(
            [clip.name for clip in clips],
            [
                "tech.fux (loop)-HD.mp4",
                "t-hawk (loop)-HD.mp4",
                "out-b (loop)-HD.mp4",
                "KOLL-HD.mp4",
                "brokchrd (loop)-HD.mp4"
            ]
        )
        self.maxDiff = None
        self.assertEqual(
            [clip.source_range for clip in clips],
            [
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:20:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:02", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:26:16", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                )
            ]
        )

    def test_aaf_simplify(self):
        aaf_path = EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(aaf_path, simplify=True)
        self.assertTrue(timeline is not None)
        self.assertEqual(type(timeline), otio.schema.Timeline)
        self.assertEqual(timeline.name, "OTIO TEST 1.Exported.01")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        self.assertEqual(
            timeline.duration(),
            otio.opentime.from_timecode("00:02:16:18", fps)
        )
        self.assertEqual(len(timeline.tracks), 1)
        video_track = timeline.tracks[0]
        self.assertEqual(len(video_track), 5)

    def test_aaf_no_simplify(self):
        aaf_path = EXAMPLE_PATH
        collection = otio.adapters.read_from_file(aaf_path, simplify=False)
        self.assertTrue(collection is not None)
        self.assertEqual(type(collection), otio.schema.SerializableCollection)
        self.assertEqual(len(collection), 1)

        timeline = collection[0]
        self.assertEqual(timeline.name, "OTIO TEST 1.Exported.01")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        self.assertEqual(
            timeline.duration(),
            otio.opentime.from_timecode("00:02:16:18", fps)
        )

        self.assertEqual(len(timeline.tracks), 12)

        video_track = timeline.tracks[0]
        self.assertEqual(len(video_track), 5)


if __name__ == '__main__':
    unittest.main()
