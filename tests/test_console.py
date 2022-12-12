# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the 'console' module."""

import unittest
import sys
import os
import subprocess
import sysconfig
import pathlib
import platform

import io

from tempfile import TemporaryDirectory  # noqa: F401
import tempfile

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
import opentimelineio.console as otio_console

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
# FIXME: remove or replace the premiere test
MULTITRACK_PATH = os.path.join(SAMPLE_DATA_DIR, "multitrack.otio")
PREMIERE_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "premiere_example.xml")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.otio")
SIMPLE_CUT_PATH = os.path.join(SAMPLE_DATA_DIR, "simple_cut.otio")
TRANSITION_PATH = os.path.join(SAMPLE_DATA_DIR, "transition.otio")


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

        # pre-fetch these strings for easy access
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()

        if platform.system() == 'Windows':
            # Normalize line-endings for assertEqual(expected, actual)
            stdout = stdout.replace('\r\n', '\n')
            stderr = stderr.replace('\r\n', '\n')

        return stdout, stderr

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
        sys.argv = ['otiocat', SCREENING_EXAMPLE_PATH]
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
                '--tracks', '0'
            ]
            self.run_test()

            # read results back in
            with open(temp_file) as fi:
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


class OTIOToolTest(ConsoleTester, unittest.TestCase):
    test_module = otio_console.otiotool

    def test_list_tracks(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--list-tracks'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: OTIO TEST - multitrack.Exported.01
TRACK: Sequence (Video)
TRACK: Sequence 2 (Video)
TRACK: Sequence 3 (Video)
""", out)

    def test_list_clips(self):
        sys.argv = [
            'otiotool',
            '-i', SCREENING_EXAMPLE_PATH,
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: Example_Screening.01
  CLIP: ZZ100_501 (LAY3)
  CLIP: ZZ100_502A (LAY3)
  CLIP: ZZ100_503A (LAY1)
  CLIP: ZZ100_504C (LAY1)
  CLIP: ZZ100_504B (LAY1)
  CLIP: ZZ100_507C (LAY2)
  CLIP: ZZ100_508 (LAY2)
  CLIP: ZZ100_510 (LAY1)
  CLIP: ZZ100_510B (LAY1)
""", out)

    def test_list_markers(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--list-markers'
        ]
        out, err = self.run_test()
        self.assertEqual(
            ("TIMELINE: sc01_sh010_layerA\n"
             "  MARKER: global: 00:00:03:23 local: 00:00:03:23 duration: 0.0 color: RED name: My MArker 1\n"  # noqa: E501 line too long
             "  MARKER: global: 00:00:16:12 local: 00:00:16:12 duration: 0.0 color: RED name: dsf\n"  # noqa: E501 line too long
             "  MARKER: global: 00:00:09:28 local: 00:00:09:28 duration: 0.0 color: RED name: \n"  # noqa: E501 line too long
             "  MARKER: global: 00:00:13:05 local: 00:00:02:13 duration: 0.0 color: RED name: \n"),  # noqa: E501 line too long
            out)

    def test_list_tracks_and_clips(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--list-tracks',
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: OTIO TEST - multitrack.Exported.01
TRACK: Sequence (Video)
  CLIP: tech.fux (loop)-HD.mp4
  CLIP: out-b (loop)-HD.mp4
  CLIP: brokchrd (loop)-HD.mp4
TRACK: Sequence 2 (Video)
  CLIP: t-hawk (loop)-HD.mp4
TRACK: Sequence 3 (Video)
  CLIP: KOLL-HD.mp4
""", out)

    def test_list_tracks_and_clips_and_media(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--list-tracks',
            '--list-clips',
            '--list-media'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: OTIO TEST - multitrack.Exported.01
TRACK: Sequence (Video)
  CLIP: tech.fux (loop)-HD.mp4
    MEDIA: None
  CLIP: out-b (loop)-HD.mp4
    MEDIA: None
  CLIP: brokchrd (loop)-HD.mp4
    MEDIA: None
TRACK: Sequence 2 (Video)
  CLIP: t-hawk (loop)-HD.mp4
    MEDIA: None
TRACK: Sequence 3 (Video)
  CLIP: KOLL-HD.mp4
    MEDIA: None
""", out)

    def test_list_tracks_and_clips_and_media_and_markers(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--list-tracks',
            '--list-clips',
            '--list-media',
            '--list-markers'
        ]
        out, err = self.run_test()
        self.assertEqual(
            ("TIMELINE: sc01_sh010_layerA\n"
             "  MARKER: global: 00:00:03:23 local: 00:00:03:23 duration: 0.0 color: RED name: My MArker 1\n"  # noqa E501 line too long
             "  MARKER: global: 00:00:16:12 local: 00:00:16:12 duration: 0.0 color: RED name: dsf\n"  # noqa E501 line too long
             "  MARKER: global: 00:00:09:28 local: 00:00:09:28 duration: 0.0 color: RED name: \n"  # noqa E501 line too long
             "TRACK:  (Video)\n"
             "  CLIP: sc01_sh010_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh010_anim.mov\n"
             "TRACK:  (Video)\n"
             "  CLIP: sc01_sh010_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh010_anim.mov\n"
             "  CLIP: sc01_sh020_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh020_anim.mov\n"
             "  CLIP: sc01_sh030_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh030_anim.mov\n"
             "  MARKER: global: 00:00:13:05 local: 00:00:02:13 duration: 0.0 color: RED name: \n"  # noqa E501 line too long
             "TRACK:  (Video)\n"
             "  CLIP: test_title\n"
             "    MEDIA: None\n"
             "TRACK:  (Video)\n"
             "  CLIP: sc01_master_layerA_sh030_temp.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_master_layerA_sh030_temp.mov\n"  # noqa E501 line too long
             "  CLIP: sc01_sh010_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh010_anim.mov\n"
             "TRACK:  (Audio)\n"
             "  CLIP: sc01_sh010_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh010_anim.mov\n"
             "  CLIP: sc01_sh010_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh010_anim.mov\n"
             "TRACK:  (Audio)\n"
             "  CLIP: sc01_placeholder.wav\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_placeholder.wav\n"
             "TRACK:  (Audio)\n"
             "  CLIP: track_08.wav\n"
             "    MEDIA: file://localhost/D%3a/media/track_08.wav\n"
             "TRACK:  (Audio)\n"
             "  CLIP: sc01_master_layerA_sh030_temp.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_master_layerA_sh030_temp.mov\n"  # noqa E501 line too long
             "  CLIP: sc01_sh010_anim.mov\n"
             "    MEDIA: file://localhost/D%3a/media/sc01_sh010_anim.mov\n"),
            out)

    def test_verify_media(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--list-tracks',
            '--list-clips',
            '--list-media',
            '--verify-media'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: sc01_sh010_layerA
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh010_anim.mov
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh010_anim.mov
  CLIP: sc01_sh020_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh020_anim.mov
  CLIP: sc01_sh030_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh030_anim.mov
TRACK:  (Video)
  CLIP: test_title
    MEDIA: None
TRACK:  (Video)
  CLIP: sc01_master_layerA_sh030_temp.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_placeholder.wav
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_placeholder.wav
TRACK:  (Audio)
  CLIP: track_08.wav
    MEDIA NOT FOUND: file://localhost/D%3a/media/track_08.wav
TRACK:  (Audio)
  CLIP: sc01_master_layerA_sh030_temp.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
    MEDIA NOT FOUND: file://localhost/D%3a/media/sc01_sh010_anim.mov
""", out)

    def test_video_only(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--video-only',
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: sc01_sh010_layerA
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh020_anim.mov
  CLIP: sc01_sh030_anim.mov
  CLIP: test_title
  CLIP: sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
""", out)

    def test_audio_only(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--audio-only',
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: sc01_sh010_layerA
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_placeholder.wav
  CLIP: track_08.wav
  CLIP: sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
""", out)

    def test_only_tracks_with_name(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--only-tracks-with-name', 'Sequence 3',
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: OTIO TEST - multitrack.Exported.01
  CLIP: KOLL-HD.mp4
""", out)

    def test_only_tracks_with_index(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--only-tracks-with-index', '3',
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: OTIO TEST - multitrack.Exported.01
  CLIP: KOLL-HD.mp4
""", out)

    def test_only_tracks_with_index2(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--only-tracks-with-index', '2', '3',
            '--list-clips'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: OTIO TEST - multitrack.Exported.01
  CLIP: t-hawk (loop)-HD.mp4
  CLIP: KOLL-HD.mp4
""", out)

    def test_only_clips_with_name(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--list-clips',
            '--list-tracks',
            '--only-clips-with-name', 'sc01_sh010_anim.mov'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: sc01_sh010_layerA
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Video)
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
TRACK:  (Audio)
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
""", out)

    def test_only_clips_with_regex(self):
        sys.argv = [
            'otiotool',
            '-i', PREMIERE_EXAMPLE_PATH,
            '--list-clips',
            '--list-tracks',
            '--only-clips-with-name-regex', 'anim'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: sc01_sh010_layerA
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh020_anim.mov
  CLIP: sc01_sh030_anim.mov
TRACK:  (Video)
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
TRACK:  (Audio)
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
""", out)

    def test_remote_transition(self):
        sys.argv = [
            'otiotool',
            '-i', TRANSITION_PATH,
            '-o', '-',
            '--remove-transitions'
        ]
        out, err = self.run_test()
        self.assertNotIn('"OTIO_SCHEMA": "Transition.', out)

    def test_trim(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--trim', '20', '40',
            '--list-clips',
            '--inspect', 't-hawk'
        ]
        out, err = self.run_test()
        self.assertEqual(
            ("TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "  ITEM: t-hawk (loop)-HD.mp4 (<class 'opentimelineio._otio.Clip'>)\n"  # noqa E501 line too long
             "    source_range: TimeRange(RationalTime(0, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    trimmed_range: TimeRange(RationalTime(0, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    visible_range: TimeRange(RationalTime(0, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    range_in_parent: TimeRange(RationalTime(2, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    trimmed range in timeline: TimeRange(RationalTime(2, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    visible range in timeline: TimeRange(RationalTime(2, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    range in Sequence 2 (<class 'opentimelineio._otio.Track'>): TimeRange(RationalTime(2, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "    range in NestedScope (<class 'opentimelineio._otio.Stack'>): TimeRange(RationalTime(2, 24), RationalTime(478, 24))\n"  # noqa E501 line too long
             "TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "  CLIP: tech.fux (loop)-HD.mp4\n"
             "  CLIP: out-b (loop)-HD.mp4\n"
             "  CLIP: t-hawk (loop)-HD.mp4\n"),
            out)

    def test_flatten(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--flatten', 'video',
            '--list-clips',
            '--list-tracks',
            '--inspect', 'out-b'
        ]
        out, err = self.run_test()
        self.assertEqual(
            ("TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "  ITEM: out-b (loop)-HD.mp4 (<class 'opentimelineio._otio.Clip'>)\n"  # noqa E501 line too long
             "    source_range: TimeRange(RationalTime(159, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    trimmed_range: TimeRange(RationalTime(159, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    visible_range: TimeRange(RationalTime(159, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    range_in_parent: TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    trimmed range in timeline: TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    visible range in timeline: TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    range in Flattened (<class 'opentimelineio._otio.Track'>): TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    range in NestedScope (<class 'opentimelineio._otio.Stack'>): TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "TRACK: Flattened (Video)\n"
             "  CLIP: tech.fux (loop)-HD.mp4\n"
             "  CLIP: t-hawk (loop)-HD.mp4\n"
             "  CLIP: out-b (loop)-HD.mp4\n"
             "  CLIP: KOLL-HD.mp4\n"
             "  CLIP: brokchrd (loop)-HD.mp4\n"),
            out)

    def test_keep_flattened_tracks(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--flatten', 'video',
            '--keep-flattened-tracks',
            '--list-clips',
            '--list-tracks',
            '--inspect', 'out-b'
        ]
        out, err = self.run_test()
        self.assertEqual(
            ("TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "  ITEM: out-b (loop)-HD.mp4 (<class 'opentimelineio._otio.Clip'>)\n"  # noqa E501 line too long
             "    source_range: TimeRange(RationalTime(0, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    trimmed_range: TimeRange(RationalTime(0, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    visible_range: TimeRange(RationalTime(0, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    range_in_parent: TimeRange(RationalTime(803, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    trimmed range in timeline: TimeRange(RationalTime(803, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    visible range in timeline: TimeRange(RationalTime(803, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    range in Sequence (<class 'opentimelineio._otio.Track'>): TimeRange(RationalTime(803, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "    range in NestedScope (<class 'opentimelineio._otio.Stack'>): TimeRange(RationalTime(803, 24), RationalTime(722, 24))\n"  # noqa E501 line too long
             "  ITEM: out-b (loop)-HD.mp4 (<class 'opentimelineio._otio.Clip'>)\n"  # noqa E501 line too long
             "    source_range: TimeRange(RationalTime(159, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    trimmed_range: TimeRange(RationalTime(159, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    visible_range: TimeRange(RationalTime(159, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    range_in_parent: TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    trimmed range in timeline: TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    visible range in timeline: TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    range in Flattened (<class 'opentimelineio._otio.Track'>): TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "    range in NestedScope (<class 'opentimelineio._otio.Stack'>): TimeRange(RationalTime(962, 24), RationalTime(236, 24))\n"  # noqa E501 line too long
             "TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "TRACK: Sequence (Video)\n"
             "  CLIP: tech.fux (loop)-HD.mp4\n"
             "  CLIP: out-b (loop)-HD.mp4\n"
             "  CLIP: brokchrd (loop)-HD.mp4\n"
             "TRACK: Sequence 2 (Video)\n"
             "  CLIP: t-hawk (loop)-HD.mp4\n"
             "TRACK: Sequence 3 (Video)\n"
             "  CLIP: KOLL-HD.mp4\n"
             "TRACK: Flattened (Video)\n"
             "  CLIP: tech.fux (loop)-HD.mp4\n"
             "  CLIP: t-hawk (loop)-HD.mp4\n"
             "  CLIP: out-b (loop)-HD.mp4\n"
             "  CLIP: KOLL-HD.mp4\n"
             "  CLIP: brokchrd (loop)-HD.mp4\n"),
            out)

    def test_stack(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH, PREMIERE_EXAMPLE_PATH,
            '--stack',
            '--list-clips',
            '--list-tracks',
            '--stats'
        ]
        out, err = self.run_test()
        self.maxDiff = None
        self.assertEqual("""Name: Stacked 2 Timelines
Start:    00:00:00:00
End:      00:02:16:18
Duration: 00:02:16:18
TIMELINE: Stacked 2 Timelines
TRACK: Sequence (Video)
  CLIP: tech.fux (loop)-HD.mp4
  CLIP: out-b (loop)-HD.mp4
  CLIP: brokchrd (loop)-HD.mp4
TRACK: Sequence 2 (Video)
  CLIP: t-hawk (loop)-HD.mp4
TRACK: Sequence 3 (Video)
  CLIP: KOLL-HD.mp4
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh020_anim.mov
  CLIP: sc01_sh030_anim.mov
TRACK:  (Video)
  CLIP: test_title
TRACK:  (Video)
  CLIP: sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_placeholder.wav
TRACK:  (Audio)
  CLIP: track_08.wav
TRACK:  (Audio)
  CLIP: sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
""", out)

    def test_concat(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH, PREMIERE_EXAMPLE_PATH,
            '--concat',
            '--list-clips',
            '--list-tracks',
            '--stats'
        ]
        out, err = self.run_test()
        self.maxDiff = None
        self.assertEqual("""Name: Concatenated 2 Timelines
Start:    00:00:00:00
End:      00:02:59:03
Duration: 00:02:59:03
TIMELINE: Concatenated 2 Timelines
TRACK:  (Video)
TRACK: Sequence (Video)
  CLIP: tech.fux (loop)-HD.mp4
  CLIP: out-b (loop)-HD.mp4
  CLIP: brokchrd (loop)-HD.mp4
TRACK: Sequence 2 (Video)
  CLIP: t-hawk (loop)-HD.mp4
TRACK: Sequence 3 (Video)
  CLIP: KOLL-HD.mp4
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
TRACK:  (Video)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh020_anim.mov
  CLIP: sc01_sh030_anim.mov
TRACK:  (Video)
  CLIP: test_title
TRACK:  (Video)
  CLIP: sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_sh010_anim.mov
  CLIP: sc01_sh010_anim.mov
TRACK:  (Audio)
  CLIP: sc01_placeholder.wav
TRACK:  (Audio)
  CLIP: track_08.wav
TRACK:  (Audio)
  CLIP: sc01_master_layerA_sh030_temp.mov
  CLIP: sc01_sh010_anim.mov
""", out)

    def test_redact(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--redact',
            '--list-clips',
            '--list-tracks'
        ]
        out, err = self.run_test()
        self.assertEqual("""TIMELINE: Timeline #1
TRACK: Track #1 (Video)
  CLIP: Clip #1
  CLIP: Clip #2
  CLIP: Clip #3
TRACK: Track #2 (Video)
  CLIP: Clip #4
TRACK: Track #3 (Video)
  CLIP: Clip #5
""", out)

    def test_stats(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--stats'
        ]
        out, err = self.run_test()
        self.assertEqual("""Name: OTIO TEST - multitrack.Exported.01
Start:    00:00:00:00
End:      00:02:16:18
Duration: 00:02:16:18
""", out)

    def test_inspect(self):
        sys.argv = [
            'otiotool',
            '-i', MULTITRACK_PATH,
            '--inspect', 'KOLL'
        ]
        out, err = self.run_test()
        self.assertEqual(
            ("TIMELINE: OTIO TEST - multitrack.Exported.01\n"
             "  ITEM: KOLL-HD.mp4 (<class 'opentimelineio._otio.Clip'>)\n"
             "    source_range: TimeRange(RationalTime(0, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    trimmed_range: TimeRange(RationalTime(0, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    visible_range: TimeRange(RationalTime(0, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    range_in_parent: TimeRange(RationalTime(1198, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    trimmed range in timeline: TimeRange(RationalTime(1198, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    visible range in timeline: TimeRange(RationalTime(1198, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    range in Sequence 3 (<class 'opentimelineio._otio.Track'>): TimeRange(RationalTime(1198, 24), RationalTime(640, 24))\n"  # noqa E501 line too long
             "    range in NestedScope (<class 'opentimelineio._otio.Stack'>): TimeRange(RationalTime(1198, 24), RationalTime(640, 24))\n"),  # noqa E501 line too long
            out)

    def test_relink(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file1 = os.path.join(temp_dir, "Clip-001.empty")
            temp_file2 = os.path.join(temp_dir, "Clip-003.empty")
            open(temp_file1, "w").write("A")
            open(temp_file2, "w").write("B")

            temp_url = pathlib.Path(temp_dir).as_uri()

            sys.argv = [
                'otiotool',
                '-i', SIMPLE_CUT_PATH,
                '--relink-by-name', temp_dir,
                '--list-media'
            ]
            out, err = self.run_test()
            self.assertIn(
                ("TIMELINE: Figure 1 - Simple Cut List\n"
                 f"    MEDIA: {temp_url}/Clip-001.empty\n"
                 "    MEDIA: file:///folder/wind-up.mov\n"
                 f"    MEDIA: {temp_url}/Clip-003.empty\n"
                 "    MEDIA: file:///folder/credits.mov\n"),
                out)


OTIOToolTest_ShellOut = CreateShelloutTest(OTIOToolTest)


if __name__ == '__main__':
    unittest.main()
