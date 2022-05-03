# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio


class CxxSDKTests(unittest.TestCase):
    def test_cpp_big_ints(self):
        self.assertTrue(otio._otio._testing.test_big_uint())


if __name__ == '__main__':
    unittest.main()
