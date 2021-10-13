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
