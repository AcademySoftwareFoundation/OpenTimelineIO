# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

""" Unit tests of functions that convert between file paths and urls. """

import unittest
import os

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SCREENING_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "screening_example.edl")
PREMIERE_XML_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "premiere_example.xml")
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

    def test_premiere_xml_urls(self):
        timeline = otio.adapters.read_from_file(PREMIERE_XML_EXAMPLE_PATH)
        for clip in timeline.find_clips():
            media_ref = clip.media_reference

            if hasattr(media_ref, 'target_url') and media_ref.target_url is not None:
                url = media_ref.target_url
                self.assertTrue(url.startswith("file://"))
                processed_url = otio.url_utils.filepath_from_url(url)
                self.assertNotEquals(url, processed_url)


if __name__ == "__main__":
    unittest.main()
