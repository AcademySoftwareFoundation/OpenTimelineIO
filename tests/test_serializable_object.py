#!/usr/bin/env python
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

import opentimelineio as otio

import unittest


class OpenTimeTypeSerializerTest(unittest.TestCase):

    def test_serialize_time(self):
        rt = otio.opentime.RationalTime(15, 24)
        encoded = otio.adapters.otio_json.write_to_string(rt)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(rt, decoded)

        rt_dur = otio.opentime.RationalTime(10, 20)
        tr = otio.opentime.TimeRange(rt, rt_dur)
        encoded = otio.adapters.otio_json.write_to_string(tr)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(tr, decoded)

        tt = otio.opentime.TimeTransform(rt, scale=1.5)
        encoded = otio.adapters.otio_json.write_to_string(tt)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(tt, decoded)


class SerializableObjTest(unittest.TestCase, otio.test_utils.OTIOAssertions):
    def test_cons(self):
        so = otio.core.SerializableObject()
        so.data['foo'] = 'bar'
        self.assertEqual(so.data['foo'], 'bar')

    def test_update(self):
        so = otio.core.SerializableObject()
        so.update({"foo": "bar"})
        self.assertEqual(so.data["foo"], "bar")
        so_2 = otio.core.SerializableObject()
        so_2.data["foo"] = "not bar"
        so.update(so_2)
        self.assertEqual(so.data["foo"], "not bar")

    def test_serialize_to_error(self):
        so = otio.core.SerializableObject()
        so.data['foo'] = 'bar'
        with self.assertRaises(otio.exceptions.InvalidSerializableLabelError):
            otio.adapters.otio_json.write_to_string(so)

    def test_copy_lib(self):
        so = otio.core.SerializableObject()
        so.data["metadata"] = {"foo": "bar"}

        import copy

        # shallow copy
        so_cp = copy.copy(so)
        so_cp.data["metadata"]["foo"] = "not bar"
        self.assertEqual(so.data, so_cp.data)

        so.foo = "bar"
        so_cp = copy.copy(so)
        # copy only copies members of the data dictionary, *not* other attrs.
        with self.assertRaises(AttributeError):
            so_cp.foo

        # deep copy
        so_cp = copy.deepcopy(so)
        self.assertIsOTIOEquivalentTo(so, so_cp)

        so_cp.data["foo"] = "bar"
        self.assertNotEqual(so, so_cp)

    def test_copy_subclass(self):
        @otio.core.register_type
        class Foo(otio.core.SerializableObject):
            _serializable_label = "Foo.1"

        foo = Foo()
        foo.data["metadata"] = {"foo": "bar"}

        import copy

        foo_copy = copy.copy(foo)

        self.assertEqual(Foo, type(foo_copy))

    def test_schema_versioning(self):
        @otio.core.register_type
        class FakeThing(otio.core.SerializableObject):
            _serializable_label = "Stuff.1"
            foo_two = otio.core.serializable_field("foo_2", doc="test")
        ft = FakeThing()

        self.assertEqual(ft.schema_name(), "Stuff")
        self.assertEqual(ft.schema_version(), 1)

        with self.assertRaises(otio.exceptions.UnsupportedSchemaError):
            otio.core.instance_from_schema(
                "Stuff",
                "2",
                {"foo": "bar"}
            )

        ft = otio.core.instance_from_schema("Stuff", "1", {"foo": "bar"})
        self.assertEqual(ft.data['foo'], "bar")

        @otio.core.register_type
        class FakeThing(otio.core.SerializableObject):
            _serializable_label = "Stuff.4"
            foo_two = otio.core.serializable_field("foo_2")

        @otio.core.upgrade_function_for(FakeThing, 2)
        def upgrade_one_to_two(data_dict):
            return {"foo_2": data_dict["foo"]}

        @otio.core.upgrade_function_for(FakeThing, 3)
        def upgrade_one_to_two_three(data_dict):
            return {"foo_3": data_dict["foo_2"]}

        ft = otio.core.instance_from_schema("Stuff", "1", {"foo": "bar"})
        self.assertEqual(ft.data['foo_3'], "bar")

        ft = otio.core.instance_from_schema("Stuff", "3", {"foo_2": "bar"})
        self.assertEqual(ft.data['foo_3'], "bar")

        ft = otio.core.instance_from_schema("Stuff", "4", {"foo_3": "bar"})
        self.assertEqual(ft.data['foo_3'], "bar")

    def test_equality(self):
        o1 = otio.core.SerializableObject()
        o2 = otio.core.SerializableObject()
        self.assertTrue(o1 is not o2)
        self.assertTrue(o1.is_equivalent_to(o2))
        self.assertIsOTIOEquivalentTo(o1, o2)

    def test_truthiness(self):
        o = otio.core.SerializableObject()
        self.assertTrue(o)


if __name__ == '__main__':
    unittest.main()
