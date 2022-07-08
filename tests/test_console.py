# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the 'console' module."""

import unittest
import sys
import os
import subprocess
import sysconfig
import platform

try:
    # python2
    import StringIO as io
except ImportError:
    # python3
    import io


# handle python2 vs python3 difference
try:
    from tempfile import TemporaryDirectory  # noqa: F401
    import tempfile
except ImportError:
    # XXX: python2.7 only
    from backports import tempfile

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
import opentimelineio.console as otio_console

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")


def CreateShelloutTest(cl):
    if os.environ.get("OTIO_DISABLE_SHELLOUT_TESTS"):
        newSuite = None
    else:
        class newSuite(cl):
            SHELL_OUT = True
        newSuite.__name__ = cl.__name__ + "_on_shell"

    return newSuite


class ConsoleTester(otio_test_utils.OTIOAssertions):
    """ Base class for running console tests both by directly calling main() and
    by shelling out.
    """

    SHELL_OUT = False

    def setUp(self):
        self.saved_args = sys.argv
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def run_test(self):
        if self.SHELL_OUT:
            # make sure its on the path
            console_script = os.path.join(sysconfig.get_path('scripts'), sys.argv[0])
            if platform.system() == 'Windows':
                console_script += '.exe'

            if not os.path.exists(console_script):
                self.fail(
                    "Could not find '{}'.  Tests that explicitly shell"
                    " out can be disabled by setting the environment variable "
                    "OTIO_DISABLE_SHELLOUT_TESTS.".format(console_script)
                )

            # actually run the test (sys.argv is already populated correctly)
            proc = subprocess.Popen(
                sys.argv,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()

            # XXX 2.7 vs 3.xx bug
            if type(stdout) is not str:
                stdout = stdout.decode("utf-8")
                stderr = stderr.decode("utf-8")

            sys.stdout.write(stdout)
            sys.stderr.write(stderr)

            if proc.returncode != 0:
                raise SystemExit()
        else:
            self.test_module.main()

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        sys.argv = self.saved_args


class OTIOStatTest(ConsoleTester, unittest.TestCase):
    test_module = otio_console.otiostat

    def test_basic(self):
        sys.argv = ['otiostat', SCREENING_EXAMPLE_PATH]
        self.run_test()
        self.assertIn("top level object: Timeline.1", sys.stdout.getvalue())


OTIOStatTest_ShellOut = CreateShelloutTest(OTIOStatTest)


class OTIOCatTests(ConsoleTester, unittest.TestCase):
    test_module = otio_console.otiocat

    def test_basic(self):
        sys.argv = ['otiocat', SCREENING_EXAMPLE_PATH, "-a", "rate=24.0"]
        self.run_test()
        self.assertIn('"name": "Example_Screening.01",', sys.stdout.getvalue())

    def test_no_media_linker(self):
        sys.argv = ['otiocat', SCREENING_EXAMPLE_PATH, "-m", "none"]
        self.run_test()
        self.assertIn('"name": "Example_Screening.01",', sys.stdout.getvalue())

    def test_input_argument_error(self):
        sys.argv = [
            'otiocat',
            SCREENING_EXAMPLE_PATH,
            "-a", "foobar",
        ]

        with self.assertRaises(SystemExit):
            self.run_test()

        # read results back in
        self.assertIn('error: adapter', sys.stderr.getvalue())

    def test_media_linker_argument_error(self):
        sys.argv = [
            'otiocat',
            SCREENING_EXAMPLE_PATH,
            "-M", "foobar",
        ]

        with self.assertRaises(SystemExit):
            self.run_test()

        # read results back in
        self.assertIn('error: media linker', sys.stderr.getvalue())


OTIOCatTests_OnShell = CreateShelloutTest(OTIOCatTests)


class OTIOConvertTests(ConsoleTester, unittest.TestCase):
    test_module = otio_console.otioconvert

    def test_basic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_basic.otio")
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                '--tracks', '0',
                "-a", "rate=24",
            ]
            self.run_test()

            # read results back in
            with open(temp_file, 'r') as fi:
                self.assertIn('"name": "Example_Screening.01",', fi.read())

    def test_begin_end(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_begin_end.otio")

            # begin needs to be a,b
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "--begin", "foobar"
            ]
            with self.assertRaises(SystemExit):
                self.run_test()

            # end requires begin
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "--end", "foobar"
            ]
            with self.assertRaises(SystemExit):
                self.run_test()

            # prune everything
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "--begin", "0,24",
                "--end", "0,24",
            ]
            otio_console.otioconvert.main()

            # check that begin/end "," parsing is checked
            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "--begin", "0",
                "--end", "0,24",
            ]
            with self.assertRaises(SystemExit):
                self.run_test()

            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "--begin", "0,24",
                "--end", "0",
            ]
            with self.assertRaises(SystemExit):
                self.run_test()

            result = otio.adapters.read_from_file(temp_file, "otio_json")
            self.assertEqual(len(result.tracks[0]), 0)
            self.assertEqual(result.name, "Example_Screening.01")

    def test_input_argument_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_input_argument_error.otio")

            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                "-a", "foobar",
            ]

            with self.assertRaises(SystemExit):
                self.run_test()

            # read results back in
            self.assertIn('error: input adapter', sys.stderr.getvalue())

    def test_output_argument_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_output_argument_error.otio")

            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "-A", "foobar",
            ]

            with self.assertRaises(SystemExit):
                self.run_test()

            # read results back in
            self.assertIn('error: output adapter', sys.stderr.getvalue())

    def test_media_linker_argument_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_media_linker_argument_error.otio")

            sys.argv = [
                'otioconvert',
                '-i', SCREENING_EXAMPLE_PATH,
                '-o', temp_file,
                '-O', 'otio_json',
                "-m", "fake_linker",
                "-M", "somestring=foobar",
                "-M", "foobar",
            ]

            with self.assertRaises(SystemExit):
                self.run_test()

            # read results back in
            self.assertIn('error: media linker', sys.stderr.getvalue())


OTIOConvertTests_OnShell = CreateShelloutTest(OTIOConvertTests)


class OTIOPlugInfoTest(ConsoleTester, unittest.TestCase):
    test_module = otio_console.otiopluginfo

    def test_basic(self):
        sys.argv = ['otiopluginfo']
        self.run_test()
        self.assertIn("Manifests loaded:", sys.stdout.getvalue())


OTIOPlugInfoTest_ShellOut = CreateShelloutTest(OTIOStatTest)


if __name__ == '__main__':
    unittest.main()
