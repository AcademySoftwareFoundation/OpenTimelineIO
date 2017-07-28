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

"""Test harness for Media References."""

import opentimelineio as otio

import unittest


class MediaReferenceTests(unittest.TestCase):

    def test_cons(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24.0)
        )
        mr = otio.media_reference.MissingReference(
            available_range=tr,
            metadata={'show': 'OTIOTheMovie'}
        )

        self.assertEqual(mr.available_range, tr)

        mr = otio.media_reference.MissingReference()
        self.assertIsNone(mr.available_range)

    def test_str_missing(self):
        missing = otio.media_reference.MissingReference()
        self.assertMultiLineEqual(
            str(missing),
            "MissingReference(None, None, {})"
        )
        self.assertMultiLineEqual(
            repr(missing),
            "otio.media_reference.MissingReference("
            "name=None, available_range=None, metadata={}"
            ")"
        )

        encoded = otio.adapters.otio_json.write_to_string(missing)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(missing, decoded)

    def test_filepath(self):
        filepath = otio.media_reference.External("/var/tmp/foo.mov")
        self.assertMultiLineEqual(
            str(filepath),
            'External("/var/tmp/foo.mov")'
        )
        self.assertMultiLineEqual(
            repr(filepath),
            "otio.media_reference.External("
            "target_url='/var/tmp/foo.mov'"
            ")"
        )

        # round trip serialize
        encoded = otio.adapters.otio_json.write_to_string(filepath)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(filepath, decoded)

    def test_equality(self):
        filepath = otio.media_reference.External(target_url="/var/tmp/foo.mov")
        filepath2 = otio.media_reference.External(
            target_url="/var/tmp/foo.mov"
        )
        self.assertEqual(filepath, filepath2)

        bl = otio.media_reference.MissingReference()
        self.assertNotEqual(filepath, bl)

        filepath = otio.media_reference.External(target_url="/var/tmp/foo.mov")
        filepath2 = otio.media_reference.External(
            target_url="/var/tmp/foo2.mov"
        )
        self.assertNotEqual(filepath, filepath2)
        self.assertEqual(filepath == filepath2, False)

        bl = otio.media_reference.MissingReference()
        self.assertNotEqual(filepath, bl)

    def test_is_missing(self):
        mr = otio.media_reference.External(target_url="/var/tmp/foo.mov")
        self.assertFalse(mr.is_missing_reference)

        mr = otio.media_reference.MissingReference()
        self.assertTrue(mr.is_missing_reference)


if __name__ == '__main__':
    unittest.main()
