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

"""Unit tests for the srt file adapter"""

import unittest
import os
import tempfile
import io

import opentimelineio as otio

OTIO_SAMPLE_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "sample_data"
)
SRT_EXAMPLE_PATH = os.path.join(OTIO_SAMPLE_DATA_DIR, "srt_example.srt")
SRT_OTIO_EXAMPLE_PATH = os.path.join(OTIO_SAMPLE_DATA_DIR,
                                     "srt_example.otio")


class SRTTest(unittest.TestCase):
    maxDiff = None
    def setUp(self):
        fd, self.tmp_path = tempfile.mkstemp(suffix=".srt", text=True)
        os.close(fd)

        fd, self.tmp_path_otio = tempfile.mkstemp(suffix=".otio", text=True)
        os.close(fd)

    def tearDown(self):
        os.unlink(self.tmp_path)

    def test_srt_read(self):
        st = otio.adapters.read_from_file(SRT_EXAMPLE_PATH)

        otio.adapters.write_to_file(st, self.tmp_path)

        with io.open(self.tmp_path) as f:
            test_data = f.read().strip()

        with io.open(self.tmp_path) as f:
            baseline_data = f.read().strip()

        self.maxDiff = None
        self.assertMultiLineEqual(baseline_data, test_data)

    def test_otio(self):
        st = otio.adapters.read_from_file(SRT_EXAMPLE_PATH)

        otio.adapters.write_to_file(st, self.tmp_path_otio)

        with io.open(self.tmp_path_otio) as f:
            test_data = f.read()

        with io.open(SRT_OTIO_EXAMPLE_PATH) as f:
            baseline_data = f.read()
        
        self.maxDiff = None
        self.assertMultiLineEqual(baseline_data, test_data)


if __name__ == '__main__':
    unittest.main()
