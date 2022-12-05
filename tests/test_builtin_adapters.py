# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test builtin adapters."""

import os
import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

from opentimelineio.adapters import (
    otio_json,
)

import tempfile


SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.otio")


class BuiltInAdapterTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_disk_io(self):
        edl_path = SCREENING_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_disk_io.otio")
            otio.adapters.write_to_file(timeline, temp_file)
            decoded = otio.adapters.read_from_file(temp_file)
            self.assertJsonEqual(timeline, decoded)

    def test_otio_round_trip(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        baseline_json = otio.adapters.otio_json.write_to_string(tl)

        self.assertEqual(tl.name, "Example_Screening.01")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, 'test_otio_round_trip.otio')
            otio.adapters.otio_json.write_to_file(tl, temp_file)
            new = otio.adapters.otio_json.read_from_file(temp_file)

            new_json = otio.adapters.otio_json.write_to_string(new)

            self.assertMultiLineEqual(baseline_json, new_json)
            self.assertIsOTIOEquivalentTo(tl, new)

    def test_disk_vs_string(self):
        """ Writing to disk and writing to a string should
        produce the same result
        """
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_disk_vs_string.otio")
            otio.adapters.write_to_file(timeline, temp_file)
            in_memory = otio.adapters.write_to_string(timeline, 'otio_json')
            with open(temp_file) as f:
                on_disk = f.read()

            self.maxDiff = None

            # for debugging
            # with open("/var/tmp/in_memory.otio", "w") as fo:
            #     fo.write(in_memory)
            #
            # with open("/var/tmp/on_disk.otio", "w") as fo:
            #     fo.write(on_disk)

            self.assertEqual(in_memory, on_disk)

    def test_adapters_fetch(self):
        """ Test the dynamic string based adapter fetching """
        self.assertEqual(
            otio.adapters.from_name('otio_json').module(),
            otio_json
        )

    def test_otio_json_default(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)
        self.assertMultiLineEqual(
            otio.adapters.write_to_string(tl, 'otio_json'),
            otio.adapters.write_to_string(tl)
        )

        test_str = otio.adapters.write_to_string(tl)
        self.assertJsonEqual(tl, otio.adapters.read_from_string(test_str))


if __name__ == '__main__':
    unittest.main()
