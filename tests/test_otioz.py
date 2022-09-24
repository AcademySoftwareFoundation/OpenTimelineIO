#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOZ adapter."""

import unittest
import os
import tempfile
import shutil

import urllib.parse as urlparse

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
MEDIA_EXAMPLE_PATH_REL = os.path.relpath(
    os.path.join(
        SAMPLE_DATA_DIR,
        "OpenTimelineIO@3xDark.png"
    )
)
MEDIA_EXAMPLE_PATH_URL_REL = otio.url_utils.url_from_filepath(
    MEDIA_EXAMPLE_PATH_REL
)
MEDIA_EXAMPLE_PATH_ABS = os.path.abspath(
    MEDIA_EXAMPLE_PATH_REL.replace(
        "3xDark",
        "3xLight"
    )
)
MEDIA_EXAMPLE_PATH_URL_ABS = otio.url_utils.url_from_filepath(
    MEDIA_EXAMPLE_PATH_ABS
)


class OTIOZTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        tl = otio.adapters.read_from_file(SCREENING_EXAMPLE_PATH)

        # convert to contrived local reference
        last_rel = False
        for cl in tl.each_clip():
            # vary the relative and absolute paths, make sure that both work
            next_rel = (
                MEDIA_EXAMPLE_PATH_URL_REL
                if last_rel else MEDIA_EXAMPLE_PATH_URL_ABS
            )
            last_rel = not last_rel
            cl.media_reference = otio.schema.ExternalReference(
                target_url=next_rel
            )

        self.tl = tl

    def test_dryrun(self):
        # generate a fake name
        with tempfile.NamedTemporaryFile(suffix=".otioz") as bogusfile:
            fname = bogusfile.name

        # dryrun should compute what the total size of the zipfile will be.
        size = otio.adapters.write_to_file(self.tl, fname, dryrun=True)
        self.assertEqual(
            size,
            os.path.getsize(MEDIA_EXAMPLE_PATH_ABS) +
            os.path.getsize(MEDIA_EXAMPLE_PATH_REL)
        )

    def test_not_a_file_error(self):
        # dryrun should compute what the total size of the zipfile will be.
        tmp_path = tempfile.mkstemp(suffix=".otioz", text=False)[1]
        with tempfile.NamedTemporaryFile() as bogusfile:
            fname = bogusfile.name
        for cl in self.tl.each_clip():
            # write with a non-file schema
            cl.media_reference = otio.schema.ExternalReference(
                target_url="http://{}".format(fname)
            )
        with self.assertRaises(otio.exceptions.OTIOError):
            otio.adapters.write_to_file(self.tl, tmp_path, dryrun=True)

        for cl in self.tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(
                target_url=otio.url_utils.url_from_filepath(fname)
            )
        with self.assertRaises(otio.exceptions.OTIOError):
            otio.adapters.write_to_file(self.tl, tmp_path, dryrun=True)

        tempdir = tempfile.mkdtemp()
        fname = tempdir
        shutil.rmtree(tempdir)
        for cl in self.tl.each_clip():
            cl.media_reference = otio.schema.ExternalReference(target_url=fname)

    def test_colliding_basename(self):
        tempdir = tempfile.mkdtemp()
        new_path = os.path.join(
            tempdir,
            os.path.basename(MEDIA_EXAMPLE_PATH_ABS)
        )
        shutil.copyfile(
            MEDIA_EXAMPLE_PATH_ABS,
            new_path
        )
        list(self.tl.each_clip())[0].media_reference.target_url = (
            otio.url_utils.url_from_filepath(new_path)
        )

        tmp_path = tempfile.mkstemp(suffix=".otioz", text=False)[1]
        with self.assertRaises(otio.exceptions.OTIOError):
            otio.adapters.write_to_file(self.tl, tmp_path)

        with self.assertRaises(otio.exceptions.OTIOError):
            otio.adapters.write_to_file(self.tl, tmp_path, dryrun=True)

        shutil.rmtree(tempdir)

    def test_round_trip(self):
        with tempfile.NamedTemporaryFile(suffix=".otioz") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        result = otio.adapters.read_from_file(tmp_path)

        for cl in result.each_clip():
            self.assertNotIn(
                cl.media_reference.target_url,
                [MEDIA_EXAMPLE_PATH_URL_ABS, MEDIA_EXAMPLE_PATH_URL_REL]
            )
            # ensure that unix style paths are used, so that bundles created on
            # windows are compatible with ones created on unix
            self.assertFalse(
                urlparse.urlparse(
                    cl.media_reference.target_url
                ).path.startswith(
                    "media\\"
                )
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.each_clip():
            # should be only field that changed
            cl.media_reference.target_url = "media/{}".format(
                os.path.basename(cl.media_reference.target_url)
            )

        self.assertJsonEqual(result, self.tl)

    def test_round_trip_with_extraction(self):
        with tempfile.NamedTemporaryFile(suffix=".otioz") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        tempdir = tempfile.mkdtemp()
        result = otio.adapters.read_from_file(
            tmp_path,
            extract_to_directory=tempdir
        )

        # make sure that all the references are ExternalReference
        for cl in result.each_clip():
            self.assertIsInstance(
                cl.media_reference,
                otio.schema.ExternalReference
            )

        # conform media references in input to what they should be in the output
        for cl in self.tl.each_clip():
            # should be only field that changed
            cl.media_reference.target_url = "media/{}".format(
                os.path.basename(cl.media_reference.target_url)
            )

        self.assertJsonEqual(result, self.tl)

        # content file
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    tempdir,
                    otio.adapters.file_bundle_utils.BUNDLE_PLAYLIST_PATH
                )
            )
        )

        # media directory overall
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    tempdir,
                    otio.adapters.file_bundle_utils.BUNDLE_DIR_NAME
                )
            )
        )

        # actual media file
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    tempdir,
                    otio.adapters.file_bundle_utils.BUNDLE_DIR_NAME,
                    os.path.basename(MEDIA_EXAMPLE_PATH_URL_REL)
                )
            )
        )

    def test_round_trip_with_extraction_no_media(self):
        with tempfile.NamedTemporaryFile(suffix=".otioz") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(
            self.tl,
            tmp_path,
            media_policy=(
                otio.adapters.file_bundle_utils.MediaReferencePolicy.AllMissing
            ),
        )

        tempdir = tempfile.mkdtemp()
        result = otio.adapters.read_from_file(
            tmp_path,
            extract_to_directory=tempdir,
        )

        version_file_path = os.path.join(
            tempdir,
            otio.adapters.file_bundle_utils.BUNDLE_VERSION_FILE
        )
        self.assertTrue(os.path.exists(version_file_path))
        with open(version_file_path, 'r') as fi:
            self.assertEqual(
                fi.read(),
                otio.adapters.file_bundle_utils.BUNDLE_VERSION
            )

        # conform media references in input to what they should be in the output
        for cl in result.each_clip():
            # should be all MissingReferences
            self.assertIsInstance(
                cl.media_reference,
                otio.schema.MissingReference
            )
            self.assertIn("original_target_url", cl.media_reference.metadata)


if __name__ == "__main__":
    unittest.main()
