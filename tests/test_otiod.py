#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOD adapter."""

import unittest
import os
import pathlib
import tempfile
from unittest import mock

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class OTIODTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
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

            # Write to otiod
            otiod_path = os.path.join(temp_dir, "round_trip.otiod")
            otio.adapters.write_to_file(
                tl,
                otiod_path,
                relative_media_base_dir=temp_dir)

            # Read from otiod
            result = otio.adapters.read_from_file(otiod_path)
            self.assertIsNotNone(result)

    def _write_marker_timeline(self, otiod_path, **kwargs):
        tl = otio.schema.Timeline()
        tl.tracks.markers.append(
            otio.schema.Marker(name="m", color=otio.core.Color.GREEN))
        otio.adapters.write_to_file(tl, otiod_path, **kwargs)

        with open(os.path.join(otiod_path, "content.otio")) as f:
            return f.read()

    def test_target_schema_versions(self):
        """A bundle can be written at older schema versions, for an older OTIO
        to read."""
        with tempfile.TemporaryDirectory() as temp_dir:
            otiod_path = os.path.join(temp_dir, "versions.otiod")
            content = self._write_marker_timeline(
                otiod_path, target_schema_versions={"Marker": 2})
            self.assertIn('"Marker.2"', content)
            self.assertIn('"GREEN"', content)

            result = otio.adapters.read_from_file(otiod_path)
            self.assertEqual(result.tracks.markers[0].color,
                             otio.core.Color.GREEN)

    def test_target_schema_versions_from_env(self):
        """OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL is used when
        target_schema_versions isn't given, as for .otio files."""
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.dict(
            os.environ,
            {"OTIO_DEFAULT_TARGET_VERSION_FAMILY_LABEL": "OTIO_CORE:0.18.1"}
        ):
            content = self._write_marker_timeline(
                os.path.join(temp_dir, "env.otiod"))
            self.assertIn('"Marker.2"', content)

    def test_media_policy_as_string(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)
            cl.media_reference = otio.schema.ExternalReference(
                "http://example.com/video.mov")

            # Test both the old and new strings.
            for i, policy in enumerate(("all_missing", "AllMissing")):
                otiod_path = os.path.join(temp_dir, "policy%d.otiod" % i)
                otio.adapters.write_to_file(
                    tl,
                    otiod_path,
                    relative_media_base_dir=temp_dir,
                    media_policy=policy)
                self.assertIsNotNone(otio.adapters.read_from_file(otiod_path))

            with self.assertRaises(ValueError):
                otio.adapters.write_to_file(
                    tl,
                    os.path.join(temp_dir, "bad.otiod"),
                    relative_media_base_dir=temp_dir,
                    media_policy="not_a_policy")


if __name__ == "__main__":
    unittest.main()
