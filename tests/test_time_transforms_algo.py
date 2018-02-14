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


class RangeInTests(unittest.TestCase):
    def test_source_range(self):
        """Test using range_of to query for clip space."""

        tr = otio.schema.Track(name="Parent Track")
        rn = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 24),
            otio.opentime.RationalTime(20, 24),
        )
        src_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(10, 24),
            otio.opentime.RationalTime(20, 24),
        )
        mr_1 = otio.schema.ExternalReference(available_range=rn)
        tr.append(
            otio.schema.Clip(
                name='cl1',
                source_range=src_range,
                media_reference=mr_1
            )
        )
        tr.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(2, 24),
            otio.opentime.RationalTime(5, 24),
        )
        cl_1 = tr[0]

        argument_to_result_map = [
            # arg               # result
            ((cl_1, cl_1, cl_1), (10, 20)),
            ((cl_1, tr,   cl_1), (0, 20)),
            ((cl_1, cl_1, tr),   (12, 5)),
            ((cl_1, tr, tr),     (2, 5)),
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
