#
# Copyright Contributors to the OpenTimelineIO project
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
import opentimelineio.test_utils as otio_test_utils

import unittest


class MediaReferenceTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24.0)
        )
        mr = otio.schema.MissingReference(
            available_range=tr,
            metadata={'show': 'OTIOTheMovie'}
        )

        self.assertEqual(mr.available_range, tr)

        mr = otio.schema.MissingReference()
        self.assertIsNone(mr.available_range)

    def test_str_missing(self):
        missing = otio.schema.MissingReference()
        self.assertMultiLineEqual(
            str(missing),
            "MissingReference(\'\', None, {})"
        )
        self.assertMultiLineEqual(
            repr(missing),
            "otio.schema.MissingReference("
            "name='', available_range=None, metadata={}"
            ")"
        )

        encoded = otio.adapters.otio_json.write_to_string(missing)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(missing, decoded)

    def test_filepath(self):
        filepath = otio.schema.ExternalReference("/var/tmp/foo.mov")
        self.assertMultiLineEqual(
            str(filepath),
            'ExternalReference("/var/tmp/foo.mov")'
        )
        self.assertMultiLineEqual(
            repr(filepath),
            "otio.schema.ExternalReference("
            "target_url='/var/tmp/foo.mov'"
            ")"
        )

        # round trip serialize
        encoded = otio.adapters.otio_json.write_to_string(filepath)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(filepath, decoded)

    def test_equality(self):
        filepath = otio.schema.ExternalReference(target_url="/var/tmp/foo.mov")
        filepath2 = otio.schema.ExternalReference(
            target_url="/var/tmp/foo.mov"
        )
        self.assertIsOTIOEquivalentTo(filepath, filepath2)

        bl = otio.schema.MissingReference()
        self.assertNotEqual(filepath, bl)

        filepath2 = otio.schema.ExternalReference(
            target_url="/var/tmp/foo2.mov"
        )
        self.assertNotEqual(filepath, filepath2)
        self.assertEqual(filepath == filepath2, False)

    def test_is_missing(self):
        mr = otio.schema.ExternalReference(target_url="/var/tmp/foo.mov")
        self.assertFalse(mr.is_missing_reference)

        mr = otio.schema.MissingReference()
        self.assertTrue(mr.is_missing_reference)


if __name__ == '__main__':
    unittest.main()
