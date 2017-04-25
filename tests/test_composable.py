""" Test harness for Composable. """

import unittest

import opentimelineio as otio


class ComposableTests(unittest.TestCase):
    def test_constructor(self):
        seqi = otio.core.Composable(
            name="test",
            metadata={"foo": "bar"}
        )
        self.assertEqual(seqi.name, "test")
        self.assertEqual(seqi.metadata, {'foo': 'bar'})

    def test_serialize(self):
        seqi = otio.core.Composable(
            name="test",
            metadata={"foo": "bar"}
        )
        encoded = otio.adapters.otio_json.write_to_string(seqi)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(seqi, decoded)

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
        self.assertEqual(seqi, decoded)
        self.assertEqual(decoded.metadata["foo"], seqi.metadata["foo"])

    def test_set_parent(self):
        seqi = otio.core.Composable()
        seqi_2 = otio.core.Composable()

        # set seqi from none
        seqi_2._set_parent(seqi)
        self.assertEqual(seqi, seqi_2._parent)

        # change seqi
        seqi_3 = otio.core.Composable()
        seqi_2._set_parent(seqi_3)
        self.assertEqual(seqi_3, seqi_2._parent)
