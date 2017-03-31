""" Transition class test harness.  """

import unittest

import opentimelineio as otio


class TransitionTests(unittest.TestCase):
    def test_constructor(self):
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type="SMPTE.Dissolve",
            parameters={
                "amount": 0.5
            },
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(trx.transition_type, "SMPTE.Dissolve")
        self.assertEqual(trx.name, "AtoB")
        self.assertEqual(trx.parameters, {"amount": 0.5})
        self.assertEqual(trx.metadata, {"foo": "bar"})

    def test_serialize(self):
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type="SMPTE.Dissolve",
            parameters={
                "amount": 0.5
            },
            metadata={
                "foo": "bar"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(trx)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(trx, decoded)

    def test_stringify(self):
        trx = otio.schema.Transition("SMPTE.Dissolve")
        in_offset = otio.opentime.RationalTime(5, 24)
        out_offset = otio.opentime.RationalTime(1, 24)
        trx.in_offset = in_offset
        trx.out_offset = out_offset
        self.assertMultiLineEqual(
            str(trx),
            "Transition("
            '"{}", '
            '"{}", '
            '{}, '
            '{}, '
            "{}, "
            "{}"
            ")".format(
                str(trx.name),
                str(trx.transition_type),
                str(trx.in_offset),
                str(trx.out_offset),
                str(trx.parameters),
                str(trx.metadata),
            )
        )

        self.assertMultiLineEqual(
            repr(trx),
            "otio.schema.Transition("
            "name={}, "
            "transition_type={}, "
            "in_offset={}, "
            "out_offset={}, "
            "parameters={}, "
            "metadata={}"
            ")".format(
                repr(trx.name),
                repr(trx.transition_type),
                repr(trx.in_offset),
                repr(trx.out_offset),
                repr(trx.parameters),
                repr(trx.metadata),
            )
        )
