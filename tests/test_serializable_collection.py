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


class SerializableColTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        self.maxDiff = None
        self.children = [
            otio.schema.Clip(name="testClip"),
            otio.schema.MissingReference()
        ]
        self.md = {'foo': 'bar'}
        self.sc = otio.schema.SerializableCollection(
            name="test",
            children=self.children,
            metadata=self.md
        )

    def test_ctor(self):
        self.assertEqual(self.sc.name, "test")
        self.assertEqual(self.sc[:], self.children)
        self.assertEqual(self.sc.metadata, self.md)

    def test_iterable(self):
        self.assertEqual(self.sc[0], self.children[0])
        self.assertEqual([i for i in self.sc], self.children)
        self.assertEqual(len(self.sc), 2)

        # test recursive iteration
        sc = otio.schema.SerializableCollection(
            name="parent",
            children=[self.sc]
        )

        self.assertEqual(len(list(sc.each_clip())), 1)

        # test deleting an item
        tmp = self.sc[0]
        del self.sc[0]
        self.assertEqual(len(self.sc), 1)
        self.sc[0] = tmp
        self.assertEqual(self.sc[0], tmp)

    def test_serialize(self):
        encoded = otio.adapters.otio_json.write_to_string(self.sc)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(self.sc, decoded)

    def test_str(self):
        self.assertMultiLineEqual(
            str(self.sc),
            "SerializableCollection(" +
            str(self.sc.name) + ", " +
            str(list(self.sc)) + ", " +
            str(self.sc.metadata) +
            ")"
        )

    def test_repr(self):
        self.assertMultiLineEqual(
            repr(self.sc),
            "otio.schema.SerializableCollection(" +
            "name=" + repr(self.sc.name) + ", " +
            "children=" + repr(list(self.sc)) + ", " +
            "metadata=" + repr(self.sc.metadata) +
            ")"
        )


if __name__ == '__main__':
    unittest.main()
