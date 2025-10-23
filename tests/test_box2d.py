# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class Box2dTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        box = otio.schema.Box2d()

        self.assertEqual(box.min, otio.schema.V2d(0.0, 0.0))
        self.assertEqual(box.max, otio.schema.V2d(0.0, 0.0))

        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)
        box = otio.schema.Box2d(v1, v2)

        self.assertEqual(box.min, v1)
        self.assertEqual(box.max, v2)

    def test_str(self):
        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)
        box = otio.schema.Box2d(v1, v2)

        self.assertMultiLineEqual(
            str(box),
            'Box2d(V2d(1.0, 2.0), V2d(3.0, 4.0))'
        )

        self.assertMultiLineEqual(
            repr(box),
            'otio.schema.Box2d('
            'min=otio.schema.V2d(x=1.0, y=2.0), '
            'max=otio.schema.V2d(x=3.0, y=4.0)'
            ')'
        )

    def test_center(self):
        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)
        box1 = otio.schema.Box2d(v1, v2)

        self.assertEqual(box1.center(),
                         otio.schema.V2d(2.0, 3.0)
                         )

    def test_extend(self):
        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)
        box1 = otio.schema.Box2d(v1, v2)

        box1.extendBy(otio.schema.V2d(5.0, 5.0))
        self.assertEqual(box1,
                         otio.schema.Box2d(
                             otio.schema.V2d(1.0, 2.0),
                             otio.schema.V2d(5.0, 5.0)
                         )
                         )

        v3 = otio.schema.V2d(2.0, 3.0)
        v4 = otio.schema.V2d(6.0, 6.0)
        box2 = otio.schema.Box2d(v3, v4)

        box1.extendBy(box2)
        self.assertEqual(box1,
                         otio.schema.Box2d(
                             otio.schema.V2d(1.0, 2.0),
                             otio.schema.V2d(6.0, 6.0)
                         )
                         )

    def test_intersects(self):
        v1 = otio.schema.V2d(1.0, 2.0)
        v2 = otio.schema.V2d(3.0, 4.0)
        box1 = otio.schema.Box2d(v1, v2)

        self.assertTrue(box1.intersects(otio.schema.V2d(2.0, 3.0)))

        self.assertFalse(box1.intersects(otio.schema.V2d(0.0, 3.0)))

        v3 = otio.schema.V2d(1.1, 1.9)
        v4 = otio.schema.V2d(3.1, 3.9)
        box2 = otio.schema.Box2d(v3, v4)

        self.assertTrue(box1.intersects(box2))

        v5 = otio.schema.V2d(3.1, 4.1)
        v6 = otio.schema.V2d(4.1, 5.1)
        box3 = otio.schema.Box2d(v5, v6)

        self.assertFalse(box1.intersects(box3))


if __name__ == '__main__':
    unittest.main()
