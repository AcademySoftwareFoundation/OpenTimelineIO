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
import sys
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "simple.aaf")
EXAMPLE_PATH2 = os.path.join(SAMPLE_DATA_DIR, "transitions.aaf")
EXAMPLE_PATH3 = os.path.join(SAMPLE_DATA_DIR, "trims.aaf")
EXAMPLE_PATH4 = os.path.join(SAMPLE_DATA_DIR, "multitrack.aaf")
EXAMPLE_PATH5 = os.path.join(SAMPLE_DATA_DIR, "preflattened.aaf")
EXAMPLE_PATH6 = os.path.join(SAMPLE_DATA_DIR, "nesting_test.aaf")
EXAMPLE_PATH7 = os.path.join(SAMPLE_DATA_DIR, "nesting_test_preflattened.aaf")


try:
    lib_path = os.environ.get("OTIO_AAF_PYTHON_LIB")
    if lib_path and lib_path not in sys.path:
        sys.path += [lib_path]
    import aaf # flake8: noqa
    could_import_aaf = True
except (ImportError):
    could_import_aaf = False

@unittest.skipIf(
    not could_import_aaf,
    "AAF module not found. You might need to set OTIO_AAF_PYTHON_LIB"
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

        self.assertEqual(len(timeline.tracks), 3)

        self.assertEqual(len(timeline.video_tracks()), 1)
        video_track = timeline.video_tracks()[0]
        self.assertEqual(len(video_track), 5)

        self.assertEqual(len(timeline.audio_tracks()), 2)

        clips = list(video_track.each_clip())

        self.assertEqual(
            [
                "tech.fux (loop)-HD.mp4",
                "t-hawk (loop)-HD.mp4",
                "out-b (loop)-HD.mp4",
                "KOLL-HD.mp4",
                "brokchrd (loop)-HD.mp4"
            ],
            [clip.name for clip in clips]
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
        self.assertIsNotNone(timeline)
        self.assertEqual(type(timeline), otio.schema.Timeline)
        self.assertEqual(timeline.name, "OTIO TEST 1.Exported.01")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        self.assertEqual(
            timeline.duration(),
            otio.opentime.from_timecode("00:02:16:18", fps)
        )
        self.assertEqual(len(timeline.tracks), 3)
        self.assertEqual(otio.schema.TrackKind.Video, timeline.tracks[0].kind)
        self.assertEqual(otio.schema.TrackKind.Audio, timeline.tracks[1].kind)
        self.assertEqual(otio.schema.TrackKind.Audio, timeline.tracks[2].kind)
        for track in timeline.tracks:
            self.assertEqual(len(track), 5)

    def test_aaf_no_simplify(self):
        aaf_path = EXAMPLE_PATH
        collection = otio.adapters.read_from_file(aaf_path, simplify=False)
        self.assertIsNotNone(collection)
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
        self.assertEqual(otio.schema.TrackKind.Video, video_track.kind)
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

        video_tracks = timeline.video_tracks()
        self.assertEqual(len(video_tracks), 1)
        video_track = video_tracks[0]
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
        self.assertEqual(timeline.name, "OTIO TEST - transitions.Exported.01")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)

        video_tracks = timeline.video_tracks()
        self.assertEqual(len(video_tracks), 1)
        video_track = video_tracks[0]
        self.assertEqual(len(video_track), 12)

        clips = list(video_track.each_clip())
        self.assertEqual(len(clips), 4)

        self.assertEqual(
            [type(item) for item in video_track],
            [
                otio.schema.Gap,
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Transition,
                otio.schema.Gap,
                otio.schema.Transition,
                otio.schema.Clip,
                otio.schema.Clip,
                otio.schema.Transition,
                otio.schema.Gap,
            ]
        )

        self.assertEqual(
            [item.name for item in video_track],
            [
                "Filler",
                "Transition",
                "tech.fux (loop)-HD.mp4",
                "Transition 2",
                "t-hawk (loop)-HD.mp4",
                "Transition 3",
                "Filler 2",
                "Transition 4",
                "KOLL-HD.mp4",
                "brokchrd (loop)-HD.mp4",
                "Transition 5",
                "Filler 3"
            ]
        )

        self.maxDiff = None
        desired_ranges = [
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(117, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(123, fps),
                otio.opentime.from_frames(200-123, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(55, fps),
                otio.opentime.from_frames(199-55, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(130, fps)
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
            otio.opentime.TimeRange(    # Gap
                otio.opentime.from_timecode("00:00:00:00", fps),
                otio.opentime.from_timecode("00:00:00:00", fps)
            ),
            otio.opentime.TimeRange(    # Transition
                otio.opentime.from_timecode("00:00:00:00", fps),
                otio.opentime.from_timecode("00:00:00:12", fps)
            ),
            otio.opentime.TimeRange(    # tech.fux
                otio.opentime.from_timecode("00:00:00:00", fps),
                otio.opentime.from_timecode("00:00:04:21", fps)
            ),
            otio.opentime.TimeRange(    # Transition
                otio.opentime.from_timecode("00:00:02:21", fps),
                otio.opentime.from_timecode("00:00:02:00", fps)
            ),
            otio.opentime.TimeRange(    # t-hawk
                otio.opentime.from_timecode("00:00:04:21", fps),
                otio.opentime.from_timecode("00:00:03:05", fps)
            ),
            otio.opentime.TimeRange(    # Transition
                otio.opentime.from_timecode("00:00:07:14", fps),
                otio.opentime.from_timecode("00:00:01:00", fps)
            ),
            otio.opentime.TimeRange(    # Gap
                otio.opentime.from_timecode("00:00:08:02", fps),
                otio.opentime.from_timecode("00:00:02:05", fps)
            ),
            otio.opentime.TimeRange(    # Transition
                otio.opentime.from_timecode("00:00:09:07", fps),
                otio.opentime.from_timecode("00:00:02:00", fps)
            ),
            otio.opentime.TimeRange(    # KOLL-HD
                otio.opentime.from_timecode("00:00:10:07", fps),
                otio.opentime.from_timecode("00:00:06:00", fps)
            ),
            otio.opentime.TimeRange(    # brokchrd
                otio.opentime.from_timecode("00:00:16:07", fps),
                otio.opentime.from_timecode("00:00:05:10", fps)
            ),
            otio.opentime.TimeRange(    # Transition
                otio.opentime.from_timecode("00:00:19:17", fps),
                otio.opentime.from_timecode("00:00:02:00", fps)
            ),
            otio.opentime.TimeRange(    # Gap
                otio.opentime.from_timecode("00:00:21:17", fps),
                otio.opentime.from_timecode("00:00:00:00", fps)
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
            otio.opentime.from_timecode("00:00:21:17", fps)
        )

    def test_aaf_user_comments(self):
        aaf_path = EXAMPLE_PATH3
        timeline = otio.adapters.read_from_file(aaf_path)
        self.assertTrue(timeline is not None)
        self.assertEqual(type(timeline), otio.schema.Timeline)
        self.assertIsNotNone(timeline.metadata.get("AAF"))
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
            self.assertIsNotNone(AAFmetadata)
            self.assertIsNotNone(AAFmetadata.get("UserComments"))
            self.assertEqual(
                AAFmetadata.get("UserComments").get("CustomTest"),
                correctWord
            )

    def test_aaf_flatten_tracks(self):
        multitrack_timeline = otio.adapters.read_from_file(EXAMPLE_PATH4)
        preflattened_timeline = otio.adapters.read_from_file(EXAMPLE_PATH5)

        # first make sure we got the structure we expected
        self.assertEqual(3, len(preflattened_timeline.tracks))
        self.assertEqual(1, len(preflattened_timeline.video_tracks()))
        self.assertEqual(2, len(preflattened_timeline.audio_tracks()))

        self.assertEqual(3, len(multitrack_timeline.video_tracks()))
        self.assertEqual(2, len(multitrack_timeline.audio_tracks()))
        self.assertEqual(5, len(multitrack_timeline.tracks))


        preflattened = preflattened_timeline.video_tracks()[0]
        self.assertEqual(7, len(preflattened))
        flattened = otio.algorithms.flatten_stack(
            multitrack_timeline.video_tracks()
        )
        self.assertEqual(7, len(flattened))

        # Lets remove some AAF metadata that will always be different
        # so we can compare everything else.
        for t in (preflattened, flattened):

            t.name = None
            t.metadata.pop("AAF", None)

            for c in t.each_child():
                if hasattr(c, "media_reference") and c.media_reference:
                    mr = c.media_reference
                    mr.metadata.get("AAF", {}).pop('LastModified', None)
                meta = c.metadata.get("AAF", {})
                meta.pop('ComponentAttributeList', None)
                meta.pop('DataDefinition', None)
                meta.pop('Length', None)
                meta.pop('StartTime', None)

            # We don't care about Gap start times, only their duration matters
            for g in t.each_child(descended_from_type=otio.schema.Gap):
                g.source_range.start_time.value = 0

        self.maxDiff = None
        self.assertMultiLineEqual(
            otio.adapters.write_to_string(preflattened, "otio_json"),
            otio.adapters.write_to_string(flattened, "otio_json")
        )


    def test_aaf_nesting(self):
        timeline = otio.adapters.read_from_file(EXAMPLE_PATH6)
        self.assertEqual(1, len(timeline.tracks))
        track = timeline.tracks[0]
        self.assertEqual(3, len(track))

        clipA, nested, clipB = track
        self.assertEqual(otio.schema.Clip, type(clipA))
        self.assertEqual(otio.schema.Track, type(nested))
        self.assertEqual(otio.schema.Clip, type(clipB))

        self.assertEqual(2, len(nested))
        nestedClipA, nestedClipB = nested
        self.assertEqual(otio.schema.Clip, type(nestedClipA))
        self.assertEqual(otio.schema.Clip, type(nestedClipB))

        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(24, 24),
                duration=otio.opentime.RationalTime(16, 24)
            ),
            clipA.trimmed_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(32, 24),
                # TODO: should actually be this, but we're not getting the
                # media timecode offset correctly from the AAF...
                # start_time=otio.opentime.RationalTime(86432, 24),
                duration=otio.opentime.RationalTime(16, 24)
            ),
            clipB.trimmed_range()
        )

        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(40, 24),
                duration=otio.opentime.RationalTime(8, 24)
            ),
            nestedClipA.trimmed_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(24, 24),
                # TODO: should actually be this, but we're not getting the
                # media timecode offset correctly from the AAF...
                # start_time=otio.opentime.RationalTime(86424, 24),
                duration=otio.opentime.RationalTime(8, 24)
            ),
            nestedClipB.trimmed_range()
        )


if __name__ == '__main__':
    unittest.main()
