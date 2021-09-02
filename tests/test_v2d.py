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
import sys

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class V2dTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        v = otio.schema.V2d(1.0, 2.0)

        self.assertEqual(v.x, 1.0)
        self.assertEqual(v.y, 2.0)

        self.assertEqual(v[0], 1.0)
        self.assertEqual(v[1], 2.0)

    def test_str(self):
        v = otio.schema.V2d(1.0, 2.0)

        self.assertMultiLineEqual(
            str(v),
            'V2d(1.0, 2.0)'
        )

        self.assertMultiLineEqual(
            repr(v),
            'otio.schema.V2d(x=1.0, y=2.0)'
        )

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

        with self.assertRaises(ValueError):
            nv.normalizeExc()

        with self.assertRaises(ValueError):
            nv.normalizedExc()

    def test_limits(self):
        self.assertEqual(otio.schema.V2d.baseTypeLowest(), -1 * sys.float_info.max)
        self.assertEqual(otio.schema.V2d.baseTypeMax(), sys.float_info.max)
        self.assertEqual(otio.schema.V2d.baseTypeSmallest(), sys.float_info.min)
        self.assertEqual(otio.schema.V2d.baseTypeEpsilon(), sys.float_info.epsilon)


if __name__ == '__main__':
    unittest.main()
