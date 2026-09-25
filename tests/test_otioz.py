#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOZ adapter."""

import unittest
import os
import pathlib
import tempfile

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class OTIOZTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            # Create a timeline
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)

            # Add a media reference
            ref = otio.schema.ExternalReference("video.mov")
            cl.media_reference = ref
            pathlib.Path(os.path.join(temp_dir, ref.target_url)).touch()

            # Write to otioz
            otioz_path = os.path.join(temp_dir, "round_trip.otioz")
            otio.adapters.write_to_file(
                tl,
                otioz_path,
                relative_media_base_dir=temp_dir)

            # Read from otiod
            result = otio.adapters.read_from_file(otioz_path)
            self.assertIsNotNone(result)

    def test_media_policy_as_string(self):
        # As for otiod: the policy may arrive as a string.
        with tempfile.TemporaryDirectory() as temp_dir:
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)
            cl.media_reference = otio.schema.ExternalReference(
                "http://example.com/video.mov")

            otioz_path = os.path.join(temp_dir, "policy.otioz")
            otio.adapters.write_to_file(
                tl,
                otioz_path,
                relative_media_base_dir=temp_dir,
                media_policy="AllMissing")
            self.assertIsNotNone(otio.adapters.read_from_file(otioz_path))


if __name__ == "__main__":
    unittest.main()
