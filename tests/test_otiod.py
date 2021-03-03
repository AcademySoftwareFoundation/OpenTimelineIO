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

"""Tests for the OTIOD adapter."""

import unittest
import os
import tempfile

import opentimelineio as otio
from opentimelineio import test_utils as otio_test_utils
from opentimelineio.adapters import file_bundle_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")

MEDIA_EXAMPLE_PATH_REL = file_bundle_utils.file_url_of(
    os.path.relpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",  # root
            "docs",
            "_static",
            "OpenTimelineIO@3xDark.png"
        )
    )
)
MEDIA_EXAMPLE_PATH_ABS = file_bundle_utils.file_url_of(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",  # root
            "docs",
            "_static",
            "OpenTimelineIO@3xLight.png"
        )
    )
)


class OTIODTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        tl_rel = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        # convert to contrived local reference
        last_rel = False
        for cl in tl_rel.each_clip():
            # vary the relative and absolute paths, make sure that both work
            next_rel = (
                MEDIA_EXAMPLE_PATH_REL if last_rel else MEDIA_EXAMPLE_PATH_ABS
            )
            last_rel = not last_rel
            cl.media_reference = otio.schema.ExternalReference(
                target_url=next_rel
            )

        self.tl = tl_rel

    def test_file_bundle_manifest(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otiod").name
        manifest = file_bundle_utils._file_bundle_manifest(
            input_otio=self.tl,
            dest_path=tmp_path,
            media_policy=file_bundle_utils.MediaReferencePolicy.AllMissing,
            adapter_name="TEST_NAME",
        )

        # should include the abs and rel paths
        self.assertEqual(len(manifest), 2)
        self.assertEqual(
            set(manifest),
            set([MEDIA_EXAMPLE_PATH_REL, MEDIA_EXAMPLE_PATH_ABS])
        )
        for thing in manifest:
            self.assertNotIn(
                "..",
                thing,
                msg="found '..' in '{}'".format(thing)
            )
            self.assertNotIn(
                "file:",
                thing,
                msg="found 'file:' in '{}'".format(thing)
            )

    def test_round_trip(self):
        tmp_path = tempfile.NamedTemporaryFile(suffix=".otiod").name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        # by default will provide relative paths
        result = otio.adapters.read_from_file(
            tmp_path,
        )

        for cl in result.each_clip():
            self.assertNotEqual(
                cl.media_reference.target_url,
                MEDIA_EXAMPLE_PATH_REL
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.each_clip():
            # construct an absolute file path to the result
            cl.media_reference.target_url = (
                otio.adapters.file_bundle_utils.file_url_of(
                    os.path.join(
                        otio.adapters.file_bundle_utils.BUNDLE_DIR_NAME,
                        os.path.basename(cl.media_reference.target_url)
                    )
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
                MEDIA_EXAMPLE_PATH_REL
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.each_clip():
            # should be only field that changed
            cl.media_reference.target_url = (
                otio.adapters.file_bundle_utils.file_url_of(
                    os.path.join(
                        tmp_path,
                        otio.adapters.file_bundle_utils.BUNDLE_DIR_NAME,
                        os.path.basename(cl.media_reference.target_url)
                    )
                )
            )

        self.assertJsonEqual(result, self.tl)


if __name__ == "__main__":
    unittest.main()
