# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

""" Unit tests of functions that convert between file paths and urls. """

import unittest
import os

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
MEDIA_EXAMPLE_PATH_REL = os.path.relpath(
    os.path.join(
        os.path.dirname(__file__),
        "..",  # root
        "docs",
        "_static",
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

ENCODED_WINDOWS_URL = "file://host/S%3a/path/file.ext"
WINDOWS_DRIVE_URL = "file://S:/path/file.ext"
CORRECTED_WINDOWS_DRIVE_PATH = "S:/path/file.ext"

ENCODED_WINDOWS_UNC_URL = "file://unc/path/sub%20dir/file.ext"
WINDOWS_UNC_URL = "file://unc/path/sub dir/file.ext"
CORRECTED_WINDOWS_UNC_PATH = "//unc/path/sub dir/file.ext"

POSIX_LOCALHOST_URL = "file://localhost/path/sub dir/file.ext"
ENCODED_POSIX_URL = "file:///path/sub%20dir/file.ext"
POSIX_URL = "file:///path/sub dir/file.ext"
CORRECTED_POSIX_PATH = "/path/sub dir/file.ext"


class TestConversions(unittest.TestCase):
    def test_roundtrip_abs(self):
        self.assertTrue(MEDIA_EXAMPLE_PATH_URL_ABS.startswith("file://"))
        full_path = os.path.abspath(
            otio.url_utils.filepath_from_url(MEDIA_EXAMPLE_PATH_URL_ABS)
        )

        # should have reconstructed it by this point
        self.assertEqual(full_path, MEDIA_EXAMPLE_PATH_ABS)

    def test_roundtrip_rel(self):
        self.assertFalse(MEDIA_EXAMPLE_PATH_URL_REL.startswith("file://"))

        result = otio.url_utils.filepath_from_url(MEDIA_EXAMPLE_PATH_URL_REL)

        # should have reconstructed it by this point
        self.assertEqual(os.path.normpath(result), MEDIA_EXAMPLE_PATH_REL)

    def test_windows_urls(self):
        for url in (ENCODED_WINDOWS_URL, WINDOWS_DRIVE_URL):
            processed_url = otio.url_utils.filepath_from_url(url)
            self.assertEqual(processed_url, CORRECTED_WINDOWS_DRIVE_PATH)

    def test_windows_unc_urls(self):
        for url in (ENCODED_WINDOWS_UNC_URL, WINDOWS_UNC_URL):
            processed_url = otio.url_utils.filepath_from_url(url)
            self.assertEqual(processed_url, CORRECTED_WINDOWS_UNC_PATH)

    def test_posix_urls(self):
        for url in (ENCODED_POSIX_URL, POSIX_URL, POSIX_LOCALHOST_URL):
            processed_url = otio.url_utils.filepath_from_url(url)
            self.assertEqual(processed_url, CORRECTED_POSIX_PATH)


if __name__ == "__main__":
    unittest.main()
