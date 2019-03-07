#!/usr/bin/env python
#
# Copyright 2019 Pixar Animation Studios
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

import opentimelineio as otio


class TestCoordinateSystemReferences(unittest.TestCase):
    def test_equality(self):
        test_obj = otio.schema.Timeline()
        global_space = test_obj.global_space()
        global_space2 = test_obj.global_space()

        self.assertEqual(global_space, global_space2)

        self.assertNotEqual(global_space, test_obj.internal_space())

        # because the target_obj is different, the references should not be equal
        other_tl = otio.schema.Timeline()
        self.assertNotEqual(
            test_obj.global_space(),
            other_tl.global_space()
        )

    def test_immutable(self):
        tl = otio.schema.Timeline()
        other_tl = otio.schema.Timeline()

        gs = tl.global_space()
        with self.assertRaises(AttributeError):
            gs.source_object = other_tl

        with self.assertRaises(AttributeError):
            gs.space = 123


if __name__ == '__main__':
    unittest.main()
