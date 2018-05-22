#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Test the ALE adapter."""

# python
import os
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "sample.ale")
EXAMPLE2_PATH = os.path.join(SAMPLE_DATA_DIR, "sample2.ale")


class ALEAdapterTest(unittest.TestCase):

    def test_ale_read(self):
        ale_path = EXAMPLE_PATH
        collection = otio.adapters.read_from_file(ale_path)
        self.assertTrue(collection is not None)
        self.assertEqual(type(collection), otio.schema.SerializableCollection)
        self.assertEqual(len(collection), 4)
        fps = float(collection.metadata.get("ALE").get("header").get("FPS"))
        self.assertEqual(fps, 24)
        self.assertEqual(
            [c.name for c in collection],
            ["test_017056", "test_017057", "test_017058", "Something"]
        )
        self.assertEqual(
            [c.source_range for c in collection],
            [
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:03", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:04", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:05", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("01:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:04:06", fps)
                )
            ]
        )

    def test_ale_read2(self):
        ale_path = EXAMPLE2_PATH
        collection = otio.adapters.read_from_file(ale_path)
        self.assertTrue(collection is not None)
        self.assertEqual(type(collection), otio.schema.SerializableCollection)
        self.assertEqual(len(collection), 2)
        fps = float(collection.metadata.get("ALE").get("header").get("FPS"))
        self.assertEqual(fps, 23.98)
        self.assertEqual(
            [c.name for c in collection],
            ["19A-1xa", "19A-2xa"]
        )
        self.assertEqual(
            [c.source_range for c in collection],
            [
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("04:00:00:00", fps),
                    otio.opentime.from_timecode("00:00:46:16", fps)
                ),
                otio.opentime.TimeRange(
                    otio.opentime.from_timecode("04:00:46:16", fps),
                    otio.opentime.from_timecode("00:00:50:16", fps)
                )
            ]
        )

    def test_ale_roundtrip(self):
        ale_path = EXAMPLE_PATH

        with open(ale_path, 'r') as fi:
            original = fi.read()
            collection = otio.adapters.read_from_string(original, "ale")
            output = otio.adapters.write_to_string(collection, "ale")
            self.maxDiff = None
            self.assertMultiLineEqual(original, output)


if __name__ == '__main__':
    unittest.main()
