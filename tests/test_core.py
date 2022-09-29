# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import sys
import shutil
import tempfile
import unittest

import opentimelineio as otio


class TestCoreFunctions(unittest.TestCase):
    def setUp(self):
        self.tmpDir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpDir)

    def test_deserialize_json_from_file_errors(self):
        """Verify the bindings return the correct errors based on the errno"""

        with self.assertRaises(FileNotFoundError) as exc:
            otio.core.deserialize_json_from_file('non-existent-file-here')
        self.assertIsInstance(exc.exception, FileNotFoundError)

    @unittest.skipUnless(
        not sys.platform.startswith("win"),
        "requires non Windows system"
    )
    def test_serialize_json_to_file_errors_non_windows(self):
        """Verify the bindings return the correct errors based on the errno"""

        with self.assertRaises(IsADirectoryError) as exc:
            otio.core.serialize_json_to_file({}, self.tmpDir)
        self.assertIsInstance(exc.exception, IsADirectoryError)

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_serialize_json_to_file_errors_windows(self):
        """Verify the bindings return the correct errors based on the errno"""

        with self.assertRaises(PermissionError) as exc:
            otio.core.serialize_json_to_file({}, self.tmpDir)
        self.assertIsInstance(exc.exception, PermissionError)
