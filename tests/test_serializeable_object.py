#!/usr/bin/env python

import opentimelineio as otio

import unittest


class OpenTimeTypeSerializerTest(unittest.TestCase):

    def test_serialize_time(self):
        rt = otio.opentime.RationalTime(15, 24)
        encoded = otio.adapters.otio_json.write_to_string(rt)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEquals(rt, decoded)

        rt_dur = otio.opentime.RationalTime(10, 20)
        tr = otio.opentime.TimeRange(rt, rt_dur)
        encoded = otio.adapters.otio_json.write_to_string(tr)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEquals(tr, decoded)

        tt = otio.opentime.TimeTransform(rt, scale=1.5)
        encoded = otio.adapters.otio_json.write_to_string(tt)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEquals(tt, decoded)


class SerializeableObjectTest(unittest.TestCase):

    def test_cons(self):
        so = otio.core.SerializeableObject()
        so.data['foo'] = 'bar'
        self.assertEquals(so.data['foo'], 'bar')

    def test_hash(self):
        so = otio.core.SerializeableObject()
        so.data['foo'] = 'bar'
        so_2 = otio.core.SerializeableObject()
        so_2.data['foo'] = 'bar'
        self.assertEquals(hash(so), hash(so_2))

    def test_update(self):
        so = otio.core.SerializeableObject()
        so.update({"foo": "bar"})
        self.assertEquals(so.data["foo"], "bar")
        so_2 = otio.core.SerializeableObject()
        so_2.data["foo"] = "not bar"
        so.update(so_2)
        self.assertEquals(so.data["foo"], "not bar")

    def test_serialize_to_error(self):
        so = otio.core.SerializeableObject()
        so.data['foo'] = 'bar'
        self.assertRaises(
            otio.exceptions.InvalidSerializeableLabelError,
            lambda: otio.adapters.otio_json.write_to_string(so)
        )

    def test_copy_lib(self):
        so = otio.core.SerializeableObject()
        so.data["metadata"] = {"foo":"bar"}
        
        import copy

        # shallow copy
        so_cp = copy.copy(so)
        so_cp.data["metadata"]["foo"] = "not bar"
        self.assertEquals(so, so_cp)

        so.foo = "bar"
        so_cp = copy.copy(so)
        # copy only copies members of the data dictionary, *not* other attrs.
        self.assertRaises(AttributeError, lambda : so_cp.foo)

        # deep copy
        so_cp = copy.deepcopy(so)
        self.assertEquals(so, so_cp)

        so_cp.data["foo"] = "bar"
        self.assertNotEquals(so, so_cp)

    def test_schema_versioning(self):
        @otio.core.register_type
        class FakeThing(otio.core.SerializeableObject):
            _serializeable_label = "Stuff.1"
            foo_two = otio.core.serializeable_field("foo_2", doc="test")
        ft = FakeThing()

        self.assertEquals(ft.schema_name(), "Stuff")
        self.assertEquals(ft.schema_version(), 1)

        self.assertRaises(
            otio.exceptions.UnsupportedSchemaError,
            lambda: otio.core.instance_from_schema(
                "Stuff",
                "2",
                {"foo": "bar"}
            )
        )

        ft = otio.core.instance_from_schema("Stuff", "1", {"foo": "bar"})
        self.assertEquals(ft.data['foo'], "bar")

        @otio.core.register_type
        class FakeThing(otio.core.SerializeableObject):
            _serializeable_label = "Stuff.4"
            foo_two = otio.core.serializeable_field("foo_2")

        @otio.core.upgrade_function_for(FakeThing, 2)
        def upgrade_one_to_two(data_dict):
            return {"foo_2": data_dict["foo"]}

        @otio.core.upgrade_function_for(FakeThing, 3)
        def upgrade_one_to_two_three(data_dict):
            return {"foo_3": data_dict["foo_2"]}

        ft = otio.core.instance_from_schema("Stuff", "1", {"foo": "bar"})
        self.assertEquals(ft.data['foo_3'], "bar")

        ft = otio.core.instance_from_schema("Stuff", "3", {"foo_2": "bar"})
        self.assertEquals(ft.data['foo_3'], "bar")

        ft = otio.core.instance_from_schema("Stuff", "4", {"foo_3": "bar"})
        self.assertEquals(ft.data['foo_3'], "bar")

if __name__ == '__main__':
    unittest.main()
