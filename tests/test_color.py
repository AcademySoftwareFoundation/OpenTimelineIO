# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class ColorTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_convert_to(self):
        white = otio.core.Color.WHITE
        self.assertEqual(white.r, 1.0)
        self.assertEqual(white.g, 1.0)
        self.assertEqual(white.b, 1.0)
        self.assertEqual(white.a, 1.0)
        self.assertEqual(white.to_hex(), "#ffffffff")
        self.assertEqual(white.to_rgba_int_list(8), [255, 255, 255, 255])
        self.assertEqual(white.to_agbr_integer(), 4294967295)
        self.assertEqual(white.to_rgba_float_list(), [1.0, 1.0, 1.0, 1.0])

        black = otio.core.Color.BLACK
        self.assertEqual(black.r, 0.0)
        self.assertEqual(black.g, 0.0)
        self.assertEqual(black.b, 0.0)
        self.assertEqual(black.a, 1.0)
        self.assertEqual(black.to_hex(), "#000000ff")
        self.assertEqual(black.to_rgba_int_list(8), [0, 0, 0, 255])
        self.assertEqual(black.to_agbr_integer(), 4278190080)
        self.assertEqual(black.to_rgba_float_list(), [0.0, 0.0, 0.0, 1.0])

    def test_from_hex(self):
        all_reds = [
            "f00",  # 3 digits
            "f00f",  # 4 digits
            "ff0000",  # 6 digits
            "ff0000ff",  # 8 digits
            "0xff0000",  # prefix
            "#ff0000",  # prefix
        ]
        for red_hex in all_reds + [s.upper() for s in all_reds]:
            red = otio.core.Color.from_hex(red_hex)
            self.assertEqual(red.r, 1.0)
            self.assertEqual(red.g, 0.0)
            self.assertEqual(red.b, 0.0)
            self.assertEqual(red.a, 1.0)

    def test_from_int_list(self):
        colors = (
            [255, 255, 255],
            [0, 0, 0],
            [255, 0, 0, 0],
        )

        for c in colors:
            actual = otio.core.Color.from_int_list(c, 8).to_rgba_int_list(8)
            if len(c) == 4:
                self.assertEqual(c, actual)
            elif len(c) == 3:
                self.assertEqual(c[0], actual[0])
                self.assertEqual(c[1], actual[1])
                self.assertEqual(c[2], actual[2])
                self.assertEqual(255, actual[3])

    def test_from_float_list(self):
        colors = (
            [1.0, 1.0, 1.0],
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
        )

        for c in colors:
            actual = otio.core.Color.from_float_list(c).to_rgba_float_list()
            if len(c) == 4:
                self.assertEqual(c, actual)
            elif len(c) == 3:
                self.assertEqual(c[0], actual[0])
                self.assertEqual(c[1], actual[1])
                self.assertEqual(c[2], actual[2])
                self.assertEqual(1.0, actual[3])

    def test_from_agbr_int(self):
        self.assertEqual(
            otio.core.Color.from_agbr_int(4281740498).to_hex(),
            '#d2362cff'
        )

    def test_repr(self):
        cl = otio.core.Color.ORANGE
        self.assertMultiLineEqual(
            repr(cl),
            'otio.core.Color('
            'name={}, '
            'r={}, '
            'g={}, '
            'b={}, '
            'a={})'.format(
                repr(cl.name),
                repr(cl.r),
                repr(cl.g),
                repr(cl.b),
                repr(cl.a),
            )
        )


if __name__ == '__main__':
    unittest.main()
