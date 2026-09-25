#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOD adapter."""

import unittest
import os
import pathlib
import tempfile

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

    def test_read_without_version_file(self):
        # The adapter that wrote otiod bundles before the C++ implementation
        # did not write a version file, so reading one must not require it.
        with tempfile.TemporaryDirectory() as temp_dir:
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)
            ref = otio.schema.ExternalReference("video.mov")
            cl.media_reference = ref
            pathlib.Path(os.path.join(temp_dir, ref.target_url)).touch()

            otiod_path = os.path.join(temp_dir, "no_version.otiod")
            otio.adapters.write_to_file(
                tl,
                otiod_path,
                relative_media_base_dir=temp_dir)

            version_path = os.path.join(otiod_path, "version.txt")
            self.assertTrue(os.path.isfile(version_path))
            os.remove(version_path)

            result = otio.adapters.read_from_file(otiod_path)
            self.assertIsNotNone(result)

    def test_media_policy_as_string(self):
        # The policy arrives as a string from the commandline, in either the
        # name the enumeration uses or the one the adapters used before it.
        with tempfile.TemporaryDirectory() as temp_dir:
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)
            cl.media_reference = otio.schema.ExternalReference(
                "http://example.com/video.mov")

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
