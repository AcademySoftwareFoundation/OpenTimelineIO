#!/usr/bin/env python2.7

"""Test builtin adapters."""

# python
import os
import tempfile
import unittest

import opentimelineio as otio

from opentimelineio.adapters import (
    cmx_3600,
    otio_json
)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")


class BuiltInAdapterTest(unittest.TestCase):

    def test_disk_io(self):
        edl_path = SCREENING_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        otiotmp = tempfile.mkstemp(suffix=".otio", text=True)[1]
        otio.adapters.write_to_file(timeline, otiotmp)
        decoded = otio.adapters.read_from_file(otiotmp)
        self.assertEqual(timeline, decoded)

    def test_edl_read(self):
        edl_path = SCREENING_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 1)
        self.assertEqual(len(timeline.tracks[0]), 9)
        self.assertEqual(
            timeline.tracks[0][0].name,
            "ZZ100_501 (LAY3)"
        )
        self.assertEqual(
            timeline.tracks[0][0].source_range.duration,
            otio.opentime.from_timecode("00:00:01:07")
        )
        self.assertEqual(
            timeline.tracks[0][1].name,
            "ZZ100_502A (LAY3)"
        )
        self.assertEqual(
            timeline.tracks[0][1].source_range.duration,
            otio.opentime.from_timecode("00:00:02:02")
        )
        self.assertEqual(
            timeline.tracks[0][2].name,
            "ZZ100_503A (LAY1)"
        )
        self.assertEqual(
            timeline.tracks[0][2].source_range.duration,
            otio.opentime.from_timecode("00:00:01:04")
        )
        self.assertEqual(
            timeline.tracks[0][3].name,
            "ZZ100_504C (LAY1)"
        )
        self.assertEqual(
            timeline.tracks[0][3].source_range.duration,
            otio.opentime.from_timecode("00:00:04:19")
        )
        self.assertEqual(
            timeline.tracks[0][4].name,
            "ZZ100_504B (LAY1)"
        )
        self.assertEqual(
            timeline.tracks[0][4].source_range.duration,
            otio.opentime.from_timecode("00:00:04:05")
        )
        self.assertEqual(
            timeline.tracks[0][5].name,
            "ZZ100_507C (LAY2)"
        )
        self.assertEqual(
            timeline.tracks[0][5].source_range.duration,
            otio.opentime.from_timecode("00:00:06:17")
        )
        self.assertEqual(
            timeline.tracks[0][6].name,
            "ZZ100_508 (LAY2)"
        )
        self.assertEqual(
            timeline.tracks[0][6].source_range.duration,
            otio.opentime.from_timecode("00:00:07:02")
        )
        self.assertEqual(
            timeline.tracks[0][7].name,
            "ZZ100_510 (LAY1)"
        )
        self.assertEqual(
            timeline.tracks[0][7].source_range.duration,
            otio.opentime.from_timecode("00:00:05:16")
        )
        self.assertEqual(
            timeline.tracks[0][8].name,
            "ZZ100_510B (LAY1)"
        )
        self.assertEqual(
            timeline.tracks[0][8].source_range.duration,
            otio.opentime.from_timecode("00:00:10:17")
        )

    def test_edl_round_trip(self):
        track = otio.schema.Sequence()
        tl = otio.schema.Timeline("test_timeline", tracks=[track])
        rt = otio.opentime.RationalTime(5.0, 24.0)
        mr = otio.media_reference.External(target_url="/var/tmp/test.mov")

        tr = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0.0, 24.0),
            duration=rt
        )

        cl = otio.schema.Clip(
            name="test clip1",
            media_reference=mr,
            source_range=tr,
        )
        cl2 = otio.schema.Clip(
            name="test clip2",
            media_reference=mr,
            source_range=tr,
        )
        cl3 = otio.schema.Clip(
            name="test clip3",
            media_reference=mr,
            source_range=tr,
        )
        tl.tracks[0].append(cl)
        tl.tracks[0].extend([cl2, cl3])

        result = otio.adapters.write_to_string(tl, adapter_name="cmx_3600")
        new_otio = otio.adapters.read_from_string(
            result,
            adapter_name="cmx_3600"
        )

        self.maxDiff = None
        self.assertMultiLineEqual(
            otio.adapters.write_to_string(new_otio, adapter_name="otio_json"),
            otio.adapters.write_to_string(tl, adapter_name="otio_json")
        )
        self.assertEqual(new_otio, tl)

    def test_read_cmx(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH, "cmx_3600")

        baseline_json = otio.adapters.otio_json.write_to_string(tl)

        self.assertEqual(tl.name, "Example_Screening.01")

        otio.adapters.otio_json.write_to_file(tl, "/var/tmp/test.otio")
        new = otio.adapters.otio_json.read_from_file(
            "/var/tmp/test.otio"
        )

        new_json = otio.adapters.otio_json.write_to_string(new)

        self.assertMultiLineEqual(baseline_json, new_json)
        self.assertEqual(tl, new)

    def test_edl_disk_vs_string(self):
        """ Writing to disk and writing to a string should
        produce the same result
        """
        edl_path = SCREENING_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        edltmp = tempfile.mkstemp(suffix=".edl", text=True)[1]
        otio.adapters.write_to_file(timeline, edltmp)
        in_memory = otio.adapters.write_to_string(timeline, 'cmx_3600')
        with open(edltmp, 'r') as f:
            on_disk = f.read()

        self.assertEqual(in_memory, on_disk)

    def test_adapters_fetch(self):
        """ Test the dynamic string based adapter fetching """
        printer = otio.adapters.from_name('otio_json')
        self.assertEqual(printer.module(), otio_json)
        self.assertEqual(
            otio.adapters.from_name('cmx_3600').module(),
            cmx_3600
        )


if __name__ == '__main__':
    unittest.main()
