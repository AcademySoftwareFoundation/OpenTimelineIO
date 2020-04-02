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

"""Transition class test harness."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class TransitionTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type="SMPTE.Dissolve",
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(trx.transition_type, "SMPTE.Dissolve")
        self.assertEqual(trx.name, "AtoB")
        self.assertEqual(trx.metadata, {"foo": "bar"})

    def test_serialize(self):
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type="SMPTE.Dissolve",
            metadata={
                "foo": "bar"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(trx)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(trx, decoded)

    def test_stringify(self):
        trx = otio.schema.Transition("SMPTE.Dissolve")
        in_offset = otio.opentime.RationalTime(5, 24)
        out_offset = otio.opentime.RationalTime(1, 24)
        trx.in_offset = in_offset
        trx.out_offset = out_offset
        self.assertMultiLineEqual(
            str(trx),
            "Transition("
            '"{}", '
            '"{}", '
            '{}, '
            "{}, "
            "{}"
            ")".format(
                str(trx.name),
                str(trx.transition_type),
                str(trx.in_offset),
                str(trx.out_offset),
                str(trx.metadata),
            )
        )

        self.assertMultiLineEqual(
            repr(trx),
            "otio.schema.Transition("
            "name={}, "
            "transition_type={}, "
            "in_offset={}, "
            "out_offset={}, "
            "metadata={}"
            ")".format(
                repr(trx.name),
                repr(trx.transition_type),
                repr(trx.in_offset),
                repr(trx.out_offset),
                repr(trx.metadata),
            )
        )


if __name__ == '__main__':
    unittest.main()
