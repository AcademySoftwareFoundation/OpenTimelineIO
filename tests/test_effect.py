import unittest

import opentimelineio as otio


class EffectTest(unittest.TestCase):

    def test_cons(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"}
        )
        encoded = otio.adapters.otio_json.write_to_string(ef)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEquals(ef, decoded)
        self.assertEquals(decoded.name, "blur it")
        self.assertEquals(decoded.effect_name, "blur")
        self.assertEquals(decoded.metadata['foo'], 'bar')

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
        self.assertEquals(ef, ef2)

    def test_str(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"}
        )
        self.assertMultiLineEqual(
            str(ef),
            "Effect({}, {}, {})".format(
                str(ef.name),
                str(ef.effect_name),
                str(ef.metadata)
            )
        )
        self.assertMultiLineEqual(
            repr(ef),
            "otio.schema.Effect("
            "name={}, "
            "effect_name={}, "
            "metadata={}"
            ")".format(
                repr(ef.name),
                repr(ef.effect_name),
                repr(ef.metadata),
            )
        )
