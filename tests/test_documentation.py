# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test cases to verify examples used in the OTIO documentation."""

import os
import unittest

import opentimelineio as otio


SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
CLIP_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "clip_example.otio")


class DocTester(unittest.TestCase):

    def test_clip(self):
        timeline = otio.adapters.read_from_file(CLIP_EXAMPLE_PATH)
        track = timeline.tracks[0]
        gapA, clip, transition, gapB = track[:]

        self.assertEqual(
            otio.opentime.RationalTime(19, 24),
            track.duration()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(19, 24)
            ),
            track.trimmed_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(19, 24)
            ),
            track.available_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(19, 24)
            ),
            track.visible_range()
        )

        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(8, 24),
                duration=otio.opentime.RationalTime(3, 24)
            ),
            track.trimmed_range_of_child(clip)
        )
        self.assertEqual(
            (
                None,
                otio.opentime.RationalTime(1, 24)
            ),
            track.handles_of_child(clip)
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(8, 24),
                duration=otio.opentime.RationalTime(3, 24)
            ),
            track.trimmed_range_of_child(clip)
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(8, 24),
                duration=otio.opentime.RationalTime(3, 24)
            ),
            track.range_of_child(clip)
        )

        self.assertEqual(
            otio.opentime.RationalTime(8, 24),
            gapA.duration()
        )

        self.assertEqual(
            otio.opentime.RationalTime(3, 24),
            clip.duration()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(8, 24),
                duration=otio.opentime.RationalTime(3, 24)
            ),
            clip.trimmed_range_in_parent()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(8, 24),
                duration=otio.opentime.RationalTime(3, 24)
            ),
            clip.range_in_parent()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(3, 24),
                duration=otio.opentime.RationalTime(3, 24)
            ),
            clip.trimmed_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(3, 24),
                duration=otio.opentime.RationalTime(4, 24)
            ),
            clip.visible_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(8, 24)
            ),
            clip.available_range()
        )
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(8, 24)
            ),
            clip.media_reference.available_range
        )

        self.assertEqual(
            otio.opentime.RationalTime(2, 24),
            transition.in_offset
        )
        self.assertEqual(
            otio.opentime.RationalTime(1, 24),
            transition.out_offset
        )

        self.assertEqual(
            otio.opentime.RationalTime(8, 24),
            gapB.duration()
        )


if __name__ == '__main__':
    unittest.main()
