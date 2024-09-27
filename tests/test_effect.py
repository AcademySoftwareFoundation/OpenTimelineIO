# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class EffectTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"},
            enabled=False
        )

        self.assertEqual(ef.enabled, False)

        encoded = otio.adapters.otio_json.write_to_string(ef)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(ef, decoded)
        self.assertEqual(decoded.name, "blur it")
        self.assertEqual(decoded.effect_name, "blur")
        self.assertEqual(decoded.metadata['foo'], 'bar')
        self.assertEqual(decoded.enabled, False)

    def test_eq(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"}
        )
        ef2 = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"}
        )
        self.assertIsOTIOEquivalentTo(ef, ef2)

    def test_str(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"},
            enabled=False
        )
        self.assertMultiLineEqual(
            str(ef),
            "Effect({}, {}, {}, {})".format(
                str(ef.name),
                str(ef.effect_name),
                str(ef.metadata),
                str(ef.enabled)
            )
        )
        self.assertMultiLineEqual(
            repr(ef),
            "otio.schema.Effect("
            "name={}, "
            "effect_name={}, "
            "metadata={}, "
            "enabled={}"
            ")".format(
                repr(ef.name),
                repr(ef.effect_name),
                repr(ef.metadata),
                repr(ef.enabled)
            )
        )

    def test_setters(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"}
        )
        self.assertEqual(ef.effect_name, "blur")
        ef.effect_name = "flop"
        self.assertEqual(ef.effect_name, "flop")
        self.assertEqual(ef.enabled, True)


class TestLinearTimeWarp(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        ef = otio.schema.LinearTimeWarp("Foo", 2.5, {'foo': 'bar'})
        self.assertEqual(ef.effect_name, "LinearTimeWarp")
        self.assertEqual(ef.name, "Foo")
        self.assertEqual(ef.time_scalar, 2.5)
        self.assertEqual(ef.metadata, {"foo": "bar"})
        self.assertEqual(ef.enabled, True)

    def test_serialize(self):
        ef = otio.schema.LinearTimeWarp("Foo", 2.5, {'foo': 'bar'})
        encoded = otio.adapters.otio_json.write_to_string(ef)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(ef, decoded)

    def test_setters(self):
        ef = otio.schema.LinearTimeWarp("Foo", 2.5, {'foo': 'bar'})
        self.assertEqual(ef.time_scalar, 2.5)
        ef.time_scalar = 5.0
        self.assertEqual(ef.time_scalar, 5.0)


class TestFreezeFrame(unittest.TestCase):
    def test_cons(self):
        ef = otio.schema.FreezeFrame("Foo", {'foo': 'bar'})
        self.assertEqual(ef.effect_name, "FreezeFrame")
        self.assertEqual(ef.name, "Foo")
        self.assertEqual(ef.time_scalar, 0)
        self.assertEqual(ef.metadata, {"foo": "bar"})
        self.assertEqual(ef.enabled, True)


if __name__ == '__main__':
    unittest.main()
