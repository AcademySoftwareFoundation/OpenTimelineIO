#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOZ adapter."""

import unittest
import os
import pathlib
import tempfile
import zipfile

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

    def test_target_schema_versions(self):
        """A bundle can be written at older schema versions, for an older OTIO
        to read."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tl = otio.schema.Timeline()
            tl.tracks.markers.append(
                otio.schema.Marker(name="m", color=otio.core.Color.GREEN))

            otioz_path = os.path.join(temp_dir, "versions.otioz")
            otio.adapters.write_to_file(
                tl, otioz_path, target_schema_versions={"Marker": 2})

            with zipfile.ZipFile(otioz_path) as zf:
                content = zf.read("content.otio").decode("utf-8")
            self.assertIn('"Marker.2"', content)

            result = otio.adapters.read_from_file(otioz_path)
            self.assertEqual(result.tracks.markers[0].color,
                             otio.core.Color.GREEN)


if __name__ == "__main__":
    unittest.main()
