# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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
                list(cdl.get("asc_sop").get("slope")),
                [0.1, 0.2, 0.3]
            )
            self.assertEqual(
                list(cdl.get("asc_sop").get("offset")),
                [1.0000, -0.0122, 0.0305]
            )
            self.assertEqual(
                list(cdl.get("asc_sop").get("power")),
                [1.0000, 0.0000, 1.0000]
            )

    def test_cdl_read_with_commas(self):
        # This EDL was generated with Premiere Pro using the CDL master effect
        # on a clip
        cdl = """TITLE: Sequence 01
FCM: NON-DROP FRAME

000001  A006C014_1701069O V     C        04:34:41:13 04:34:41:16 00:00:00:00 00:00:00:03
* FROM CLIP NAME: A006C014_1701069O_LOG_NO_LUT.mov
* ASC_SOP: (1.1549, 1.1469, 1.1422000000000001)(-0.067799999999999999, -0.055500000000000001, -0.032300000000000002)(1.1325000000000001, 1.1351, 1.1221000000000001)
* ASC_SAT: 1.2988
"""  # noqa: E501
        timeline = otio.adapters.read_from_string(cdl, "cmx_3600")

        clip = timeline.tracks[0][0]
        cdl_metadata = clip.metadata["cdl"]

        ref_sop_values = {
            "slope": [
                1.1549,
                1.1469,
                1.1422000000000001,
            ],
            "offset": [
                -0.067799999999999999,
                -0.055500000000000001,
                -0.032300000000000002,
            ],
            "power": [
                1.1325000000000001,
                1.1351,
                1.1221000000000001,
            ],
        }

        self.assertAlmostEqual(cdl_metadata["asc_sat"], 1.2988)
        for function in ("slope", "offset", "power"):
            comparisons = zip(
                cdl_metadata["asc_sop"][function], ref_sop_values[function]
            )
            for value_comp, ref_comp in comparisons:
                self.assertAlmostEqual(
                    value_comp, ref_comp, msg=f"mismatch in {function}"
                )

    def test_cdl_round_trip(self):
        original = """TITLE: Example_Screening.01

001  AX       V     C        01:00:04:05 01:00:05:12 00:00:00:00 00:00:01:07
* FROM CLIP NAME:  ZZ100_501 (LAY3)
*ASC_SOP (0.1 0.2 0.3) (1.0 -0.0122 0.0305) (1.0 0.0 1.0)
*ASC_SAT 0.9
* SOURCE FILE: ZZ100_501.LAY3.01
"""
        expected = """TITLE: Example_Screening.01

001  ZZ100501 V     C        01:00:04:05 01:00:05:12 00:00:00:00 00:00:01:07
* FROM CLIP NAME:  ZZ100_501 (LAY3)
* OTIO TRUNCATED REEL NAME FROM: ZZ100_501 (LAY3)
*ASC_SOP (0.1 0.2 0.3) (1.0 -0.0122 0.0305) (1.0 0.0 1.0)
*ASC_SAT 0.9
* SOURCE FILE: ZZ100_501.LAY3.01
"""
        timeline = otio.adapters.read_from_string(original, "cmx_3600")
        output = otio.adapters.write_to_string(timeline, "cmx_3600")
        self.assertMultiLineEqual(expected, output)


if __name__ == '__main__':
    unittest.main()
