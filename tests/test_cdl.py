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

# python
import os
import unittest

import opentimelineio as otio

__doc__ = """Test CDL support in the EDL adapter."""

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
CDL_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "cdl.edl")


class CDLAdapterTest(unittest.TestCase):
    def test_cdl_read(self):
        edl_path = CDL_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 1)
        self.assertEqual(len(timeline.tracks[0]), 2)
        for clip in timeline.tracks[0]:
            # clip = timeline.tracks[0][0]
            self.assertEqual(
                clip.name,
                "ZZ100_501 (LAY3)"
            )
            self.assertEqual(
                clip.source_range.duration,
                otio.opentime.from_timecode("00:00:01:07", 24)
            )
            cdl = clip.metadata.get("cdl", {})
            self.assertEqual(
                cdl.get("asc_sat"),
                0.9
            )
            self.assertEqual(
                cdl.get("asc_sop").get("slope"),
                [0.1, 0.2, 0.3]
            )
            self.assertEqual(
                cdl.get("asc_sop").get("offset"),
                [1.0000, -0.0122, 0.0305]
            )
            self.assertEqual(
                cdl.get("asc_sop").get("power"),
                [1.0000, 0.0000, 1.0000]
            )

    def test_cdl_round_trip(self):
        original = """TITLE: Example_Screening.01

001  AX       V     C        01:00:04:05 01:00:05:12 00:00:00:00 00:00:01:07
* FROM CLIP NAME:  ZZ100_501 (LAY3)
*ASC_SOP (0.1 0.2 0.3) (1.0 -0.0122 0.0305) (1.0 0.0 1.0)
*ASC_SAT 0.9
* SOURCE FILE: ZZ100_501.LAY3.01
"""
        timeline = otio.adapters.read_from_string(original, "cmx_3600")
        output = otio.adapters.write_to_string(timeline, "cmx_3600")
        self.assertMultiLineEqual(original, output)


if __name__ == '__main__':
    unittest.main()
