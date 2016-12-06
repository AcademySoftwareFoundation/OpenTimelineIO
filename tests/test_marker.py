#!/usr/bin/env python

import unittest

import opentimelineio as otio


class MarkerTest(unittest.TestCase):

    def test_cons(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24)
        )
        m = otio.schema.Marker(
            name="marker_1",
            range=tr,
            metadata={'foo': 'bar'}
        )
        self.assertEqual(m.name, 'marker_1')
        self.assertEqual(m.metadata['foo'], 'bar')
        self.assertEqual(m.range, tr)
        self.assertNotEqual(hash(m), hash(otio.schema.Marker()))

        encoded = otio.adapters.otio_json.write_to_string(m)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(m, decoded)

    def test_equality(self):
        m = otio.schema.Marker()
        bo = otio.core.Item()

        self.assertNotEqual(m, bo)
        self.assertNotEqual(bo, m)


if __name__ == '__main__':
    unittest.main()
