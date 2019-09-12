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

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

try:
    # Python 2.7
    import urlparse
except ImportError:
    # Python 3
    import urllib.parse as urlparse

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
MEDIA_EXAMPLE_PATH = os.path.join(
    "file:{}".format(os.path.dirname(__file__)),
    "..",  # root
    "docs",
    "_static",
    "OpenTimelineIO@3xDark.png"
)
MEDIA_EXAMPLE_URL_PARSED = urlparse.urlparse(MEDIA_EXAMPLE_PATH)


class OTIODTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        # convert to contrived local reference
        for cl in tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(
                target_url=MEDIA_EXAMPLE_PATH
            )

        self.tl = tl

    def test_round_trip(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otiod").name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assert_(os.path.exists(tmp_path))

        # by default will provide relative paths
        result = otio.adapters.read_from_file(
            tmp_path,
        )

        for cl in result.each_clip():
            self.assertNotEqual(
                cl.media_reference.target_url,
                MEDIA_EXAMPLE_PATH
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.each_clip():
            # should be only field that changed
            cl.media_reference.target_url = "file:{}".format(
                os.path.join(
                    otio.adapters.file_bundle_utils.BUNDLE_DIR_NAME,
                    os.path.basename(cl.media_reference.target_url)
                )
            )

        self.assertJsonEqual(result, self.tl)

    def test_round_trip_all_missing_references(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otiod").name
        otio.adapters.write_to_file(
            self.tl,
            tmp_path,
            media_policy=(
                otio.adapters.file_bundle_utils.MediaReferencePolicy.AllMissing
            )
        )

        # ...but can be optionally told to generate absolute paths
        result = otio.adapters.read_from_file(
            tmp_path,
            absolute_media_reference_paths=True
        )

        for cl in result.each_clip():
            self.assertIsInstance(
                cl.media_reference,
                otio.schema.MissingReference
            )

    def test_round_trip_absolute_paths(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otiod").name
        otio.adapters.write_to_file(self.tl, tmp_path)

        # ...but can be optionally told to generate absolute paths
        result = otio.adapters.read_from_file(
            tmp_path,
            absolute_media_reference_paths=True
        )

        for cl in result.each_clip():
            self.assertNotEqual(
                cl.media_reference.target_url,
                MEDIA_EXAMPLE_PATH
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.each_clip():
            # should be only field that changed
            cl.media_reference.target_url = "file:{}".format(
                os.path.join(
                    tmp_path,
                    otio.adapters.file_bundle_utils.BUNDLE_DIR_NAME,
                    os.path.basename(cl.media_reference.target_url)
                )
            )

        self.assertJsonEqual(result, self.tl)


if __name__ == "__main__":
    unittest.main()
