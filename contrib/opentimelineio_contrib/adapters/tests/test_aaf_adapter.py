# -*- coding: utf-8 -*-
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
import tempfile

import opentimelineio as otio
from opentimelineio_contrib.adapters.aaf_adapter.aaf_writer import (
    AAFAdapterError,
    AAFValidationError
)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SIMPLE_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "simple.aaf"
)
TRANSITIONS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "transitions.aaf"
)
TRIMS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "trims.aaf"
)
MULTITRACK_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "multitrack.aaf"
)
PREFLATTENED_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "preflattened.aaf"
)
NESTING_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "nesting_test.aaf"
)
NESTED_STACK_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "nested_stack.aaf"
)
NESTING_PREFLATTENED_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "nesting_test_preflattened.aaf"
)
MISC_SPEED_EFFECTS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "misc_speed_effects.aaf"
)
PRECHECK_FAIL_OTIO = os.path.join(
    SAMPLE_DATA_DIR,
    "precheckfail.otio"
)
LINEAR_SPEED_EFFECTS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "linear_speed_effects.aaf"
)
TIMCODE_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "timecode_test.aaf"
)
MUTED_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "test_muted_clip.aaf"
)
ESSENCE_GROUP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "essence_group.aaf"
)
ONE_AUDIO_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "one_audio_clip.aaf"
)
FPS30_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "30fps.aaf"
)
FPS2997_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "2997fps.aaf"
)
DUPLICATES_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "duplicates.aaf"
)
NO_METADATA_OTIO_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "no_metadata.otio"
)
NOT_AAF_OTIO_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "not_aaf.otio"
)
UTF8_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "utf8.aaf"
)
MULTIPLE_TOP_LEVEL_MOBS_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "multiple_top_level_mobs.aaf"
)
GAPS_OTIO_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "gaps.otio"
)


def safe_str(maybe_str):
    """To help with testing between python 2 and 3, this function attempts to
    decode a string, and if it cannot decode it just returns the string.
    """
    try:
        return maybe_str.decode('utf-8')
    except AttributeError:
        return maybe_str


try:
    lib_path = os.environ.get("OTIO_AAF_PYTHON_LIB")
    if lib_path and lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    import aaf2  # noqa
    from aaf2.components import (SourceClip,
                                 Filler,
                                 Transition,
                                 Timecode,
                                 OperationGroup,
                                 Sequence)
    from aaf2.mobs import MasterMob, SourceMob
    from aaf2.misc import VaryingValue
    could_import_aaf = True
except (ImportError):
    could_import_aaf = False


@unittest.skipIf(
    not could_import_aaf,
    "AAF module not found. You might need to set OTIO_AAF_PYTHON_LIB"
)
class AAFReaderTests(unittest.TestCase):

    def test_aaf_read(self):
        aaf_path = SIMPLE_EXAMPLE_PATH
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
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:20:00", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:02", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:26:16", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:30:00", fps)
                )
            ]
        )

    def test_aaf_global_start_time(self):
        timeline = otio.adapters.read_from_file(SIMPLE_EXAMPLE_PATH)
        self.assertEqual(
            otio.opentime.from_timecode("01:00:00:00", 24),
            timeline.global_start_time
        )

    def test_aaf_read_trims(self):
        aaf_path = TRIMS_EXAMPLE_PATH
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
                otio.opentime.from_frames(86400, fps),
                otio.opentime.from_frames(720 - 0, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(86400 + 121, fps),
                otio.opentime.from_frames(480 - 121, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(86400 + 123, fps),
                otio.opentime.from_frames(523 - 123, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(0, fps),
                otio.opentime.from_frames(559 - 0, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(86400 + 69, fps),
                otio.opentime.from_frames(720 - 69, fps)
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
        aaf_path = TRANSITIONS_EXAMPLE_PATH
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
                "Transition",
                "t-hawk (loop)-HD.mp4",
                "Transition",
                "Filler",
                "Transition",
                "KOLL-HD.mp4",
                "brokchrd (loop)-HD.mp4",
                "Transition",
                "Filler"
            ]
        )

        self.maxDiff = None
        desired_ranges = [
            otio.opentime.TimeRange(
                otio.opentime.from_frames(86400 + 0, fps),
                otio.opentime.from_frames(117, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(86400 + 123, fps),
                otio.opentime.from_frames(200 - 123, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(55, fps),
                otio.opentime.from_frames(199 - 55, fps)
            ),
            otio.opentime.TimeRange(
                otio.opentime.from_frames(86400 + 0, fps),
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
                desired,
                actual,
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

    def test_timecode(self):
        aaf_path = TIMCODE_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(aaf_path)
        self.assertNotEqual(
            timeline.tracks[0][0].source_range.start_time,
            timeline.tracks[0][1].source_range.start_time
        )
        self.assertEqual(
            timeline.tracks[0][1].source_range.start_time,
            otio.opentime.RationalTime(86424, 24),
        )

    def test_aaf_user_comments(self):
        aaf_path = TRIMS_EXAMPLE_PATH
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
        multitrack_timeline = otio.adapters.read_from_file(
            MULTITRACK_EXAMPLE_PATH
        )
        preflattened_timeline = otio.adapters.read_from_file(
            PREFLATTENED_EXAMPLE_PATH
        )

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

            t.name = ""
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
                dur = g.source_range.duration
                rate = g.source_range.start_time.rate
                g.source_range = otio.opentime.TimeRange(
                    otio.opentime.RationalTime(0, rate),
                    dur
                )

        self.maxDiff = None
        self.assertMultiLineEqual(
            otio.adapters.write_to_string(preflattened, "otio_json"),
            otio.adapters.write_to_string(flattened, "otio_json")
        )

    def test_aaf_nesting(self):
        timeline = otio.adapters.read_from_file(NESTING_EXAMPLE_PATH)
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
                start_time=otio.opentime.RationalTime(86400 + 32, 24),
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
                start_time=otio.opentime.RationalTime(86400 + 24, 24),
                duration=otio.opentime.RationalTime(8, 24)
            ),
            nestedClipB.trimmed_range()
        )

    # TODO: This belongs in the algorithms tests, not the AAF tests.
    def SKIP_test_nesting_flatten(self):
        nested_timeline = otio.adapters.read_from_file(
            NESTING_EXAMPLE_PATH
        )
        preflattened_timeline = otio.adapters.read_from_file(
            NESTING_PREFLATTENED_EXAMPLE_PATH
        )
        flattened_track = otio.algorithms.flatten_stack(nested_timeline.tracks)
        self.assertEqual(
            preflattened_timeline.tracks[0],
            flattened_track
        )

    def test_read_linear_speed_effects(self):
        timeline = otio.adapters.read_from_file(
            LINEAR_SPEED_EFFECTS_EXAMPLE_PATH
        )
        self.assertEqual(1, len(timeline.tracks))
        track = timeline.tracks[0]
        self.assertEqual(20, len(track))

        clip = track[0]
        self.assertEqual(0, len(clip.effects))

        for clip in track[1:]:
            self.assertIsInstance(clip, otio.schema.Clip)
            self.assertEqual(1, len(clip.effects))
            effect = clip.effects[0]
            self.assertEqual(otio.schema.LinearTimeWarp, type(effect))

        expected = [
            50.00,   # 2/1
            33.33,   # 3/1
            25.00,   # 4/1
            200.00,  # 1/2
            100.00,  # 2/2
            66.67,   # 3/2
            50.00,   # 4/2
            300.00,  # 1/3
            150.00,  # 2/3
            100.00,  # 3/3
            75.00,   # 4/3
            400.00,  # 1/4
            200.00,  # 2/4
            133.33,  # 3/4
            100.00,  # 4/4
            500.00,  # 1/5
            250.00,  # 2/5
            166.67,  # 3/5
            125.00   # 4/5
        ]
        actual = [
            round(clip.effects[0].time_scalar * 100.0, 2) for clip in track[1:]
        ]
        self.assertEqual(expected, actual)

    def test_read_misc_speed_effects(self):
        timeline = otio.adapters.read_from_file(
            MISC_SPEED_EFFECTS_EXAMPLE_PATH
        )
        self.assertEqual(1, len(timeline.tracks))
        track = timeline.tracks[0]
        self.assertEqual(10, len(track))

        clip = track[0]
        self.assertEqual(0, len(clip.effects))
        self.assertEqual(8, clip.duration().value)

        clip = track[1]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.FreezeFrame, type(effect))
        self.assertEqual(0, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[2]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(2.0, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[3]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(0.5, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[4]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(3.0, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[5]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(0.3750, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[6]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(14.3750, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[7]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(0.3750, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[8]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertEqual(otio.schema.LinearTimeWarp, type(effect))
        self.assertEqual(-1.0, effect.time_scalar)
        self.assertEqual(8, clip.duration().value)

        clip = track[9]
        self.assertEqual(1, len(clip.effects))
        effect = clip.effects[0]
        self.assertTrue(isinstance(effect, otio.schema.TimeEffect))
        self.assertEqual(16, clip.duration().value)
        # TODO: We don't yet support non-linear time warps, but when we
        # do then this effect is a "Speed Bump" from 166% to 44% to 166%

    def test_muted_clip(self):
        sc = otio.adapters.read_from_file(MUTED_CLIP_PATH, simplify=False)
        gp = sc[0].tracks[8][0][0]

        self.assertIsNotNone(gp)
        self.assertTrue(gp.metadata['AAF']['muted_clip'])
        self.assertIsInstance(gp, otio.schema.Gap)
        self.assertEqual(gp.name, 'Frame Debugger 0h.mov_MUTED')

    def test_essence_group(self):
        timeline = otio.adapters.read_from_file(ESSENCE_GROUP_PATH)

        self.assertIsNotNone(timeline)
        self.assertEqual(
            otio.opentime.RationalTime(12, 24),
            timeline.duration()
        )

    def test_30fps(self):
        tl = otio.adapters.read_from_file(FPS30_CLIP_PATH)
        self.assertEqual(tl.duration().rate, 30)

    def test_2997fps(self):
        tl = otio.adapters.read_from_file(FPS2997_CLIP_PATH)
        self.assertEqual(tl.duration().rate, 30000 / 1001.0)

    def test_utf8_names(self):
        timeline = otio.adapters.read_from_file(UTF8_CLIP_PATH)
        self.assertEqual(
            (u"Sequence_ABCXYZñçêœ•∑´®†¥¨ˆøπ“‘åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥÷.Exported.01"),
            safe_str(timeline.name)
        )
        video_track = timeline.video_tracks()[0]
        first_clip = video_track[0]
        self.assertEqual(
            safe_str(first_clip.name),
            (u"Clip_ABCXYZñçêœ•∑´®†¥¨ˆøπ“‘åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥÷")
        )
        self.assertEqual(
            (
                first_clip.media_reference.metadata["AAF"]["UserComments"]["Comments"]
            ).encode('utf-8'),
            (u"Comments_ABCXYZñçêœ•∑´®†¥¨ˆøπ“‘åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥÷").encode('utf-8')
        )

    def test_multiple_top_level_mobs(self):
        result = otio.adapters.read_from_file(MULTIPLE_TOP_LEVEL_MOBS_CLIP_PATH)
        self.assertIsInstance(result, otio.schema.SerializableCollection)
        self.assertEqual(2, len(result))


class AAFWriterTests(unittest.TestCase):
    def test_aaf_writer_gaps(self):
        otio_timeline = otio.adapters.read_from_file(GAPS_OTIO_PATH)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        otio.adapters.write_to_file(otio_timeline, tmp_aaf_path)
        self._verify_aaf(tmp_aaf_path)

    def test_aaf_writer_simple(self):
        self._verify_aaf(SIMPLE_EXAMPLE_PATH)

    def test_aaf_writer_transitions(self):
        self._verify_aaf(TRANSITIONS_EXAMPLE_PATH)

    def test_aaf_writer_duplicates(self):
        self._verify_aaf(DUPLICATES_PATH)

    def test_aaf_writer_nometadata(self):
        def _target_url_fixup(timeline):
            # fixes up relative paths to be absolute to this test file
            test_dir = os.path.dirname(os.path.abspath(__file__))
            for clip in timeline.each_clip():
                target_url_str = clip.media_reference.target_url
                clip.media_reference.target_url = os.path.join(test_dir, target_url_str)

        # Exercise getting Mob IDs from AAF files
        otio_timeline = otio.adapters.read_from_file(NO_METADATA_OTIO_PATH)
        _target_url_fixup(otio_timeline)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        otio.adapters.write_to_file(otio_timeline, tmp_aaf_path)
        self._verify_aaf(tmp_aaf_path)

        # Expect exception to raise on non AAF files with no metadata
        otio_timeline = otio.adapters.read_from_file(NOT_AAF_OTIO_PATH)
        _target_url_fixup(otio_timeline)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        with self.assertRaises(AAFAdapterError):
            otio.adapters.write_to_file(otio_timeline, tmp_aaf_path)

        # Generate empty Mob IDs fallback for not crashing
        otio_timeline = otio.adapters.read_from_file(NOT_AAF_OTIO_PATH)
        _target_url_fixup(otio_timeline)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        otio.adapters.write_to_file(otio_timeline, tmp_aaf_path, use_empty_mob_ids=True)
        self._verify_aaf(tmp_aaf_path)

    def test_fail_on_precheck(self):
        # Expect exception to raise on null available_range and rate mismatch
        otio_timeline = otio.adapters.read_from_file(PRECHECK_FAIL_OTIO)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        try:
            otio.adapters.write_to_file(otio_timeline, tmp_aaf_path)
        except AAFValidationError as e:
            # Four error messages are raised
            self.assertEqual(4, len(list(filter(bool, str(e).split("\n")))))
            with self.assertRaises(AAFValidationError):
                raise e

    def test_aaf_roundtrip_first_clip(self):
        def _target_url_fixup(timeline):
            # fixes up relative paths to be absolute to this test file
            test_dir = os.path.dirname(os.path.abspath(__file__))
            for clip in timeline.each_clip():
                target_url_str = clip.media_reference.target_url
                clip.media_reference.target_url = os.path.join(test_dir, target_url_str)

        # Exercise getting Mob IDs from AAF files
        otio_timeline = otio.adapters.read_from_file(NO_METADATA_OTIO_PATH)
        _target_url_fixup(otio_timeline)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        otio.adapters.write_to_file(otio_timeline, tmp_aaf_path)
        self._verify_first_clip(otio_timeline, tmp_aaf_path)

    def _verify_first_clip(self, original_timeline, aaf_path):
        timeline_from_aaf = otio.adapters.read_from_file(aaf_path)

        original_clips = list(original_timeline.each_clip())
        aaf_clips = list(timeline_from_aaf.each_clip())

        self.assertTrue(len(original_clips) > 0)
        self.assertEqual(len(aaf_clips), len(original_clips))

        first_clip_in_original_timeline = original_clips[0]
        first_clip_in_aaf_timeline = aaf_clips[0]

        # Comparing stuff
        for prop in ['source_range']:
            self.assertEqual(getattr(first_clip_in_original_timeline, prop),
                             getattr(first_clip_in_aaf_timeline, prop),
                             "`{}` did not match".format(prop))

        for method in ['visible_range', 'trimmed_range']:
            self.assertEqual(getattr(first_clip_in_original_timeline, method)(),
                             getattr(first_clip_in_aaf_timeline, method)(),
                             "`{}` did not match".format(method))

    def test_aaf_writer_nesting(self):
        self._verify_aaf(NESTING_EXAMPLE_PATH)

    def test_aaf_writer_nested_stack(self):
        self._verify_aaf(NESTED_STACK_EXAMPLE_PATH)

    def _verify_aaf(self, aaf_path):
        otio_timeline = otio.adapters.read_from_file(aaf_path, simplify=True)
        fd, tmp_aaf_path = tempfile.mkstemp(suffix='.aaf')
        otio.adapters.write_to_file(otio_timeline, tmp_aaf_path)

        with aaf2.open(tmp_aaf_path) as dest, aaf2.open(aaf_path) as orig:
            # Basic number of mobs should be equal
            self.assertEqual(len(list(orig.content.compositionmobs())),
                             len(list(dest.content.compositionmobs())))
            self.assertEqual(len(list(orig.content.mastermobs())),
                             len(list(dest.content.mastermobs())))

            compositionmobs = list(dest.content.compositionmobs())
            self.assertEqual(1, len(compositionmobs))
            compositionmob = compositionmobs[0]
            self.assertEqual(len(otio_timeline.tracks), len(compositionmob.slots))

            for otio_track, aaf_timeline_mobslot in zip(otio_timeline.tracks,
                                                        compositionmob.slots):

                media_kind = aaf_timeline_mobslot.media_kind.lower()
                self.assertTrue(media_kind in ["picture", "sound"])
                kind_mapping = {
                    "picture": otio.schema.TrackKind.Video,
                    "sound": otio.schema.TrackKind.Audio
                }
                self.assertEqual(otio_track.kind, kind_mapping[media_kind])

                sequence = None
                if media_kind == "picture":
                    sequence = aaf_timeline_mobslot.segment
                elif media_kind == "sound":
                    opgroup = aaf_timeline_mobslot.segment
                    self.assertTrue(isinstance(opgroup, OperationGroup))
                    input_segments = opgroup.segments
                    self.assertTrue(hasattr(input_segments, "__iter__"))
                    self.assertTrue(len(input_segments) >= 1)
                    sequence = opgroup.segments[0]
                self.assertTrue(isinstance(sequence, Sequence))

                self.assertEqual(len(list(otio_track.each_child(shallow_search=True))),
                                 len(sequence.components))
                for otio_child, aaf_component in zip(
                        otio_track.each_child(shallow_search=True),
                        sequence.components):
                    type_mapping = {
                        otio.schema.Clip: aaf2.components.SourceClip,
                        otio.schema.Transition: aaf2.components.Transition,
                        otio.schema.Gap: aaf2.components.Filler,
                        otio.schema.Stack: aaf2.components.OperationGroup,
                        otio.schema.Track: aaf2.components.OperationGroup
                    }
                    self.assertEqual(type(aaf_component),
                                     type_mapping[type(otio_child)])

                    if isinstance(aaf_component, SourceClip):
                        self._verify_compositionmob_sourceclip_structure(aaf_component)

                    if isinstance(aaf_component, aaf2.components.OperationGroup):
                        nested_aaf_segments = aaf_component.segments
                        for nested_otio_child, nested_aaf_segment in zip(
                                otio_child.each_child(), nested_aaf_segments):
                            self._is_otio_aaf_same(nested_otio_child,
                                                   nested_aaf_segment)
                    else:
                        self._is_otio_aaf_same(otio_child, aaf_component)

        # Inspect the OTIO -> AAF -> OTIO file
        roundtripped_otio = otio.adapters.read_from_file(tmp_aaf_path, simplify=True)

        self.assertIsNotNone(roundtripped_otio)
        self.assertTrue(isinstance(roundtripped_otio, otio.schema.Timeline))
        self.assertEqual(otio_timeline.name, roundtripped_otio.name)
        self.assertEqual(otio_timeline.duration().rate,
                         roundtripped_otio.duration().rate)

    def _verify_compositionmob_sourceclip_structure(self, compmob_clip):
        self.assertTrue(isinstance(compmob_clip, SourceClip))
        self.assertTrue(isinstance(compmob_clip.mob, MasterMob))
        mastermob = compmob_clip.mob
        for mastermob_slot in mastermob.slots:
            mastermob_clip = mastermob_slot.segment
            self.assertTrue(isinstance(mastermob_clip, SourceClip))
            self.assertTrue(isinstance(mastermob_clip.mob, SourceMob))
            filemob = mastermob_clip.mob

            self.assertEqual(1, len(filemob.slots))
            filemob_clip = filemob.slots[0].segment

            self.assertTrue(isinstance(filemob_clip, SourceClip))
            self.assertTrue(isinstance(filemob_clip.mob, SourceMob))
            tapemob = filemob_clip.mob
            self.assertTrue(len(tapemob.slots) >= 2)

            timecode_slots = [tape_slot for tape_slot in tapemob.slots
                              if isinstance(tape_slot.segment,
                                            Timecode)]

            self.assertEqual(1, len(timecode_slots))

            for tape_slot in tapemob.slots:
                tapemob_component = tape_slot.segment
                if not isinstance(tapemob_component, Timecode):
                    self.assertTrue(isinstance(tapemob_component, SourceClip))
                    tapemob_clip = tapemob_component
                    self.assertEqual(None, tapemob_clip.mob)
                    self.assertEqual(None, tapemob_clip.slot)
                    self.assertEqual(0, tapemob_clip.slot_id)

    def _is_otio_aaf_same(self, otio_child, aaf_component):
        if isinstance(aaf_component, SourceClip):
            orig_mob_id = str(otio_child.metadata["AAF"]["SourceID"])
            dest_mob_id = str(aaf_component.mob.mob_id)
            self.assertEqual(orig_mob_id, dest_mob_id)

        if isinstance(aaf_component, (SourceClip, Filler)):
            orig_duration = otio_child.visible_range().duration.value
            dest_duration = aaf_component.length
            self.assertEqual(orig_duration, dest_duration)

        if isinstance(aaf_component, Transition):
            orig_pointlist = otio_child.metadata["AAF"]["PointList"]
            params = aaf_component["OperationGroup"].value.parameters
            varying_value = [param for param in params if isinstance(param,
                                                                     VaryingValue)][0]
            dest_pointlist = varying_value.getvalue("PointList")
            for orig_point, dest_point in zip(orig_pointlist, dest_pointlist):
                self.assertEqual(orig_point["Value"], dest_point.value)
                self.assertEqual(orig_point["Time"], dest_point.time)


class SimplifyTests(unittest.TestCase):
    def test_aaf_simplify(self):
        aaf_path = SIMPLE_EXAMPLE_PATH
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
            self.assertNotEqual(type(track[0]), otio.schema.Track)
            self.assertEqual(len(track), 5)

    def test_aaf_no_simplify(self):
        aaf_path = SIMPLE_EXAMPLE_PATH
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

    def test_simplify_top_level_track(self):
        """Test for cases where a track has a single item but should not be
        collapsed because it is the the last track in the stack ie:

        TL
            tracks Stack
                track1
                    clip

        in this case, track1 should not be pruned.
        """

        # get the simplified form of the clip
        tl = otio.adapters.read_from_file(ONE_AUDIO_CLIP_PATH, simplify=True)

        # ensure that we end up with a track that contains a clip
        self.assertEqual(type(tl.tracks[0]), otio.schema.Track)
        self.assertEqual(tl.tracks[0].kind, otio.schema.TrackKind.Audio)
        self.assertEqual(type(tl.tracks[0][0]), otio.schema.Clip)

    def test_simplify_track_stack_track(self):
        tl = otio.schema.Timeline()
        tl.tracks.append(otio.schema.Track())
        tl.tracks[0].append(otio.schema.Stack())
        tl.tracks[0][0].append(otio.schema.Track())
        tl.tracks[0][0][0].append(otio.schema.Clip())

        from opentimelineio_contrib.adapters import advanced_authoring_format
        simple_tl = advanced_authoring_format._simplify(tl)

        self.assertEqual(
            type(simple_tl.tracks[0][0]), otio.schema.Clip
        )

        tl = otio.schema.Timeline()
        tl.tracks.append(otio.schema.Track())
        tl.tracks[0].append(otio.schema.Stack())
        tl.tracks[0][0].append(otio.schema.Track())
        tl.tracks[0][0][0].append(otio.schema.Track())
        tl.tracks[0][0][0][0].append(otio.schema.Clip())

        from opentimelineio_contrib.adapters import advanced_authoring_format
        simple_tl = advanced_authoring_format._simplify(tl)

        # top level thing should not be a clip
        self.assertEqual(
            type(simple_tl.tracks[0]), otio.schema.Track
        )
        self.assertEqual(
            type(simple_tl.tracks[0][0]), otio.schema.Clip
        )

    def test_simplify_stack_clip_clip(self):
        tl = otio.schema.Timeline()
        tl.tracks.append(otio.schema.Track())
        tl.tracks[0].append(otio.schema.Stack())
        tl.tracks[0][0].append(otio.schema.Clip())
        tl.tracks[0][0].append(otio.schema.Clip())

        from opentimelineio_contrib.adapters import advanced_authoring_format
        simple_tl = advanced_authoring_format._simplify(tl)

        self.assertNotEqual(
            type(simple_tl.tracks[0]), otio.schema.Clip
        )
        self.assertEqual(
            type(simple_tl.tracks[0][0]), otio.schema.Stack
        )

    def test_simplify_stack_track_clip(self):
        tl = otio.schema.Timeline()
        tl.tracks.append(otio.schema.Track())
        tl.tracks[0].append(otio.schema.Stack())
        tl.tracks[0][0].append(otio.schema.Track())
        tl.tracks[0][0][0].append(otio.schema.Clip())
        tl.tracks[0][0].append(otio.schema.Track())
        tl.tracks[0][0][1].append(otio.schema.Clip())

        from opentimelineio_contrib.adapters import advanced_authoring_format
        simple_tl = advanced_authoring_format._simplify(tl)

        # None of the things in the top level stack should be a clip
        for i in simple_tl.tracks:
            self.assertNotEqual(type(i), otio.schema.Clip)


if __name__ == '__main__':
    unittest.main()
