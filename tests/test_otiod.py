#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOD adapter."""

import unittest
import os
import tempfile

import opentimelineio as otio
from opentimelineio import test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.otio")

MEDIA_EXAMPLE_PATH_REL = os.path.relpath(
    os.path.join(
        SAMPLE_DATA_DIR,
        "OpenTimelineIO@3xDark.png"
    )
)
MEDIA_EXAMPLE_PATH_URL_REL = otio._otio.bundle.url_from_filepath(
    MEDIA_EXAMPLE_PATH_REL
)
MEDIA_EXAMPLE_PATH_ABS = os.path.abspath(
    MEDIA_EXAMPLE_PATH_REL.replace(
        "3xDark",
        "3xLight"
    )
)
MEDIA_EXAMPLE_PATH_URL_ABS = otio._otio.bundle.url_from_filepath(
    MEDIA_EXAMPLE_PATH_ABS
)


class OTIODTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        # convert to contrived local reference
        last_rel = False
        for cl in tl.find_clips():
            # vary the relative and absolute paths, make sure that both work
            next_rel = (
                MEDIA_EXAMPLE_PATH_URL_REL if last_rel else MEDIA_EXAMPLE_PATH_URL_ABS
            )
            last_rel = not last_rel
            cl.media_reference = otio.schema.ExternalReference(
                target_url=next_rel
            )

        self.tl = tl

    def test_round_trip(self):
        with tempfile.NamedTemporaryFile(suffix=".otiod") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        # by default will provide relative paths
        result = otio.adapters.read_from_file(
            tmp_path,
        )

        for cl in result.find_clips():
            self.assertNotEqual(
                cl.media_reference.target_url,
                MEDIA_EXAMPLE_PATH_URL_REL
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.find_clips():
            # construct an absolute file path to the result
            cl.media_reference.target_url = (
                otio._otio.bundle.url_from_filepath(
                    os.path.join(
                        otio._otio.bundle.media_dir,
                        os.path.basename(cl.media_reference.target_url)
                    )
                )
            )

        self.assertJsonEqual(result, self.tl)

    def test_round_trip_all_missing_references(self):
        with tempfile.NamedTemporaryFile(suffix=".otiod") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(
            self.tl,
            tmp_path,
            media_policy=(
                otio._otio.bundle.MediaReferencePolicy.AllMissing
            )
        )

        # ...but can be optionally told to generate absolute paths
        result = otio.adapters.read_from_file(
            tmp_path,
            absolute_media_reference_paths=True
        )

        for cl in result.find_clips():
            self.assertIsInstance(
                cl.media_reference,
                otio.schema.MissingReference
            )

    def test_round_trip_absolute_paths(self):
        with tempfile.NamedTemporaryFile(suffix=".otiod") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(self.tl, tmp_path)

        # ...but can be optionally told to generate absolute paths
        result = otio.adapters.read_from_file(
            tmp_path,
            absolute_media_reference_paths=True
        )

        for cl in result.find_clips():
            self.assertNotEqual(
                cl.media_reference.target_url,
                MEDIA_EXAMPLE_PATH_URL_REL
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.find_clips():
            # should be only field that changed
            cl.media_reference.target_url = (
                otio._otio.bundle.url_from_filepath(
                    os.path.join(
                        tmp_path,
                        otio._otio.bundle.media_dir,
                        os.path.basename(cl.media_reference.target_url)
                    )
                )
            )

        self.assertJsonEqual(result, self.tl)


if __name__ == "__main__":
    unittest.main()
