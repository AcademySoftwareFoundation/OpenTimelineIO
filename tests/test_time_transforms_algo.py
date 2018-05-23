#
# Copyright 2018 Pixar Animation Studios
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

import opentimelineio as otio

__doc__ = """Test range_of function from algorithms."""

# @TODO: track that is shorter than a clip, both directions
# @TODO: track that is longer than a single clip, both directions
# @TODO: track within a track with a clip, both directions
# @TODO: case where you have a common parent


@unittest.skip
class RangeInTests(unittest.TestCase):
    def test_range_of_track_shorter_than_clip(self):
        """Test the range_of for a shorter track containing a longer clip."""

        # track starts at frame 2 and goes 5 frames
        tr = otio.schema.Track(name="Parent Track")
        tr.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(2, 24),
            otio.opentime.RationalTime(5, 24),
        )

        # media reference starts at frame 0 and goes 20 frames
        rn = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 24),
            otio.opentime.RationalTime(20, 24),
        )
        mr_1 = otio.schema.ExternalReference(available_range=rn)

        # clip starts at frame 10 and goes 8 frames
        src_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(10, 24),
            otio.opentime.RationalTime(20, 24),
        )
        test_clip = otio.schema.Clip(
            name='cl1',
            source_range=src_range,
            media_reference=mr_1
        )
        tr.append(test_clip)

        cl_1 = tr[0]

        # ranges
        # track: 2, 5
        # clip: 10, 20

        #   # arg               # result
        argument_to_result_map = [
            # from the clip up to the track
            ((cl_1, cl_1, cl_1), (10, 20)),
            ((cl_1, cl_1, tr),   (12, 5)),
            ((cl_1, tr,   cl_1), (0, 20)),
            ((cl_1, tr, tr),     (2, 5)),

            # from the track down to the clip
            ((tr, cl_1, cl_1), (12, 5)),
            # ((tr, cl_1, tr),   (12, 5)),
            # ((tr, tr,   cl_1), (2, 5)),
            # ((tr, tr, tr),     (2, 5)),
        ]

        for args, expected_result in argument_to_result_map:
            measured_result_range = otio.range_of(*args)
            measured_result = (
                measured_result_range.start_time.value,
                measured_result_range.duration.value
            )

            # make sure we didn't edit anything in place
            self.assertIsNot(measured_result, args[0].trimmed_range())
            self.assertIsNot(measured_result, args[1].trimmed_range())
            self.assertIsNot(measured_result, args[2].trimmed_range())

            self.assertEqual(measured_result, expected_result)

    def test_range_of_track_longer_than_clip(self):
        """Test the range_of for a longer track containing a shorter clip."""

        tr = otio.schema.Track(name="Parent Track")
        rn = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 24),
            otio.opentime.RationalTime(20, 24),
        )
        # src_range = otio.opentime.TimeRange(
        #     otio.opentime.RationalTime(10, 24),
        #     otio.opentime.RationalTime(20, 24),
        # )
        mr_1 = otio.schema.ExternalReference(available_range=rn)
        clip_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(2, 24),
            otio.opentime.RationalTime(5, 24),
        )
        # print tr.duration()
        for i in range(4):
            tr.append(
                otio.schema.Clip(
                    name='cl'+ str(i),
                    source_range=clip_range,
                    media_reference=mr_1
                )
            )

        # cl_1 = tr[2]

        # ranges
        # track: 0, 20
        # clip: 2, 5

        #   # arg               # result
        argument_to_result_map = [
            # from the clip up to the track
            # ((cl_1, cl_1, cl_1), (2, 5)),
            # ((cl_1, cl_1, tr),   (2, 5)),
            # ((cl_1, tr,   cl_1), (10, 5)),
            # ((cl_1, tr, tr),     (10, 5)),

            # from the track down to the clip
            # ((tr, cl_1, cl_1), (2, 5)), # (!!)
            # ((tr, cl_1, tr),   (-8, 20)),
            # ((tr, tr,   cl_1), (10, 5)), # (!!)
            # ((tr, tr, tr),     (0, 20)),
        ]

        for args, expected_result in argument_to_result_map:
            measured_result_range = otio.range_of(*args)
            measured_result = (
                measured_result_range.start_time.value,
                measured_result_range.duration.value
            )

            self.assertEqual(measured_result, expected_result)


if __name__ == '__main__':
    unittest.main()
