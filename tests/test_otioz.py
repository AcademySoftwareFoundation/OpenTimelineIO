#!/usr/bin/env python
#
# Copyright 2019 Pixar Animation Studios
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

"""Tests for the OTIOZ adapter."""

import unittest
import os
import tempfile
import shutil

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
MEDIA_EXAMPLE_PATH = os.path.join(
    "file://{}".format(os.path.dirname(__file__)),
    "..",  # root
    "docs",
    "_static",
    "OpenTimelineIO@3xDark.png"
)


class OTIOZTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        # convert to contrived local reference
        for cl in tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(
                target_url=MEDIA_EXAMPLE_PATH
            )

        self.tl = tl

    def test_dryrun(self):
        # dryrun should compute what the total size of the zipfile will be.
        tmp_path = tempfile.mkstemp(suffix=".otioz", text=False)[1]
        size = otio.adapters.write_to_file(self.tl, tmp_path, dryrun=True)
        self.assertEqual(
            size,
            os.path.getsize(MEDIA_EXAMPLE_PATH.split("file://")[1])
        )

    def test_not_a_file_error(self):
        # dryrun should compute what the total size of the zipfile will be.
        tmp_path = tempfile.mkstemp(suffix=".otioz", text=False)[1]
        with tempfile.NamedTemporaryFile() as bogusfile:
            fname = bogusfile.name
        for cl in self.tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(
                target_url=fname
            )
        with self.assertRaises(otio.exceptions.OTIOError):
            otio.adapters.write_to_file(self.tl, tmp_path, dryrun=True)

        for cl in self.tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(
                target_url="file://{}".format(fname)
            )
        with self.assertRaises(otio.exceptions.OTIOError):
            otio.adapters.write_to_file(self.tl, tmp_path, dryrun=True)

        tempdir = tempfile.mkdtemp()
        fname = tempdir
        shutil.rmtree(tempdir)
        for cl in self.tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(target_url=fname)

    def test_round_trip(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otioz").name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assert_(os.path.exists(tmp_path))

        result = otio.adapters.read_from_file(tmp_path)
        self.assertJsonEqual(result, self.tl)

    def test_round_trip_with_extraction(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otioz").name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assert_(os.path.exists(tmp_path))

        tempdir = tempfile.mkdtemp()
        result = otio.adapters.read_from_file(
            tmp_path,
            extract_to_directory=tempdir
        )
        self.assertJsonEqual(result, self.tl)

        self.assert_(
            os.path.exists(
                os.path.join(
                    tempdir,
                    otio.adapters.from_name("otioz").module().BUNDLE_DIR_NAME
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
