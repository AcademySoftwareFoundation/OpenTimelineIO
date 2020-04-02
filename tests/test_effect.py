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


class EffectTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        ef = otio.schema.Effect(
            name="blur it",
            effect_name="blur",
            metadata={"foo": "bar"}
        )
        encoded = otio.adapters.otio_json.write_to_string(ef)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(ef, decoded)
        self.assertEqual(decoded.name, "blur it")
        self.assertEqual(decoded.effect_name, "blur")
        self.assertEqual(decoded.metadata['foo'], 'bar')

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


class TestLinearTimeWarp(unittest.TestCase):
    def test_cons(self):
        ef = otio.schema.LinearTimeWarp("Foo", 2.5, {'foo': 'bar'})
        self.assertEqual(ef.effect_name, "LinearTimeWarp")
        self.assertEqual(ef.name, "Foo")
        self.assertEqual(ef.time_scalar, 2.5)
        self.assertEqual(ef.metadata, {"foo": "bar"})


class TestFreezeFrame(unittest.TestCase):
    def test_cons(self):
        ef = otio.schema.FreezeFrame("Foo", {'foo': 'bar'})
        self.assertEqual(ef.effect_name, "FreezeFrame")
        self.assertEqual(ef.name, "Foo")
        self.assertEqual(ef.time_scalar, 0)
        self.assertEqual(ef.metadata, {"foo": "bar"})


if __name__ == '__main__':
    unittest.main()
