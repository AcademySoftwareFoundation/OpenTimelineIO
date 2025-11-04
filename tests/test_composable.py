# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test harness for Composable."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class ComposableTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        seqi = otio.core.Composable(
            name="test",
            metadata={"foo": "bar"}
        )
        self.assertEqual(seqi.name, "test")
        self.assertEqual(seqi.metadata, {'foo': 'bar'})

    def test_serialize(self):
        b = otio.schema.Box2d(
            otio.schema.V2d(0.0, 0.0), otio.schema.V2d(16.0, 9.0))
        seqi = otio.core.Composable(
            name="test",
            metadata={"box": b}
        )
        encoded = otio.adapters.otio_json.write_to_string(seqi)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(seqi, decoded)

    def test_stringify(self):
        seqi = otio.core.Composable()
        self.assertMultiLineEqual(
            str(seqi),
            "Composable("
            "{}, "
            "{}"
            ")".format(
                str(seqi.name),
                str(seqi.metadata),
            )
        )

        self.assertMultiLineEqual(
            repr(seqi),
            "otio.core.Composable("
            "name={}, "
            "metadata={}"
            ")".format(
                repr(seqi.name),
                repr(seqi.metadata),
            )
        )

    def test_metadata(self):
        seqi = otio.core.Composable()
        seqi.metadata["foo"] = "bar"
        encoded = otio.adapters.otio_json.write_to_string(seqi)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(seqi, decoded)
        self.assertEqual(decoded.metadata["foo"], seqi.metadata["foo"])


if __name__ == '__main__':
    unittest.main()
