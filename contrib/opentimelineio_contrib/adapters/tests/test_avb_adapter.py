# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test the AVB adapter."""

# python
import os
import sys
import unittest

import opentimelineio as otio

try:
    # python2
    import StringIO as io
except ImportError:
    # python3
    import io

TRANSCRIPTION_RESULT = ""

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SIMPLE_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "simple.avb"
)
TRANSITIONS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "transitions.avb"
)
TRIMS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "trims.avb"
)
MULTITRACK_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "multitrack.avb"
)
PREFLATTENED_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "preflattened.avb"
)
NESTING_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "nesting_test.avb"
)
NESTED_STACK_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "nested_stack.avb"
)
NESTING_PREFLATTENED_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "nesting_test_preflattened.avb"
)
MISC_SPEED_EFFECTS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "misc_speed_effects.avb"
)
PRECHECK_FAIL_OTIO = os.path.join(
    SAMPLE_DATA_DIR,
    "precheckfail.otio"
)
LINEAR_SPEED_EFFECTS_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "linear_speed_effects.avb"
)
TIMCODE_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "timecode_test.avb"
)
MUTED_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "test_muted_clip.avb"
)
ESSENCE_GROUP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "essence_group.avb"
)
ONE_AUDIO_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "one_audio_clip.avb"
)
FPS30_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "30fps.avb"
)
FPS2997_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "2997fps.avb"
)
FPS2997_DFTC_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "2997fps-DFTC.avb"
)
DUPLICATES_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "duplicates.avb"
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
    "utf8.avb"
)
MULTIPLE_TOP_LEVEL_MOBS_CLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "multiple_top_level_mobs.avb"
)
GAPS_OTIO_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "gaps.otio"
)
COMPOSITE_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "composite.avb"
)

SUBCLIP_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "subclip_sourceclip_references_compositionmob_with_mastermob.avb"
)

COMPOSITION_METADATA_MASTERMOB_METADATA_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "normalclip_sourceclip_references_compositionmob_"
    "has_also_mastermob_usercomments.avb"
)

COMPOSITION_METADATA_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "normalclip_sourceclip_references_compositionmob_"
    "with_usercomments_no_mastermob_usercomments.avb"
)

MULTIPLE_TIMECODE_OBJECTS_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "multiple_timecode_objects.avb"
)

MULTIPLE_MARKERS_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "multiple_markers.avb"
)

KEYFRAMED_PROPERTIES_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "keyframed_properties.avb"
)

MARKER_OVER_TRANSITION_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "marker-over-transition.avb",
)

MARKER_OVER_AUDIO_PATH = os.path.join(
    SAMPLE_DATA_DIR,
    "marker-over-audio.avb"
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
    lib_path = os.environ.get("OTIO_AVB_PYTHON_LIB")
    if lib_path and lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    import avb  # noqa
    could_import_avb = True
except (ImportError):
    could_import_avb = False


@unittest.skipIf(
    not could_import_avb,
    "AVB module not found. You might need to set OTIO_AVB_PYTHON_LIB"
)
class AVBReaderTests(unittest.TestCase):
    def test_avb_read(self):
        avb_path = SIMPLE_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(avb_path)
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

    def test_avb_global_start_time(self):
        timeline = otio.adapters.read_from_file(SIMPLE_EXAMPLE_PATH)
        self.assertEqual(
            otio.opentime.from_timecode("01:00:00:00", 24),
            timeline.global_start_time
        )

    def skip_test_avb_global_start_time_NTSC_DFTC(self):
        timeline = otio.adapters.read_from_file(FPS2997_DFTC_PATH)
        # TODO : I don't understand this test
        self.assertEqual(
            otio.opentime.from_timecode("05:00:00;00", rate=(30000.0 / 1001)),
            timeline.global_start_time
        )

    def test_avb_read_trims(self):
        avb_path = TRIMS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(avb_path)
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

    def test_avb_read_transitions(self):
        avb_path = TRANSITIONS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(avb_path)
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
        avb_path = TIMCODE_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(avb_path)
        self.assertNotEqual(
            timeline.tracks[0][0].source_range.start_time,
            timeline.tracks[0][1].source_range.start_time
        )
        self.assertEqual(
            timeline.tracks[0][1].source_range.start_time,
            otio.opentime.RationalTime(86424, 24),
        )

    def test_avb_user_comments(self):
        avb_path = TRIMS_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(avb_path)
        self.assertIsNotNone(timeline)
        self.assertEqual(type(timeline), otio.schema.Timeline)
        self.assertIsNotNone(timeline.metadata.get("AVB"))
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
            avb_metadata = clip.media_reference.metadata.get("AVB")
            attribute_meta = avb_metadata.get("attributes")
            self.assertIsNotNone(attribute_meta)
            self.assertIsNotNone(attribute_meta.get("_USER"))
            self.assertEqual(
                attribute_meta.get("_USER").get("CustomTest"),
                correctWord
            )

    def test_avb_flatten_tracks(self):
        multitrack_timeline = otio.adapters.read_from_file(
            MULTITRACK_EXAMPLE_PATH, attach_markers=False
        )
        preflattened_timeline = otio.adapters.read_from_file(
            PREFLATTENED_EXAMPLE_PATH, attach_markers=False
        )

        # first make sure we got the structure we expected
        self.assertEqual(3, len(preflattened_timeline.tracks))
        self.assertEqual(1, len(preflattened_timeline.video_tracks()))
        self.assertEqual(2, len(preflattened_timeline.audio_tracks()))

        self.assertEqual(3, len(multitrack_timeline.video_tracks()))
        self.assertEqual(2, len(multitrack_timeline.audio_tracks()))
        # AVB doesn't have marker tracks like AAF which has 3 additional tracks
        self.assertEqual(5, len(multitrack_timeline.tracks))

        preflattened = preflattened_timeline.video_tracks()[0]
        self.assertEqual(7, len(preflattened))
        flattened = otio.algorithms.flatten_stack(
            multitrack_timeline.video_tracks()
        )
        self.assertEqual(7, len(flattened))

        # Lets remove some AVB metadata that will always be different
        # so we can compare everything else.
        for t in (preflattened, flattened):

            t.name = ""
            t.metadata.pop("AVB", None)

            for c in t.each_child():
                if hasattr(c, "media_reference") and c.media_reference:
                    mr = c.media_reference
                    mr.metadata.get("AVB", {}).pop('last_modified', None)
                    mr.metadata.get("AVB", {}).pop('attributes', None)
                meta = c.metadata.get("AVB", {})
                meta.pop('attributes', None)
                meta.pop('length', None)
                meta.pop('start_time', None)
                c.markers.clear()

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

    def test_avb_nesting(self):
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
        timeline = otio.adapters.read_from_file(MUTED_CLIP_PATH)
        self.assertIsInstance(timeline, otio.schema.Timeline)
        self.assertEqual(len(timeline.tracks), 1)
        track = timeline.tracks[0]
        self.assertEqual(len(track), 1)
        clip = track[0]
        self.assertIsInstance(clip, otio.schema.Clip)
        self.assertEqual(clip.name, 'Frame Debugger 0h.mov')
        self.assertEqual(clip.enabled, False)

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

    def skip_test_2997fps(self):
        # TODO not sure whats up with this
        tl = otio.adapters.read_from_file(FPS2997_CLIP_PATH)
        self.assertEqual(tl.duration().rate, 30000 / 1001.0)

    def test_utf8_names(self):
        # NOTE: AAF to AVB convert in MC resulted in different for name
        # on macOS vs Windows Ω -> ? this appears to be MC issue
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
        comment = first_clip.media_reference.metadata.get('AVB', {}) \
                                                     .get('attributes', {}) \
                                                     .get('_USER', {}) \
                                                     .get("Comments", "")
        self.assertEqual(
            comment.encode('utf-8'),
            (u"Comments_ABCXYZñçêœ•∑´®†¥¨ˆøπ“‘åß∂ƒ©˙∆˚¬…æΩ≈ç√∫˜µ≤≥÷").encode('utf-8')
        )

    def test_multiple_top_level_mobs(self):
        result = otio.adapters.read_from_file(MULTIPLE_TOP_LEVEL_MOBS_CLIP_PATH)
        self.assertIsInstance(result, otio.schema.SerializableCollection)
        self.assertEqual(2, len(result))

    def test_external_reference_from_unc_path(self):
        timeline = otio.adapters.read_from_file(SIMPLE_EXAMPLE_PATH)
        video_track = timeline.video_tracks()[0]
        first_clip = video_track[0]
        self.assertIsInstance(first_clip.media_reference,
                              otio.schema.ExternalReference)

        unc_path = first_clip.media_reference.metadata.get("AVB", {}) \
                                                      .get("attributes", {}) \
                                                      .get("_USER", {}) \
                                                      .get("UNC Path")
        unc_path = "file://" + unc_path
        self.assertEqual(
            first_clip.media_reference.target_url,
            unc_path
        )

    def test_external_reference_paths(self):
        timeline = otio.adapters.read_from_file(COMPOSITE_PATH)
        video_target_urls = [
            [
                "file:////animation/root/work/editorial/jburnell/700/1.aaf",
                "file:////animation/root/work/editorial/jburnell/700/2.aaf",
                "file:////animation/root/work/editorial/jburnell/700/3.aaf"
            ],
            [
                "file://C//Avid MediaFiles/MXF/1/700.Exported.03_Vi48896FA0V.mxf"
            ]
        ]
        audio_target_urls = [
            [
                "file://C//OMFI MediaFiles/700.ExportA01.5D8A14612890A.aif"
            ]
        ]

        for track_index, video_track in enumerate(timeline.video_tracks()):
            for clip_index, clip in enumerate(video_track):
                self.assertIsInstance(clip.media_reference,
                                      otio.schema.ExternalReference)
                self.assertEqual(clip.media_reference.target_url,
                                 video_target_urls[track_index][clip_index])

        for track_index, audio_track in enumerate(timeline.audio_tracks()):
            for clip_index, clip in enumerate(audio_track):
                self.assertIsInstance(clip.media_reference,
                                      otio.schema.ExternalReference)
                self.assertEqual(clip.media_reference.target_url,
                                 audio_target_urls[track_index][clip_index])

    def test_avb_subclip_metadata(self):
        """
        For subclips, the AVB SourceClip can actually reference a CompositionMob
        (instead of a MasterMob)
        In which case we need to drill down into the CompositionMob
        to find the MasterMob with the UserComments.
        """

        timeline = otio.adapters.read_from_file(SUBCLIP_PATH)
        audio_track = timeline.audio_tracks()[0]
        first_clip = audio_track[0]
        avb_metadata = first_clip.media_reference.metadata.get("AVB")

        expected_md = {"Director": "director_name",
                       "Line": "script_line",
                       "Talent": "Speaker",
                       "Logger": "logger",
                       "Character": "character_name"}

        self._verify_user_comments(avb_metadata, expected_md)

    def test_avb_sourcemob_usage(self):
        """
        Each clip stores it's source mob usage AVB value as metadata in`SourceMobUsage`.
        For sub-clips this value should be `Usage_SubClip`.
        """
        # `Usage_SubClip` value
        subclip_timeline = otio.adapters.read_from_file(SUBCLIP_PATH)
        subclip_usages = {"Subclip.BREATH": "subclip"}
        for clip in subclip_timeline.each_clip():
            self.assertEqual(
                clip.metadata.get("AVB", {}).get("SourceMobUsage"),
                subclip_usages[clip.name]
            )

        # no usage value
        simple_timeline = otio.adapters.read_from_file(SIMPLE_EXAMPLE_PATH)
        simple_usages = {
            "KOLL-HD.mp4": "",
            "brokchrd (loop)-HD.mp4": "",
            "out-b (loop)-HD.mp4": "",
            "t-hawk (loop)-HD.mp4": "",
            "tech.fux (loop)-HD.mp4": ""
        }
        for clip in simple_timeline.each_clip():
            self.assertEqual(
                clip.metadata.get("AVB", {}).get("SourceMobUsage", ""),
                simple_usages[clip.name]
            )

    def test_avb_composition_metadata(self):
        """
        For standard clips the AAF SourceClip can actually reference a
        CompositionMob (instead of a MasterMob) and the composition mob is holding the
        UserComments instead of the MasterMob.
        My guess is that the CompositionMob is used to share the same metadata
        between different SourceClips
        """

        timeline = otio.adapters.read_from_file(COMPOSITION_METADATA_PATH)

        audio_track = timeline.audio_tracks()[0]
        first_clip = audio_track[0]

        avb_metadata = first_clip.media_reference.metadata.get("AVB")

        expected_md = {"Director": "director",
                       "Line": "scriptline",
                       "Talent": "talent",
                       "Logger": "",
                       "Character": "character"}

        self._verify_user_comments(avb_metadata, expected_md)

    def test_avb_composition_metadata_mastermob(self):
        """
        For standard clips the AVB SourceClip can actually reference a
        CompositionMob (instead of a masterMob), the CompositionMob is holding
        UserComments AND the MasterMob is holding UserComments.
        In this case the masterMob has the valid UserComments (empirically determined)
        """

        timeline = otio.adapters.read_from_file(
            COMPOSITION_METADATA_MASTERMOB_METADATA_PATH)

        audio_track = timeline.audio_tracks()[0]
        first_clip = audio_track[0]

        avb_metadata = first_clip.media_reference.metadata.get("AVB")

        expected_md = {"Director": "director",
                       "Line": "scriptline",
                       "Talent": "talent",
                       "Logger": "logger",
                       "Character": "character"}

        self._verify_user_comments(avb_metadata, expected_md)

    def test_avb_multiple_timecode_objects(self):
        """
        Make sure we can read SourceClips with multiple timecode objects of the
        same start value and length.
        """

        timeline = otio.adapters.read_from_file(
            MULTIPLE_TIMECODE_OBJECTS_PATH)

        self.assertIsNotNone(timeline)

        video_track = timeline.video_tracks()[0]
        only_clip = video_track[0]

        available_range = only_clip.media_reference.available_range

        self.assertEqual(available_range.start_time.value, 86501.0)
        self.assertEqual(available_range.duration.value, 1981.0)

    def SKIP_test_avb_transcribe_log(self):
        """Excercise an aaf-adapter read with transcribe_logging enabled."""

        # capture output of debugging statements
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        otio.adapters.read_from_file(SUBCLIP_PATH, transcribe_log=True)
        result_stdout = sys.stdout.getvalue()
        result_stderr = sys.stderr.getvalue()

        sys.stdout = old_stdout
        sys.stderr = old_stderr

        # conform python 2 and 3 behavior
        result_stdout = result_stdout.replace("b'", "").replace("'", "")

        self.assertEqual(result_stdout, TRANSCRIPTION_RESULT)
        self.assertEqual(result_stderr, '')

    def test_avb_marker_over_transition(self):
        """
        Make sure we can transcibe this composition with markers over transition.
        """

        timeline = None

        try:
            timeline = otio.adapters.read_from_file(
                MARKER_OVER_TRANSITION_PATH
            )

        except Exception as e:
            print('[ERROR] Transcribing test sample data `{}` caused an exception: {}'.format(  # noqa
                os.path.basename(MARKER_OVER_TRANSITION_PATH),
                e)
            )

        self.assertIsNotNone(timeline)

    def test_avb_marker_over_audio_file(self):
        """
        Make sure we can transcibe markers over an audio AAF file.
        """

        timeline = None

        try:
            timeline = otio.adapters.read_from_file(
                MARKER_OVER_AUDIO_PATH
            )

        except Exception as e:
            print('[ERROR] Transcribing test sample data `{}` caused an exception: {}'.format(  # noqa
                os.path.basename(MARKER_OVER_AUDIO_PATH),
                e)
            )

        self.assertIsNotNone(timeline)

        # Verify markers
        # We expect 1 track with 3 markers on it from the test data.
        self.assertTrue(1 == len(timeline.tracks))

        track = timeline.tracks[0]
        clip = track[0]

        self.assertEqual(3, len(clip.markers))

        fps = 24.0
        expected_markers = [
            {
                'color': 'RED',
                'label': 'm1',
                'start_time': otio.opentime.from_frames(86450.0, fps)
            },
            {
                'color': 'GREEN',
                'label': 'm2',
                'start_time': otio.opentime.from_frames(86503.0, fps)
            },
            {
                'color': 'BLUE',
                'label': 'm3',
                'start_time': otio.opentime.from_frames(86566.0, fps)
            }
        ]

        for index, marker in enumerate(clip.markers):
            expected_marker = expected_markers[index]

            color = marker.color
            label = marker.metadata.get('AVB', {}) \
                                   .get('attributes', {}) \
                                   .get("_ATN_CRM_USER")
            start_time = marker.marked_range.start_time

            self.assertEqual(color, expected_marker.get('color'))
            self.assertEqual(label, expected_marker.get('label'))
            self.assertEqual(start_time, expected_marker.get('start_time'))

    def _verify_user_comments(self, avb_metadata, expected_md):

        self.assertTrue(avb_metadata is not None)

        attribute_meta = avb_metadata.get("attributes", {})
        self.assertTrue("_USER" in attribute_meta.keys())

        user_comments = attribute_meta['_USER']

        user_comment_keys = user_comments.keys()
        for k, v in expected_md.items():
            self.assertTrue(k in user_comment_keys)
            self.assertEqual(user_comments[k], v)

    def test_attach_markers(self):
        """Check if markers are correctly translated and attached to the right items.
        """
        timeline = otio.adapters.read_from_file(MULTIPLE_MARKERS_PATH,
                                                attach_markers=True)

        expected_markers = {
            (0, 'Timecode'): [
                ('GREEN: TC1: zts02_1080: f1206: seq.f2604',
                 1795.0, 1.0, 24.0, 'GREEN')
            ],
            (1, 'Filler'): [('PUBLISH', 0.0, 1.0, 24.0, 'RED')],
            (1, 'zts02_1010'): [
                ('GREEN: V1: zts02_1010: f1104: seq.f1104',
                 1104.0, 1.0, 24.0, 'GREEN')
            ],
            (2, 'Filler'): [
                ('FX', 0.0, 1.0, 24.0, 'YELLOW'),
                ('BLUE: V2 (no FX): zts02_1020: f1134: seq.f1327',
                 518.0, 1.0, 24.0, 'BLUE')
            ],
            (3, 'Filler'): [
                ('INSERT', 0.0, 1.0, 24.0, 'CYAN'),
                ('CYAN: V3: zts02_1030: f1212: seq.f1665',
                 856.0,
                 1.0,
                 24.0,
                 'CYAN')
            ],
            (4, 'Drop_24.mov'): [
                ('MAGENTA: V4: zts02_1040: f1001: seq.f1666',
                 86400.0, 1.0, 24.0, 'MAGENTA')
            ],
            (5, 'Filler'): [
                ('RED: V5: zts02_1050: f1061: seq.f1885',
                 884.0, 1.0, 24.0, 'RED')
            ]
        }

        all_markers = {}
        for i, track in enumerate(
                timeline.each_child(descended_from_type=otio.schema.Track)
        ):
            for item in track.each_child():
                markers = [
                    (
                        m.name,
                        m.marked_range.start_time.value,
                        m.marked_range.duration.value,
                        m.marked_range.start_time.rate,
                        m.color
                    ) for m in item.markers
                ]
                if markers:
                    all_markers[(i, item.name)] = markers
        self.assertEqual(all_markers, expected_markers)

    def SKIP_test_keyframed_properties(self):
        def get_expected_dict(timeline):
            expected = []
            for clip in timeline.each_child(descended_from_type=otio.schema.Clip):
                for effect in clip.effects:
                    props = {}
                    parameters = effect.metadata.get("AAF", {}).get("Parameters", {})
                    for paramName, paramValue in parameters.items():
                        try:
                            is_animated = "_avb_keyframed_property" in paramValue
                        except (TypeError, KeyError):
                            is_animated = False
                        try:
                            baked_count = len(paramValue["keyframe_baked_values"])
                        except (TypeError, KeyError):
                            baked_count = None
                        props[paramName] = {"keyframed": is_animated,
                                            "baked_sample_count": baked_count}
                    expected.append(props)
            return expected

        tl_unbaked = otio.adapters.read_from_file(KEYFRAMED_PROPERTIES_PATH,
                                                  bake_keyframed_properties=False)

        tl_baked = otio.adapters.read_from_file(KEYFRAMED_PROPERTIES_PATH,
                                                bake_keyframed_properties=True)

        expected_unbaked = [
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_SCALE_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_SCALE_X_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_SCALE_Y_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_ROT_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_ROT_X_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_ROT_Y_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_ROT_Z_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
                "Vergence": {"baked_sample_count": None, "keyframed": True},
            },
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_POS_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_POS_X_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_POS_Y_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_POS_Z_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
                "Vergence": {"baked_sample_count": None, "keyframed": True},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": None, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": None,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": None, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": None,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": None, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": None,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": None, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": None,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": None, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": None,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_PRSP_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_PRSP_X_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_PRSP_Y_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_PRSP_Z_U": {"baked_sample_count": None, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
                "Vergence": {"baked_sample_count": None, "keyframed": True},
            },
        ]

        expected_baked = [
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_SCALE_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_SCALE_X_U": {"baked_sample_count": 212, "keyframed": True},
                "DVE_SCALE_Y_U": {"baked_sample_count": 212, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_ROT_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_ROT_X_U": {"baked_sample_count": 159, "keyframed": True},
                "DVE_ROT_Y_U": {"baked_sample_count": 159, "keyframed": True},
                "DVE_ROT_Z_U": {"baked_sample_count": 159, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
                "Vergence": {"baked_sample_count": 159, "keyframed": True},
            },
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_POS_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_POS_X_U": {"baked_sample_count": 116, "keyframed": True},
                "DVE_POS_Y_U": {"baked_sample_count": 116, "keyframed": True},
                "DVE_POS_Z_U": {"baked_sample_count": 116, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
                "Vergence": {"baked_sample_count": 116, "keyframed": True},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": 276, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": 276,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": 182, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": 182,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": 219, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": 219,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": 193, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": 193,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AvidMotionInputFormat": {"baked_sample_count": None,
                                          "keyframed": False},
                "AvidMotionOutputFormat": {"baked_sample_count": None,
                                           "keyframed": False},
                "AvidMotionPulldown": {"baked_sample_count": None, "keyframed": False},
                "AvidPhase": {"baked_sample_count": None, "keyframed": False},
                "PARAM_SPEED_MAP_U": {"baked_sample_count": 241, "keyframed": True},
                "PARAM_SPEED_OFFSET_MAP_U": {"baked_sample_count": 241,
                                             "keyframed": True},
                "SpeedRatio": {"baked_sample_count": None, "keyframed": False},
            },
            {
                "AFX_FIXED_ASPECT_U": {"baked_sample_count": None, "keyframed": False},
                "AvidEffectID": {"baked_sample_count": None, "keyframed": False},
                "AvidParameterByteOrder": {"baked_sample_count": None,
                                           "keyframed": False},
                "DVE_BORDER_ENABLED_U": {"baked_sample_count": None,
                                         "keyframed": False},
                "DVE_DEFOCUS_MODE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_FG_KEY_HIGH_SAT_U": {"baked_sample_count": None,
                                          "keyframed": False},
                "DVE_MT_WARP_FOREGROUND_U": {"baked_sample_count": None,
                                             "keyframed": False},
                "DVE_PRSP_ENABLED_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_PRSP_X_U": {"baked_sample_count": 241, "keyframed": True},
                "DVE_PRSP_Y_U": {"baked_sample_count": 241, "keyframed": True},
                "DVE_PRSP_Z_U": {"baked_sample_count": 241, "keyframed": True},
                "DVE_TRACKING_POS_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_AMPLT_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_CURVE_U": {"baked_sample_count": None, "keyframed": False},
                "DVE_WARP_FREQ_U": {"baked_sample_count": None, "keyframed": False},
                "Vergence": {"baked_sample_count": 241, "keyframed": True},
            },
        ]

        self.assertEqual(get_expected_dict(tl_unbaked), expected_unbaked)
        self.assertEqual(get_expected_dict(tl_baked), expected_baked)


if __name__ == '__main__':
    unittest.main()
