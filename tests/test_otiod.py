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
IMAGE0_EXAMPLE = "OpenTimelineIO@3xDark.png"
IMAGE0_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, IMAGE0_EXAMPLE)
IMAGE1_EXAMPLE = "OpenTimelineIO@3xLight.png"
IMAGE1_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, IMAGE1_EXAMPLE)


class OTIODTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        track = otio.schema.Track(name="track")
        mr0 = otio.schema.ExternalReference(
            available_range=otio.opentime.TimeRange(
                duration=otio.opentime.RationalTime(1, 24)
            ),
            target_url=IMAGE0_EXAMPLE_PATH
        )
        cl0 = otio.schema.Clip(
            name="clip 0",
            media_reference=mr0,
            source_range=otio.opentime.TimeRange(
                duration=otio.opentime.RationalTime(24, 24)
            ),
        )
        track.append(cl0)
        mr1 = otio.schema.ExternalReference(
            available_range=otio.opentime.TimeRange(
                duration=otio.opentime.RationalTime(1, 24)
            ),
            target_url=IMAGE1_EXAMPLE_PATH
        )
        cl1 = otio.schema.Clip(
            name="clip 1",
            media_reference=mr1,
            source_range=otio.opentime.TimeRange(
                duration=otio.opentime.RationalTime(24, 24)
            ),
        )
        track.append(cl1)
        self.tl = otio.schema.Timeline("test_round_trip", tracks=[track])

    def test_round_trip(self):

        with tempfile.NamedTemporaryFile(suffix=".otiod") as bogusfile:
            tmp_path = bogusfile.name
        otio.adapters.write_to_file(self.tl, tmp_path)
        self.assertTrue(os.path.exists(tmp_path))

        result = otio.adapters.read_from_file(tmp_path)

        clips = result.find_clips()
        # \todo
        # self.assertTrue(
        #     clips[0].media_reference.target_url.endswith(IMAGE0_EXAMPLE)
        # )
        # self.assertTrue(
        #     clips[1].media_reference.target_url.endswith(IMAGE1_EXAMPLE)
        # )

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

        result = otio.adapters.read_from_file(
            tmp_path,
            absolute_media_reference_paths=True
        )

        clips = result.find_clips()
        # \todo
        # self.assertTrue(
        #     clips[0].media_reference.target_url.endswith(IMAGE0_EXAMPLE)
        # )
        # self.assertTrue(
        #     clips[1].media_reference.target_url.endswith(IMAGE1_EXAMPLE)
        # )


if __name__ == "__main__":
    unittest.main()
