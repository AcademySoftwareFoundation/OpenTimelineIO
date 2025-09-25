# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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

    def test_unknown_to_dict(self):
        unknown = self.orig.media_reference.metadata["stuff"]
        self.assertTrue(unknown.is_unknown_schema)
        unknown_data = unknown.data
        self.assertIsNotNone(
            unknown_data
        )

        self.assertEqual(
            unknown_data,
            {
                "some_data": 895,
                "howlongami": otio.opentime.RationalTime(rate=30, value=100)
            }
        )
        
        # Mutation of unkown_data should not mutate the unknown object.
        unknown_data["some_data"] = 0
        self.assertEqual(
            unknown.data,
            {
                "some_data": 895,
                "howlongami": otio.opentime.RationalTime(rate=30, value=100)
            }
        )


if __name__ == '__main__':
    unittest.main()
