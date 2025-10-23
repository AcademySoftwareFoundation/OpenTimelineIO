# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import json
import sys
import unittest

import opentimelineio.test_utils as otio_test_utils

import opentimelineio as otio


class V2dTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        v = otio.schema.V2d()

        self.assertEqual(v.x, 0.0)
        self.assertEqual(v.y, 0.0)

        v = otio.schema.V2d(1.0, 2.0)

        self.assertEqual(v.x, 1.0)
        self.assertEqual(v.y, 2.0)

        self.assertEqual(v[0], 1.0)
        self.assertEqual(v[1], 2.0)

    def test_str(self):
        v = otio.schema.V2d(1.0, 2.0)

        self.assertMultiLineEqual(str(v), "V2d(1.0, 2.0)")

        self.assertMultiLineEqual(repr(v), "otio.schema.V2d(x=1.0, y=2.0)")

    def test_equality(self):
        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)

        self.assertFalse(v1 == v2)
        self.assertTrue(v1 != v2)

        v3 = otio.schema.V2d(1.0, 2.0)
        self.assertTrue(v1 == v3)
        self.assertFalse(v1 != v3)

        self.assertTrue(v1.equalWithAbsError(v3, 0.0))
        self.assertTrue(v1.equalWithRelError(v3, 0.0))

    def test_math_ops(self):
        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)

        self.assertEqual(v1 ^ v2, 11.0)
        self.assertEqual(v1.dot(v2), 11.0)

        self.assertEqual(v1 % v2, -2.0)
        self.assertEqual(v1.cross(v2), -2.0)

        self.assertEqual(v1 + v2, otio.schema.V2d(4.0, 6.0))
        self.assertEqual(v1 - v2, otio.schema.V2d(-2.0, -2.0))
        self.assertEqual(v1 * v2, otio.schema.V2d(3.0, 8.0))
        self.assertEqual(v1 / v2, otio.schema.V2d(1.0 / 3.0, 0.5))

        v1 += v2
        self.assertEqual(v1, otio.schema.V2d(4.0, 6.0))

        v1 -= v2
        self.assertEqual(v1, otio.schema.V2d(1.0, 2.0))

        v1 *= v2
        self.assertEqual(v1, otio.schema.V2d(3.0, 8.0))

        v1 /= v2
        self.assertEqual(v1, otio.schema.V2d(1.0, 2.0))

    def test_geometry(self):
        v = otio.schema.V2d(3.0, 4.0)

        self.assertEqual(v.length(), 5.0)
        self.assertEqual(v.length2(), 25.0)

    def test_normalize(self):
        v = otio.schema.V2d(3.0, 4.0)

        self.assertEqual(v.normalized(), otio.schema.V2d(0.6, 0.8))
        self.assertEqual(v.normalizedNonNull(), otio.schema.V2d(0.6, 0.8))

        v2 = v
        v.normalize()
        v2.normalizeNonNull()
        self.assertEqual(v, otio.schema.V2d(0.6, 0.8))
        self.assertEqual(v2, otio.schema.V2d(0.6, 0.8))

        nv = otio.schema.V2d(0.0, 0.0)

        with self.assertRaises((ValueError, RuntimeError)):
            nv.normalizeExc()

        with self.assertRaises((ValueError, RuntimeError)):
            nv.normalizedExc()

    def test_limits(self):
        self.assertEqual(otio.schema.V2d.baseTypeLowest(), -1 * sys.float_info.max)
        self.assertEqual(otio.schema.V2d.baseTypeMax(), sys.float_info.max)
        self.assertEqual(otio.schema.V2d.baseTypeSmallest(), sys.float_info.min)
        self.assertEqual(otio.schema.V2d.baseTypeEpsilon(), sys.float_info.epsilon)

    def test_json_serialization(self):
        serialized = otio.adapters.otio_json.write_to_string(otio.schema.V2d(0.1, 0.2))
        json_v2d = json.loads(serialized)
        self.assertEqual(json_v2d["OTIO_SCHEMA"], "V2d.1")

    def test_serialization_round_trip(self):
        v2d = otio.schema.V2d(0.3, 0.4)
        serialized = otio.adapters.otio_json.write_to_string(v2d)
        deserialized = otio.adapters.otio_json.read_from_string(serialized)
        self.assertEqual(v2d, deserialized)


if __name__ == "__main__":
    unittest.main()
