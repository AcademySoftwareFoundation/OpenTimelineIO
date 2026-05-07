#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for the OTIOZ adapter."""

import unittest
import os
import pathlib
import shutil
import tempfile

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class OTIOZTester(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tl = otio.schema.Timeline()
            tr = otio.schema.Track()
            tl.tracks.append(tr)
            cl = otio.schema.Clip()
            tr.append(cl)
            ref = otio.schema.ExternalReference("video.mov")
            cl.media_reference = ref

            pathlib.Path(os.path.join(temp_dir, ref.target_url)).touch()

            otioz_path = os.path.join(temp_dir, "round_trip.otioz")
            otio.adapters.write_to_file(
                tl,
                otioz_path,
                relative_media_path=temp_dir)
            
            result = otio.adapters.read_from_file(otioz_path)

if __name__ == "__main__":
    unittest.main()
