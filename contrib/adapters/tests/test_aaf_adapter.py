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
EXAMPLE_PATH2 = os.path.join(SAMPLE_DATA_DIR, "transitions.aaf")
EXAMPLE_PATH3 = os.path.join(SAMPLE_DATA_DIR, "trims.aaf")


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

        video_track = timeline.tracks[8][0]
        self.assertEqual(len(video_track), 5)

    def test_aaf_read_trims(self):
        aaf_path = EXAMPLE_PATH3
        timeline = otio.adapters.read_from_file(aaf_path)
        self.assertEqual(
            timeline.name,
            "OTIO TEST 1.Exported.01 - trims.Exported.02"
        )
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)

        self.assertEqual(len(timeline.tracks), 1)
        video_track = timeline.tracks[0]
        self.assertEqual(len(video_track), 6)

        self.assertEqual(
            [type(item) for item in video_track],
            [
                otio.schema.Clip,
                otio.schema.Clip,
                otio.schema.Clip,
                otio.schema.Clip,
                otio.schema.Gap,
                otio.schema.Clip,
            ]
        )

        clips = list(video_track.each_clip())

        self.assertEqual(
            [item.name for item in video_track],
            [
                "tech.fux (loop)-HD.mp4",
                "t-hawk (loop)-HD.mp4",
                "out-b (loop)-HD.mp4",
                "KOLL-HD.mp4",
                "Filler",   # Gap
                "brokchrd (loop)-HD.mp4"
            ]
        )

        self.maxDiff = None
        desired_ranges = [
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(720-0, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(121, fps),
                otio.opentime.from_frames(480-121, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(123, fps),
                otio.opentime.from_frames(523-123, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(559-0, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(69, fps),
                otio.opentime.from_frames(720-69, fps)
            )
        ]
        for clip, desired in zip(clips, desired_ranges):
            actual = clip.source_range
            self.assertEqual(
                actual,
                desired,
                "clip '{}' source_range should be {} not {}".format(
                    clip.name,
                    desired,
                    actual
                )
            )
        
        desired_ranges = [
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("00:00:00:00", fps),
                otio.opentime.from_timecode("00:00:30:00", fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("00:00:30:00", fps),
                otio.opentime.from_timecode("00:00:14:23", fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("00:00:44:23", fps),
                otio.opentime.from_timecode("00:00:16:16", fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("00:01:01:15", fps),
                otio.opentime.from_timecode("00:00:23:07", fps)
            ),
            otio.opentime.TimeRange(    # Gap
                otio.opentime.from_timecode("00:01:24:22", fps),
                otio.opentime.from_timecode("00:00:04:12", fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("00:01:29:10", fps),
                otio.opentime.from_timecode("00:00:27:03", fps)
            )
        ]
        for item, desired in zip(video_track, desired_ranges):
            actual = item.trimmed_range_in_parent()
            self.assertEqual(
                actual,
                desired,
                "item '{}' trimmed_range_in_parent should be {} not {}".format(
                    clip.name,
                    desired,
                    actual
                )
            )

        self.assertEqual(
            timeline.duration(),
            otio.opentime.from_timecode("00:01:56:13", fps)
        )

    def test_aaf_read_transitions(self):
        aaf_path = EXAMPLE_PATH2
        timeline = otio.adapters.read_from_file(aaf_path)
        self.assertEqual(timeline.name, "OTIO TEST 2.Exported.01")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        # self.assertEqual(
        #     timeline.duration(),
        #     otio.opentime.from_timecode("00:02:01:05", fps)
        # )

        self.assertEqual(len(timeline.tracks), 1)
        video_track = timeline.tracks[0]
        self.assertEqual(len(video_track), 10)

        self.assertEqual(
            [type(item) for item in video_track],
            [
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Clip,
                otio.schema.Transition
            ]
        )

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
        actual_ranges = [clip.source_range for clip in clips]
        desired_ranges = [
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(719+1, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(123, fps),
                otio.opentime.from_frames(421-123+1, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(72, fps),
                otio.opentime.from_frames(656-72+1, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(55, fps),
                otio.opentime.from_frames(639-55+1, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(719+1, fps)
            )
        ]
        for clip, desired in zip(clips, desired_ranges):
            actual = clip.source_range
            self.assertEqual(actual, desired, "clip {} timing should be {} not {}".format(clip.name, desired, actual))
        
        self.assertEqual(
            [item.trimmed_range_in_parent() for item in video_track],
            [
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("00:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
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

    def test_aaf_user_comments(self):
        aaf_path = EXAMPLE_PATH3
        timeline = otio.adapters.read_from_file(aaf_path)
        self.assertTrue(timeline is not None)
        self.assertEqual(type(timeline), otio.schema.Timeline)
        self.assertTrue(timeline.metadata.get("AAF") is not None)
        correctWords = [
            "test1",
            "testing 1 2 3",
            u"Eyjafjallaj\xf6kull",
            "'s' \"d\" `b`",
            None,   # Gap
            None
        ]
        for clip, correctWord in zip(timeline.tracks[0], correctWords):
            if isinstance(clip, otio.schema.Gap):
                continue
            AAFmetadata = clip.media_reference.metadata.get("AAF")
            self.assertTrue(AAFmetadata is not None)
            self.assertTrue(AAFmetadata.get("UserComments") is not None)
            self.assertEqual(
                AAFmetadata.get("UserComments").get("CustomTest"),
                correctWord
            )

if __name__ == '__main__':
    unittest.main()
