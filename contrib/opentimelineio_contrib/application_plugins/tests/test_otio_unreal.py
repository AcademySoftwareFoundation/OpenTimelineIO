# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the otio_unreal plugin"""

import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

import opentimelineio as otio
from opentimelineio.opentime import RationalTime, TimeRange

from otio_unreal import (
    METADATA_KEY_UE,
    import_otio,
    export_otio,
    set_sub_sequence_path,
    get_sub_sequence_path,
    LevelSequenceProxy,
    ShotSectionProxy,
)


class OTIOUnrealIOTest(unittest.TestCase):
    """Test case to validate interchange between OTIO and Unreal
    Engine with ``otio_unreal`` Python API.
    """

    FRAME_RATE = 24.0

    TIME_1SEC = RationalTime(24, FRAME_RATE)
    TIME_2SEC = RationalTime(48, FRAME_RATE)
    TIME_4SEC = RationalTime(96, FRAME_RATE)
    TIME_7SEC = RationalTime(168, FRAME_RATE)

    RANGE_1SEC = TimeRange(duration=TIME_1SEC)
    RANGE_2SEC = TimeRange(duration=TIME_2SEC)
    RANGE_4SEC = TimeRange(duration=TIME_4SEC)
    RANGE_7SEC = TimeRange(duration=TIME_7SEC)

    PROJ_ROOT = Path("/Game/Test")
    SEQ_ROOT = PROJ_ROOT / "Sequences"

    @contextmanager
    def no_max_diff(self):
        """Temporarily remove diff limit to clearly describe JSON
        differences.
        """
        prev_max_diff = self.maxDiff
        self.maxDiff = None

        yield

        self.maxDiff = prev_max_diff

    def build_test_timeline(self):
        """Build OTIO timeline which tests core otio_unreal features.

        Returns:
            otio.schema.Timeline: Test timeline
        """
        # Project - nested sequences
        proj_timeline = otio.schema.Timeline(
            global_start_time=RationalTime(0, self.FRAME_RATE)
        )
        set_sub_sequence_path(
            proj_timeline.tracks, (self.PROJ_ROOT / "Test.Test").as_posix()
        )

        proj_track1 = otio.schema.Track(name="Video Track 1")
        proj_timeline.tracks.append(proj_track1)

        proj_gap1 = otio.schema.Gap(source_range=self.RANGE_1SEC)
        proj_track1.append(proj_gap1)

        # Sequence A - single track
        seq_a_root = self.SEQ_ROOT / "A"
        seq_a_shots_root = seq_a_root / "Shots"

        seq_a_stack = otio.schema.Stack(name="Test_A", source_range=self.RANGE_7SEC)
        set_sub_sequence_path(seq_a_stack, (seq_a_root / "Test_A.Test_A").as_posix())
        proj_track1.append(seq_a_stack)

        seq_a_track1 = otio.schema.Track(name="Video Track 1")
        seq_a_stack.append(seq_a_track1)

        # Sequence A shots
        # No time warp or offset
        shot_a1_clip = otio.schema.Clip(name="Test_A001", source_range=self.RANGE_1SEC)
        shot_a1_clip.media_reference = otio.schema.MissingReference(
            available_range=self.RANGE_1SEC
        )
        set_sub_sequence_path(
            shot_a1_clip, (seq_a_shots_root / "Test_A001.Test_A001").as_posix()
        )
        seq_a_track1.append(shot_a1_clip)

        # Linear time warp scale up
        shot_a2_clip = otio.schema.Clip(
            name="Test_A002",
            source_range=TimeRange(start_time=self.TIME_1SEC, duration=self.TIME_1SEC),
        )
        shot_a2_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(
                start_time=self.TIME_1SEC, duration=self.TIME_2SEC
            )
        )
        shot_a2_clip.effects.append(otio.schema.LinearTimeWarp(time_scalar=2.0))
        set_sub_sequence_path(
            shot_a2_clip, (seq_a_shots_root / "Test_A002.Test_A002").as_posix()
        )
        seq_a_track1.append(shot_a2_clip)

        # Linear time warp scale down
        shot_a3_clip = otio.schema.Clip(
            name="Test_A003", source_range=TimeRange(duration=self.TIME_2SEC)
        )
        shot_a3_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(duration=self.TIME_1SEC)
        )
        shot_a3_clip.effects.append(otio.schema.LinearTimeWarp(time_scalar=0.5))
        set_sub_sequence_path(
            shot_a3_clip, (seq_a_shots_root / "Test_A003.Test_A003").as_posix()
        )
        seq_a_track1.append(shot_a3_clip)

        # Positive start frame offset
        shot_a4_clip = otio.schema.Clip(
            name="Test_A004",
            source_range=TimeRange(start_time=self.TIME_2SEC, duration=self.TIME_1SEC),
        )
        shot_a4_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(
                start_time=self.TIME_1SEC, duration=self.TIME_2SEC
            )
        )
        set_sub_sequence_path(
            shot_a4_clip, (seq_a_shots_root / "Test_A004.Test_A004").as_posix()
        )
        seq_a_track1.append(shot_a4_clip)

        # Negative start frame offset
        shot_a5_clip = otio.schema.Clip(
            name="Test_A005",
            source_range=TimeRange(start_time=self.TIME_1SEC, duration=self.TIME_2SEC),
        )
        shot_a5_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(
                start_time=self.TIME_2SEC, duration=self.TIME_2SEC
            )
        )
        set_sub_sequence_path(
            shot_a5_clip, (seq_a_shots_root / "Test_A005.Test_A005").as_posix()
        )
        seq_a_track1.append(shot_a5_clip)

        # Markers
        for item in [seq_a_stack, shot_a2_clip]:
            for i, (color, color_name) in enumerate(
                [
                    (otio.schema.MarkerColor.RED, "red"),
                    (otio.schema.MarkerColor.PINK, "pink"),
                    (otio.schema.MarkerColor.ORANGE, "orange"),
                    (otio.schema.MarkerColor.YELLOW, "yellow"),
                    (otio.schema.MarkerColor.GREEN, "green"),
                    (otio.schema.MarkerColor.CYAN, "cyan"),
                    (otio.schema.MarkerColor.BLUE, "blue"),
                    (otio.schema.MarkerColor.PURPLE, "purple"),
                    (otio.schema.MarkerColor.MAGENTA, "magenta"),
                    (otio.schema.MarkerColor.WHITE, "white"),
                    (otio.schema.MarkerColor.BLACK, "black"),
                ]
            ):
                item.markers.append(
                    otio.schema.Marker(
                        name=color_name,
                        marked_range=TimeRange(
                            start_time=RationalTime(
                                item.source_range.start_time.to_frames() + i,
                                self.FRAME_RATE,
                            ),
                            duration=RationalTime(1, self.FRAME_RATE),
                        ),
                        color=color,
                    )
                )

        # Sequence B - multi track
        seq_b_root = self.SEQ_ROOT / "B"
        seq_b_shots_root = seq_b_root / "Shots"

        seq_b_stack = otio.schema.Stack(name="Test_B", source_range=self.RANGE_4SEC)
        set_sub_sequence_path(seq_b_stack, (seq_b_root / "Test_B.Test_B").as_posix())
        proj_track1.append(seq_b_stack)

        seq_b_track1 = otio.schema.Track(name="Video Track 1")
        seq_b_stack.append(seq_b_track1)
        seq_b_track2 = otio.schema.Track(name="Video Track 2")
        seq_b_stack.append(seq_b_track2)

        # Sequence B shots
        # Track 1: |  gap  |  clip  |
        seq_b_gap1 = otio.schema.Gap(source_range=self.RANGE_1SEC)
        seq_b_track1.append(seq_b_gap1)

        # Matching media reference range
        shot_b2_clip = otio.schema.Clip(
            name="Test_B002",
            source_range=TimeRange(start_time=self.TIME_2SEC, duration=self.TIME_2SEC),
        )
        shot_b2_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(
                start_time=self.TIME_2SEC, duration=self.TIME_2SEC
            )
        )
        set_sub_sequence_path(
            shot_b2_clip, (seq_b_shots_root / "Test_B002.Test_B002").as_posix()
        )
        seq_b_track1.append(shot_b2_clip)

        # Track 2: |  clip  |  gap  |  clip  |
        # Trimmed section within long media reference
        shot_b1_clip = otio.schema.Clip(
            name="Test_B001",
            source_range=TimeRange(start_time=self.TIME_4SEC, duration=self.TIME_1SEC),
        )
        shot_b1_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(duration=self.TIME_7SEC)
        )
        set_sub_sequence_path(
            shot_b1_clip, (seq_b_shots_root / "Test_B001.Test_B001").as_posix()
        )
        seq_b_track2.append(shot_b1_clip)

        seq_b_gap2 = otio.schema.Gap(source_range=self.RANGE_2SEC)
        seq_b_track2.append(seq_b_gap2)

        # Media reference with negative start time
        shot_b3_clip = otio.schema.Clip(name="Test_B003", source_range=self.RANGE_1SEC)
        shot_b3_clip.media_reference = otio.schema.MissingReference(
            available_range=TimeRange(
                start_time=-self.TIME_2SEC, duration=self.TIME_4SEC
            )
        )
        set_sub_sequence_path(
            shot_b3_clip, (seq_b_shots_root / "Test_B003.Test_B003").as_posix()
        )
        seq_b_track2.append(shot_b3_clip)

        return proj_timeline

    def assert_shot_section(self, item, shot_section_proxy):
        """Assert that an Unreal shot section matches the expected
        characteristics of its associated OTIO item.

        Args:
            item (otio.schema.Item): Associated item
            shot_section_proxy (ShotSectionProxy): Shot section to test
        """
        # Sub-sequence exists
        sub_seq = shot_section_proxy.section.get_sequence()
        self.assertIsNotNone(sub_seq)

        sub_seq_proxy = LevelSequenceProxy(sub_seq, shot_section_proxy)
        sub_seq_source_range = sub_seq_proxy.get_source_range()

        # Shot display name == item name
        self.assertEqual(shot_section_proxy.section.get_shot_display_name(), item.name)

        # Sub-sequence path == item metadata
        self.assertEqual(sub_seq.get_path_name(), get_sub_sequence_path(item))

        # Frame rate
        self.assertEqual(
            sub_seq_proxy.get_frame_rate(), item.source_range.start_time.rate
        )

        # Section range == range in parent
        self.assertEqual(
            shot_section_proxy.get_range_in_parent(), item.range_in_parent()
        )

        # Visible playback range == source range
        self.assertEqual(sub_seq_source_range, item.source_range)

        if (
            hasattr(item, "media_reference")
            and item.media_reference
            and item.media_reference.available_range
        ):
            # Playback range == media reference available range
            self.assertEqual(
                sub_seq_proxy.get_available_range(),
                item.media_reference.available_range,
            )

            # Time offset == source range start frame - available range start frame
            self.assertEqual(
                shot_section_proxy.get_start_frame_offset(),
                item.source_range.start_time.to_frames()
                - item.media_reference.available_range.start_time.to_frames(),
            )

        else:
            # Playback range == source range if no media reference
            self.assertEqual(
                sub_seq_proxy.get_available_range(),
                item.source_range,
            )

        # Work range >= trimmed range
        self.assertLessEqual(
            sub_seq.get_work_range_start(), sub_seq_source_range.start_time.to_seconds()
        )
        self.assertGreaterEqual(
            sub_seq.get_work_range_end(),
            sub_seq_source_range.end_time_exclusive().to_seconds(),
        )

        # View range >= trimmed range
        self.assertLessEqual(
            sub_seq.get_view_range_start(), sub_seq_source_range.start_time.to_seconds()
        )
        self.assertGreaterEqual(
            sub_seq.get_view_range_end(),
            sub_seq_source_range.end_time_exclusive().to_seconds(),
        )

        if item.effects:
            for effect in item.effects:
                if isinstance(effect, otio.schema.LinearTimeWarp):
                    # Linear time warm == section time scale
                    self.assertEqual(
                        effect.time_scalar, shot_section_proxy.get_time_scale()
                    )

        return sub_seq_proxy

    def test_roundtrip(self):
        """Test that an OTIO timeline can be imported to an Unreal
        level sequence hierarchy, and then exported back to an OTIO
        timeline, matching the source 1:1.

        Note:
            While this roundtrip must be lossless and covers most
            supported OTIO -> Unreal -> OTIO features, not all OTIO
            features are supported, and there are cases where supported
            features may roundtrip with a lossy result due to the
            limited feature matrix of this plugin.
        """
        temp_dir = tempfile.TemporaryDirectory()
        in_otio_path = Path(temp_dir.name) / "test_timeline_in.otio"
        out_otio_path = Path(temp_dir.name) / "test_timeline_out.otio"

        # OTIO -> UE
        # ----------
        in_timeline = self.build_test_timeline()
        otio.adapters.write_to_file(in_timeline, str(in_otio_path))

        proj_level_seq, in_timeline = import_otio(str(in_otio_path))

        # Verify project
        self.assertEqual(
            proj_level_seq.get_path_name(), get_sub_sequence_path(in_timeline.tracks)
        )
        proj_level_seq_proxy = LevelSequenceProxy(proj_level_seq)
        proj_shot_track = proj_level_seq_proxy.get_shot_track()
        self.assertIsNotNone(proj_shot_track)
        proj_shot_sections = proj_shot_track.get_sections()
        self.assertEqual(len(proj_shot_sections), 2)

        # Verify sequence A
        seq_a_item = in_timeline.tracks[0][1]
        seq_a_shot_section_proxy = ShotSectionProxy(
            proj_shot_sections[0], proj_level_seq_proxy
        )
        seq_a_level_seq_proxy = self.assert_shot_section(
            seq_a_item, seq_a_shot_section_proxy
        )
        seq_a_shot_track = seq_a_level_seq_proxy.get_shot_track()
        self.assertIsNotNone(seq_a_shot_track)
        seq_a_shot_sections = seq_a_shot_track.get_sections()
        self.assertEqual(len(seq_a_shot_sections), 5)

        # Verify sequence A shots
        for i in range(5):
            self.assert_shot_section(
                seq_a_item[0][i],
                ShotSectionProxy(seq_a_shot_sections[i], seq_a_level_seq_proxy),
            )

        # Verify sequence B
        seq_b_item = in_timeline.tracks[0][2]
        seq_b_shot_section_proxy = ShotSectionProxy(
            proj_shot_sections[1], proj_level_seq_proxy
        )
        seq_b_level_seq_proxy = self.assert_shot_section(
            seq_b_item, seq_b_shot_section_proxy
        )
        seq_b_shot_track = seq_b_level_seq_proxy.get_shot_track()
        self.assertIsNotNone(seq_b_shot_track)
        seq_b_shot_sections = seq_b_shot_track.get_sections()
        self.assertEqual(len(seq_b_shot_sections), 3)

        # Verify sequence B shots
        self.assert_shot_section(
            seq_b_item[0][1],
            ShotSectionProxy(seq_b_shot_sections[2], seq_b_level_seq_proxy),
        )
        self.assert_shot_section(
            seq_b_item[1][0],
            ShotSectionProxy(seq_b_shot_sections[0], seq_b_level_seq_proxy),
        )
        self.assert_shot_section(
            seq_b_item[1][2],
            ShotSectionProxy(seq_b_shot_sections[1], seq_b_level_seq_proxy),
        )

        # UE -> OTIO
        # ----------
        out_timeline = export_otio(str(out_otio_path), proj_level_seq)

        # Remove all metadata except sub_sequence, so we can compare with
        # in_timeline.
        root_level_seq_path = get_sub_sequence_path(out_timeline.tracks)
        out_timeline.tracks.metadata.clear()
        set_sub_sequence_path(out_timeline.tracks, root_level_seq_path)

        for item in out_timeline.children_if():
            level_seq_path = get_sub_sequence_path(item)
            if level_seq_path is not None:

                # Verify expected metadata keys
                ue_metadata = item.metadata[METADATA_KEY_UE]
                self.assertTrue("timecode" in ue_metadata)
                self.assertTrue("is_active" in ue_metadata)
                self.assertTrue("is_locked" in ue_metadata)
                self.assertTrue("pre_roll_frames" in ue_metadata)
                self.assertTrue("post_roll_frames" in ue_metadata)
                self.assertTrue("can_loop" in ue_metadata)
                self.assertTrue("end_frame_offset" in ue_metadata)
                self.assertTrue("first_loop_start_frame_offset" in ue_metadata)
                self.assertTrue("hierarchical_bias" in ue_metadata)
                self.assertTrue("network_mask" in ue_metadata)

                item.metadata.clear()
                set_sub_sequence_path(item, level_seq_path)

        # JSON data should match between in and out timeline
        with self.no_max_diff():
            self.assertEqual(
                out_timeline.to_json_string(), in_timeline.to_json_string()
            )
