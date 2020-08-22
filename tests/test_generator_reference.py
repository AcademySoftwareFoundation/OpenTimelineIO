""" Generator Reference class test harness.  """

import unittest
import os

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
GEN_REF_TEST = os.path.join(SAMPLE_DATA_DIR, "generator_reference_test.otio")


class GeneratorRefTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        self.gen = otio.schema.GeneratorReference(
            name="SMPTEBars",
            generator_kind="SMPTEBars",
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(100, 24),
            ),
            parameters={
                "test_param": 5.0,
            },
            metadata={
                "foo": "bar"
            }
        )

    def test_constructor(self):
        self.assertEqual(self.gen.generator_kind, "SMPTEBars")
        self.assertEqual(self.gen.name, "SMPTEBars")
        self.assertEqual(self.gen.parameters, {"test_param": 5.0})
        self.assertEqual(self.gen.metadata, {"foo": "bar"})
        self.assertEqual(
            self.gen.available_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(100, 24),
            )
        )

    def test_serialize(self):
        encoded = otio.adapters.otio_json.write_to_string(self.gen)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(self.gen, decoded)

    def test_read_file(self):
        self.assertTrue(os.path.exists(GEN_REF_TEST))
        decoded = otio.adapters.otio_json.read_from_file(GEN_REF_TEST)
        self.assertEqual(
            decoded.tracks[0][0].media_reference.generator_kind, "SMPTEBars"
        )

    def test_stringify(self):
        self.assertMultiLineEqual(
            str(self.gen),
            "GeneratorReference("
            '"{}", '
            '"{}", '
            '{}, '
            "{}"
            ")".format(
                str(self.gen.name),
                str(self.gen.generator_kind),
                str(self.gen.parameters),
                str(self.gen.metadata),
            )
        )

        self.assertMultiLineEqual(
            repr(self.gen),
            "otio.schema.GeneratorReference("
            "name={}, "
            "generator_kind={}, "
            "parameters={}, "
            "metadata={}"
            ")".format(
                repr(self.gen.name),
                repr(self.gen.generator_kind),
                repr(self.gen.parameters),
                repr(self.gen.metadata),
            )
        )


if __name__ == '__main__':
    unittest.main()
