#
# Copyright 2017 Pixar Animation Studios
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

"""Test harness for Composable."""

import unittest

import opentimelineio as otio


class ComposableTests(unittest.TestCase, otio.test_utils.OTIOAssertions):
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
