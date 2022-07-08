# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the 'examples'"""
import unittest
import sys
import os
import subprocess


# handle python2 vs python3 difference
try:
    from tempfile import TemporaryDirectory  # noqa: F401
    import tempfile
except ImportError:
    # XXX: python2.7 only
    from backports import tempfile

import opentimelineio as otio


class BuildSimpleTimelineExampleTest(unittest.TestCase):
    """use the build_simple_timeline.py example to generate timelines"""

    def test_duration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "test_basic.otio")

            examples_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "examples",
                "build_simple_timeline.py",
            )

            subprocess.check_call(
                [sys.executable, examples_path, temp_file],
                stdout=subprocess.PIPE
            )
            known = otio.adapters.read_from_file(temp_file)

            # checks against a couple of the adapters
            for suffix in [".xml", ".edl", ".otio"]:
                this_test_file = temp_file.replace(".otio", suffix)
                subprocess.check_call(
                    [sys.executable, examples_path, this_test_file],
                    stdout=subprocess.PIPE
                )
                test_result = otio.adapters.read_from_file(this_test_file)
                self.assertEqual(known.duration(), test_result.duration())


if __name__ == '__main__':
    unittest.main()
