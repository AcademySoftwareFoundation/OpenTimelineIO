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

    def test_serialize_to_error(self):
        so = otio.core.SerializeableObject()
        so.data['foo'] = 'bar'
        self.assertRaises(
            otio.exceptions.InvalidSerializeableLabelError,
            lambda: otio.adapters.otio_json.write_to_string(so)
        )

if __name__ == '__main__':
    unittest.main()
