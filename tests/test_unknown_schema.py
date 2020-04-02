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

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

has_undefined_schema = """
{
    "OTIO_SCHEMA": "Clip.1",
    "effects": [],
    "markers": [],
    "media_reference": {
        "OTIO_SCHEMA": "ExternalReference.1",
        "available_range": {
            "OTIO_SCHEMA": "TimeRange.1",
            "duration": {
                "OTIO_SCHEMA": "RationalTime.1",
                "rate": 24,
                "value": 140
            },
            "start_time": {
                "OTIO_SCHEMA": "RationalTime.1",
                "rate": 24,
                "value": 91
            }
        },
        "metadata": {
            "stuff": {
                "OTIO_SCHEMA": "MyOwnDangSchema.3",
                "some_data": 895,
                "howlongami": {
                     "OTIO_SCHEMA": "RationalTime.1",
                      "rate": 30,
                      "value": 100
                   }
            }
        },
        "name": null,
        "target_url": "/usr/tmp/some_media.mov"
    },
    "metadata": {},
    "name": null,
    "source_range": null
}
"""


class UnknownSchemaTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        # make an OTIO data structure containing an undefined schema object
        self.orig = otio.adapters.otio_json.read_from_string(has_undefined_schema)

    def test_serialize_deserialize(self):
        serialized = otio.adapters.otio_json.write_to_string(self.orig)
        test_otio = otio.adapters.otio_json.read_from_string(serialized)

        self.assertIsOTIOEquivalentTo(self.orig, test_otio)

    def test_is_unknown_schema(self):
        self.assertFalse(self.orig.is_unknown_schema)
        unknown = self.orig.media_reference.metadata["stuff"]
        self.assertTrue(unknown.is_unknown_schema)


if __name__ == '__main__':
    unittest.main()
