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

__doc__ = """Test the CMX 3600 EDL adapter."""

# python
import os
import tempfile
import unittest
import re

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
NO_SPACES_PATH = os.path.join(SAMPLE_DATA_DIR, "no_spaces_test.edl")
DISSOLVE_TEST = os.path.join(SAMPLE_DATA_DIR, "dissolve_test.edl")
DISSOLVE_TEST_2 = os.path.join(SAMPLE_DATA_DIR, "dissolve_test_2.edl")


class EDLAdapterTest(unittest.TestCase):

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

        self.assertEqual(len(timeline.tracks[0][3].markers), 1)
        marker = timeline.tracks[0][3].markers[0]
        self.assertEqual(marker.name, "ANIM FIX NEEDED")
        self.assertEqual(marker.metadata.get("cmx_3600").get("color"), "RED")
        self.assertEqual(marker.marked_range.start_time,
                         otio.opentime.from_timecode("01:00:01:14"))
        self.assertEqual(marker.color, otio.schema.MarkerColor.RED)

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

    def test_edl_round_trip_mem2disk2mem(self):
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
        tl.tracks[0].name = "V"
        tl.tracks[0].append(cl)
        tl.tracks[0].extend([cl2, cl3])

        result = otio.adapters.write_to_string(tl, adapter_name="cmx_3600")
        new_otio = otio.adapters.read_from_string(
            result,
            adapter_name="cmx_3600"
        )

        def strip_trailing_decimal_zero(s):
            return re.sub(r'"(value|rate)": (\d+)\.0', r'"\1": \2', s)

        self.maxDiff = None
        self.assertMultiLineEqual(
            strip_trailing_decimal_zero(
                otio.adapters.write_to_string(
                    new_otio,
                    adapter_name="otio_json"
                )
            ),
            strip_trailing_decimal_zero(
                otio.adapters.write_to_string(
                    tl,
                    adapter_name="otio_json"
                )
            )
        )
        self.assertEqual(new_otio, tl)

    def test_edl_round_trip_disk2mem2disk(self):
        self.maxDiff = None
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        tmp_path = tempfile.mkstemp(suffix=".edl", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)

        result = otio.adapters.read_from_file(tmp_path)

        # When debugging, you can use this to see the difference in the OTIO
        # otio.adapters.otio_json.write_to_file(timeline, "/tmp/original.otio")
        # otio.adapters.otio_json.write_to_file(result, "/tmp/output.otio")
        # os.system("opendiff /tmp/{original,output}.otio")

        original_json = otio.adapters.otio_json.write_to_string(timeline)
        output_json = otio.adapters.otio_json.write_to_string(result)
        self.assertMultiLineEqual(original_json, output_json)

        # The in-memory OTIO representation should be the same
        self.assertEqual(timeline, result)

        # When debugging, use this to see the difference in the EDLs on disk
        # os.system("opendiff {} {}".format(SCREENING_EXAMPLE_PATH, tmp_path))

        # But the EDL text on disk are *not* byte-for-byte identical
        with open(SCREENING_EXAMPLE_PATH, "r") as original_file:
            with open(tmp_path, "r") as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())

    def test_regex_flexibility(self):
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)
        no_spaces = otio.adapters.read_from_file(NO_SPACES_PATH)
        self.assertEqual(timeline, no_spaces)

    def test_clip_with_tab_and_space_delimiters(self):
        timeline = otio.adapters.read_from_string(
            '001  Z10 V  C\t\t01:00:04:05 01:00:05:12 00:59:53:11 00:59:54:18',
            adapter_name="cmx_3600"
        )
        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 1)
        self.assertEqual(
            timeline.tracks[0].kind,
            otio.schema.SequenceKind.Video
        )
        self.assertEqual(len(timeline.tracks[0]), 1)
        self.assertEqual(
            timeline.tracks[0][0].source_range.start_time.value,
            86501
        )
        self.assertEqual(
            timeline.tracks[0][0].source_range.duration.value,
            31
        )

    def test_dissolve_parse(self):
        tl = otio.adapters.read_from_file(DISSOLVE_TEST)
        self.assertEqual(len(tl.tracks[0]), 3)

        self.assertTrue(isinstance(tl.tracks[0][1], otio.schema.Transition))

        self.assertEqual(tl.tracks[0][0].duration().value, 14)
        self.assertEqual(tl.tracks[0][2].duration().value, 6)

    def test_dissolve_parse_middle(self):
        tl = otio.adapters.read_from_file(DISSOLVE_TEST_2)
        self.assertEqual(len(tl.tracks[0]), 3)

        self.assertTrue(isinstance(tl.tracks[0][1], otio.schema.Transition))

        trck = tl.tracks[0]
        self.assertEqual(trck[0].duration().value, 10)
        self.assertEqual(trck[2].source_range.start_time.value, 86400+201)
        self.assertEqual(trck[2].duration().value, 10)

    def test_dissolve_with_odd_frame_count_maintains_length(self):
        # EXERCISE
        tl = otio.adapters.read_from_string(
            '1 CLPA V C     00:00:04:17 00:00:07:02 00:00:00:00 00:00:02:09\n'
            '2 CLPA V C     00:00:07:02 00:00:07:02 00:00:02:09 00:00:02:09\n'
            '2 CLPB V D 027 00:00:06:18 00:00:07:21 00:00:02:09 00:00:03:12\n'
            '3 CLPB V C     00:00:07:21 00:00:15:21 00:00:03:12 00:00:11:12\n',
            adapter_name="cmx_3600"
        )

        # VALIDATE
        self.assertEqual(tl.duration().value, (11*24)+12)

    def test_fade_to_black_ends_with_gap(self):
        # EXERCISE
        tl = otio.adapters.read_from_string(
            '1 CLPA V C     00:00:03:18 00:00:12:15 00:00:00:00 00:00:08:21\n'
            '2 CLPA V C     00:00:12:15 00:00:12:15 00:00:08:21 00:00:08:21\n'
            '2 BL   V D 024 00:00:00:00 00:00:01:00 00:00:08:21 00:00:09:21\n',
            adapter_name="cmx_3600"
        )

        # VALIDATE
        self.assertEqual(len(tl.tracks[0]), 3)
        self.assertTrue(isinstance(tl.tracks[0][1], otio.schema.Transition))
        self.assertTrue(isinstance(tl.tracks[0][2], otio.schema.Gap))
        self.assertEqual(tl.tracks[0][2].duration().value, 12)
        self.assertEqual(tl.tracks[0][2].source_range.start_time.value, 0)


if __name__ == '__main__':
    unittest.main()
