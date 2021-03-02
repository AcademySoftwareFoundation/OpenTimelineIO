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

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class BoundsTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        name = "test"
        box = otio.schema.Box2d(
            otio.schema.V2d(1.0, 2.0),
            otio.schema.V2d(3.0, 4.0)
        )

        bounds = otio.schema.Bounds(
            name=name,
            box=box
        )

        self.assertEqual(bounds.name, name)
        self.assertEqual(bounds.box, box)

        encoded = otio.adapters.otio_json.write_to_string(bounds)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(bounds, decoded)

    def test_str(self):
        name = "str_test"

        minV = otio.schema.V2d(1.0, 2.0)
        maxV = otio.schema.V2d(3.0, 4.0)

        box = otio.schema.Box2d(minV, maxV)

        bounds = otio.schema.Bounds(
            name=name,
            box=box
        )

        self.assertMultiLineEqual(
            str(bounds),
            'Bounds("str_test", Box2d(V2d(1.0, 2.0), V2d(3.0, 4.0)), {})'
        )

        self.assertMultiLineEqual(
            repr(bounds),
            'otio.schema.Bounds('
            "name='str_test', "
            'box=otio.schema.Box2d('
            'min=otio.schema.V2d(x=1.0, y=2.0), '
            'max=otio.schema.V2d(x=3.0, y=4.0)'
            '), '
            'metadata={}'
            ')'
        )

    def test_get_set_box(self):
        box = otio.schema.Box2d(
            otio.schema.V2d(1.0, 2.0),
            otio.schema.V2d(3.0, 4.0)
        )

        bounds = otio.schema.Bounds(
            box=box
        )

        self.assertEqual(box, bounds.box)

        box2 = otio.schema.Box2d(
            otio.schema.V2d(5.0, 6.0),
            otio.schema.V2d(7.0, 8.0)
        )

        bounds.box = box2
        self.assertEqual(box2, bounds.box)


if __name__ == '__main__':
    unittest.main()
