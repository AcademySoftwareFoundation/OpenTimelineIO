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
import os
import tempfile

try:
    # python2
    import StringIO as io
except ImportError:
    # python3
    import io

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")


class ConsoleTester(otio.test_utils.OTIOAssertions):
    def setUp(self):
        self.saved_args = sys.argv
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

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
        sys.argv = ['otiocat', SCREENING_EXAMPLE_PATH, "-a", "rate=24.0"]
        otio.console.otiocat.main()
        self.assertIn('"name": "Example_Screening.01",', sys.stdout.getvalue())

    def test_no_media_linker(self):
        sys.argv = ['otiocat', SCREENING_EXAMPLE_PATH, "-m", "none"]
        otio.console.otiocat.main()
        self.assertIn('"name": "Example_Screening.01",', sys.stdout.getvalue())

    def test_input_argument_error(self):
        sys.argv = [
            'otiocat',
            SCREENING_EXAMPLE_PATH,
            "-a", "foobar",
        ]

        with self.assertRaises(SystemExit):
            otio.console.otiocat.main()

        # read results back in
        self.assertIn('error: adapter', sys.stderr.getvalue())

    def test_media_linker_argument_error(self):
        sys.argv = [
            'otiocat',
            SCREENING_EXAMPLE_PATH,
            "-M", "foobar",
        ]

        with self.assertRaises(SystemExit):
            otio.console.otiocat.main()

        # read results back in
        self.assertIn('error: media linker', sys.stderr.getvalue())


class OTIOConvertTests(ConsoleTester, unittest.TestCase):
    def test_basic(self):
        with tempfile.NamedTemporaryFile() as tf:
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', tf.name,
                '-O', 'otio_json',
                "-a", "rate=24",
            ]
            otio.console.otioconvert.main()

            # read results back in
            with open(tf.name, 'r') as fi:
                self.assertIn('"name": "Example_Screening.01",', fi.read())

    def test_input_argument_error(self):
        with tempfile.NamedTemporaryFile() as tf:
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', tf.name,
                '-O', 'otio_json',
                "-a", "foobar",
            ]

            with self.assertRaises(SystemExit):
                otio.console.otioconvert.main()

            # read results back in
            self.assertIn('error: input adapter', sys.stderr.getvalue())

    def test_output_argument_error(self):
        with tempfile.NamedTemporaryFile() as tf:
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', tf.name,
                '-O', 'otio_json',
                "-A", "foobar",
            ]

            with self.assertRaises(SystemExit):
                otio.console.otioconvert.main()

            # read results back in
            self.assertIn('error: output adapter', sys.stderr.getvalue())

    def test_media_linker_argument_error(self):
        with tempfile.NamedTemporaryFile() as tf:
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', tf.name,
                '-O', 'otio_json',
                "-M", "foobar",
            ]

            with self.assertRaises(SystemExit):
                otio.console.otioconvert.main()

            # read results back in
            self.assertIn('error: media linker', sys.stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
