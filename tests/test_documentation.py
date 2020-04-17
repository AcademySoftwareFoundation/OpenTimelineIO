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
