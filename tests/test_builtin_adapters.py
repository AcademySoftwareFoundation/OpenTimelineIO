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

"""Test builtin adapters."""

import os
import shutil
import tempfile
import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

from opentimelineio.adapters import (
    otio_json,
)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")


class BuiltInAdapterTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_disk_io(self):
        edl_path = SCREENING_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        temp_dir = tempfile.mkdtemp(prefix='test_disk_io')
        try:
            temp_file = os.path.join(temp_dir, "foo.otio")
            otio.adapters.write_to_file(timeline, temp_file)
            decoded = otio.adapters.read_from_file(temp_file)
            self.assertJsonEqual(timeline, decoded)

        finally:
            shutil.rmtree(temp_dir)

    def test_otio_round_trip(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        baseline_json = otio.adapters.otio_json.write_to_string(tl)

        self.assertEqual(tl.name, "Example_Screening.01")

        temp_dir = tempfile.mkdtemp(prefix='test_otio_round_trip')
        try:
            temp_file = os.path.join(temp_dir, 'test.otio')
            otio.adapters.otio_json.write_to_file(tl, temp_file)
            new = otio.adapters.otio_json.read_from_file(temp_file)

            new_json = otio.adapters.otio_json.write_to_string(new)

            self.assertMultiLineEqual(baseline_json, new_json)
            self.assertIsOTIOEquivalentTo(tl, new)

        finally:
            shutil.rmtree(temp_dir)

    def test_disk_vs_string(self):
        """ Writing to disk and writing to a string should
        produce the same result
        """
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        temp_dir = tempfile.mkdtemp(prefix='test_disk_vs_string')
        try:
            temp_file = os.path.join(temp_dir, "foo.otio")
            otio.adapters.write_to_file(timeline, temp_file)
            in_memory = otio.adapters.write_to_string(timeline, 'otio_json')
            with open(temp_file, 'r') as f:
                on_disk = f.read()

            self.assertEqual(in_memory, on_disk)

        finally:
            shutil.rmtree(temp_dir)

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
