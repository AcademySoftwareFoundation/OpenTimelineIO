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

"""Unit tests for the 'console' module."""

import unittest
import sys
import StringIO
import os
import tempfile

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")


class ConsoleTester(otio.test_utils.OTIOAssertions):
    def setUp(self):
        self.saved_args = sys.argv
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        sys.argv = self.saved_args


class OTIOStatTest(ConsoleTester, unittest.TestCase):
    def test_basic(self):
        sys.argv = ['otiostat', SCREENING_EXAMPLE_PATH]
        otio.console.otiostat.main()
        self.assertIn("top level object: Timeline.1", sys.stdout.getvalue())


class OTIOCatTests(ConsoleTester, unittest.TestCase):
    def test_basic(self):
        sys.argv = ['otiocat', SCREENING_EXAMPLE_PATH]
        otio.console.otiocat.main()
        self.assertIn('"name": "Example_Screening.01",', sys.stdout.getvalue())


class OTIOConvertTests(unittest.TestCase):
    def test_basic(self):
        with tempfile.NamedTemporaryFile() as tf:
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', tf.name,
                '-O', 'otio_json'
            ]
            otio.console.otioconvert.main()

            # read results back in
            with open(tf.name, 'r') as fi:
                self.assertIn('"name": "Example_Screening.01",', fi.read())


if __name__ == '__main__':
    unittest.main()
