#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import opentimelineio as otio
import opentimelineio._otio
import opentimelineio.test_utils as otio_test_utils

import unittest
import json


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


class SerializableObjTest(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        so = otio.core.SerializableObjectWithMetadata()
        so.metadata['foo'] = 'bar'
        self.assertEqual(so.metadata['foo'], 'bar')

    def test_cons2(self):
        v = opentimelineio._otio.AnyVector()
        v.append(1)
        v.append('inside any vector')

        d = opentimelineio._otio.AnyDictionary()
        d['key_1'] = 1234
        d['key_2'] = {'asdasdasd': 5.6}
        so = otio.core.SerializableObjectWithMetadata(
            metadata={
                'string': 'myvalue',
                'int': -999999999999,
                'list': [1, 2.5, 'asd'],
                'dict': {'map1': [345]},
                'AnyVector': v,
                'AnyDictionary': d
            }
        )
        so.metadata['foo'] = 'bar'
        self.assertEqual(so.metadata['foo'], 'bar')
        self.assertEqual(so.metadata['string'], 'myvalue')
        self.assertEqual(so.metadata['int'], -999999999999)
        self.assertIsInstance(so.metadata['list'], opentimelineio._otio.AnyVector)
        self.assertEqual(list(so.metadata['list']), [1, 2.5, 'asd'])  # AnyVector. Is this right?
        self.assertIsInstance(so.metadata['dict'], opentimelineio._otio.AnyDictionary)
        # self.assertDictEqual(so.metadata['dict'], {'map1': [345]})
        self.assertIsInstance(so.metadata['AnyVector'], opentimelineio._otio.AnyVector)
        self.assertEqual(list(so.metadata['AnyVector']), [1, 'inside any vector'])
        self.assertIsInstance(so.metadata['AnyDictionary'], opentimelineio._otio.AnyDictionary)
        self.assertEqual(dict(so.metadata['AnyDictionary']), {'key_1': 1234, 'key_2': {'asdasdasd': 5.6}})

    def test_update(self):
        so = otio.core.SerializableObjectWithMetadata()
        so.metadata.update({"foo": "bar"})
        self.assertEqual(so.metadata["foo"], "bar")
        so_2 = otio.core.SerializableObjectWithMetadata()
        so_2.metadata["foo"] = "not bar"
        so.metadata.update(so_2.metadata)
        self.assertEqual(so.metadata["foo"], "not bar")

    def test_copy_lib(self):
        so = otio.core.SerializableObjectWithMetadata()
        so.metadata["meta_data"] = {"foo": "bar"}

        import copy

        # shallow copy is an error
        with self.assertRaises(ValueError):
            so_cp = copy.copy(so)

        # deep copy
        so_cp = copy.deepcopy(so)
        self.assertIsNotNone(so_cp)
        self.assertIsOTIOEquivalentTo(so, so_cp)

        so_cp.metadata["foo"] = "bar"
        self.assertNotEqual(so, so_cp)

    def test_copy_subclass(self):
        @otio.core.register_type
        class Foo(otio.core.SerializableObjectWithMetadata):
            _serializable_label = "Foof.1"

        foo = Foo()
        foo.metadata["meta_data"] = {"foo": "bar"}

        import copy

        with self.assertRaises(ValueError):
            foo_copy = copy.copy(foo)

        foo_copy = copy.deepcopy(foo)

        self.assertEqual(Foo, type(foo_copy))

    def test_equality(self):
        o1 = otio.core.SerializableObject()
        o2 = otio.core.SerializableObject()
        self.assertTrue(o1 is not o2)
        self.assertTrue(o1.is_equivalent_to(o2))
        self.assertIsOTIOEquivalentTo(o1, o2)

    def test_equivalence_symmetry(self):
        def test_equivalence(A, B, msg):
            self.assertTrue(A.is_equivalent_to(B), f"{msg}: A ~= B")
            self.assertTrue(B.is_equivalent_to(A), f"{msg}: B ~= A")

        def test_difference(A, B, msg):
            self.assertFalse(A.is_equivalent_to(B), f"{msg}: A ~= B")
            self.assertFalse(B.is_equivalent_to(A), f"{msg}: B ~= A")

        A = otio.core.Composable()
        B = otio.core.Composable()
        test_equivalence(A, B, "blank objects")

        A.metadata["key"] = {"a": 0}
        test_difference(A, B, "A has different metadata")

        B.metadata["key"] = {"a": 0}
        test_equivalence(A, B, "add metadata to B")

        A.metadata["key"]["sub-key"] = 1
        test_difference(A, B, "Add dict within A with specific metadata")

    def test_truthiness(self):
        o = otio.core.SerializableObject()
        self.assertTrue(o)

    def test_instancing_without_instancing_support(self):
        o = otio.core.SerializableObjectWithMetadata()
        c = otio.core.SerializableObjectWithMetadata()
        o.metadata["child1"] = c
        o.metadata["child2"] = c
        self.assertTrue(o.metadata["child1"] is o.metadata["child2"])

        oCopy = o.clone()
        # Note: If we ever enable INSTANCING_SUPPORT in the C++ code,
        # then this will (and should) fail
        self.assertTrue(oCopy.metadata["child1"] is not oCopy.metadata["child2"])

    def test_cycle_detection(self):
        o = otio.core.SerializableObjectWithMetadata()
        o.metadata["myself"] = o

        # Note: If we ever enable INSTANCING_SUPPORT in the C++ code,
        # then modify the code below to be:
        #   oCopy = o.clone()
        #   self.assertTrue(oCopy is oCopy.metadata["myself"])
        with self.assertRaises(ValueError):
            o.clone()


class VersioningTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_schema_definition(self):
        """define a schema and instantiate it from python"""

        # ensure that the type hasn't already been registered
        self.assertNotIn("Stuff", otio.core.type_version_map())

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
                2,
                {"foo": "bar"}
            )

        version_map = otio.core.type_version_map()
        self.assertEqual(version_map["Stuff"], 1)

        ft = otio.core.instance_from_schema("Stuff", 1, {"foo": "bar"})
        self.assertEqual(ft._dynamic_fields['foo'], "bar")

    @unittest.skip("@TODO: disabled pending discussion")
    def test_double_register_schema(self):
        @otio.core.register_type
        class DoubleReg(otio.core.SerializableObject):
            _serializable_label = "Stuff.1"
            foo_two = otio.core.serializable_field("foo_2", doc="test")
        _ = DoubleReg()  # quiet pyflakes

        # not allowed to register a type twice
        with self.assertRaises(ValueError):
            @otio.core.register_type
            class DoubleReg(otio.core.SerializableObject):
                _serializable_label = "Stuff.1"

    def test_upgrade_versions(self):
        """Test adding an upgrade functions for a type"""

        @otio.core.register_type
        class FakeThing(otio.core.SerializableObject):
            _serializable_label = "NewStuff.4"
            foo_two = otio.core.serializable_field("foo_2")

        @otio.core.upgrade_function_for(FakeThing, 2)
        def upgrade_one_to_two(_data_dict):
            return {"foo_2": _data_dict["foo"]}

        @otio.core.upgrade_function_for(FakeThing, 3)
        def upgrade_one_to_two_three(_data_dict):
            return {"foo_3": _data_dict["foo_2"]}

        # @TODO: further discussion required
        # not allowed to overwrite registered functions
        # with self.assertRaises(ValueError):
        #     @otio.core.upgrade_function_for(FakeThing, 3)
        #     def upgrade_one_to_two_three_again(_data_dict):
        #         raise RuntimeError("shouldn't see this ever")

        ft = otio.core.instance_from_schema("NewStuff", 1, {"foo": "bar"})
        self.assertEqual(ft._dynamic_fields['foo_3'], "bar")

        ft = otio.core.instance_from_schema("NewStuff", 3, {"foo_2": "bar"})
        self.assertEqual(ft._dynamic_fields['foo_3'], "bar")

        ft = otio.core.instance_from_schema("NewStuff", 4, {"foo_3": "bar"})
        self.assertEqual(ft._dynamic_fields['foo_3'], "bar")

    def test_upgrade_rename(self):
        """test that upgrading system handles schema renames correctly"""

        @otio.core.register_type
        class FakeThingToRename(otio.core.SerializableObject):
            _serializable_label = "ThingToRename.2"
            my_field = otio.core.serializable_field("my_field", doc="example")

        thing = otio.core.type_version_map()
        self.assertTrue(thing)

    def test_downgrade_version(self):
        """ test a python defined downgrade function"""

        @otio.core.register_type
        class FakeThing(otio.core.SerializableObject):
            _serializable_label = "FakeThingToDowngrade.2"
            foo_two = otio.core.serializable_field("foo_2")

        @otio.core.downgrade_function_from(FakeThing, 2)
        def downgrade_2_to_1(_data_dict):
            return {"foo": _data_dict["foo_2"]}

        # @TODO: further discussion required
        # # not allowed to overwrite registered functions
        # with self.assertRaises(ValueError):
        #     @otio.core.downgrade_function_from(FakeThing, 2)
        #     def downgrade_2_to_1_again(_data_dict):
        #         raise RuntimeError("shouldn't see this ever")

        f = FakeThing()
        f.foo_two = "a thing here"

        downgrade_target = {"FakeThingToDowngrade": 1}

        result = json.loads(
            otio.adapters.otio_json.write_to_string(f, downgrade_target)
        )

        self.assertDictEqual(
            result,
            {
                "OTIO_SCHEMA": "FakeThingToDowngrade.1",
                "foo": "a thing here",
            }
        )


if __name__ == '__main__':
    unittest.main()
