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

__doc__ = """Test builtin adapters."""

# python
import os
import tempfile
import unittest

import opentimelineio as otio

from opentimelineio.adapters import (
    otio_json,
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

    def test_otio_round_trip(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        baseline_json = otio.adapters.otio_json.write_to_string(tl)

        self.assertEqual(tl.name, "Example_Screening.01")

        otio.adapters.otio_json.write_to_file(tl, "/var/tmp/test.otio")
        new = otio.adapters.otio_json.read_from_file(
            "/var/tmp/test.otio"
        )

        new_json = otio.adapters.otio_json.write_to_string(new)

        self.assertMultiLineEqual(baseline_json, new_json)
        self.assertEqual(tl, new)

    def test_disk_vs_string(self):
        """ Writing to disk and writing to a string should
        produce the same result
        """
        timeline = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        tmp = tempfile.mkstemp(suffix=".otio", text=True)[1]
        otio.adapters.write_to_file(timeline, tmp)
        in_memory = otio.adapters.write_to_string(timeline, 'otio_json')
        with open(tmp, 'r') as f:
            on_disk = f.read()

        self.assertEqual(in_memory, on_disk)

    def test_adapters_fetch(self):
        """ Test the dynamic string based adapter fetching """
        self.assertEqual(
            otio.adapters.from_name('otio_json').module(),
            otio_json
        )


if __name__ == '__main__':
    unittest.main()
