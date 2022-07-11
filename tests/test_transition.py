# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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

    def test_setters(self):
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type="SMPTE.Dissolve",
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(trx.transition_type, "SMPTE.Dissolve")
        trx.transition_type = "EdgeWipe"
        self.assertEqual(trx.transition_type, "EdgeWipe")

    def test_parent_range(self):
        timeline = otio.schema.Timeline(
            tracks=[
                otio.schema.Track(
                    name="V1",
                    children=[
                        otio.schema.Clip(
                            name="A",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=1,
                                    rate=30
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                )
                            )
                        ),
                        otio.schema.Transition(
                            in_offset=otio.opentime.RationalTime(
                                value=7,
                                rate=30
                            ),
                            out_offset=otio.opentime.RationalTime(
                                value=10,
                                rate=30
                            ),
                        ),
                        otio.schema.Clip(
                            name="B",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=100,
                                    rate=30
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=50,
                                    rate=30
                                )
                            )
                        ),
                    ]
                )
            ]
        )
        trx = timeline.tracks[0][1]
        time_range = otio.opentime.TimeRange(otio.opentime.RationalTime(43, 30),
                                             otio.opentime.RationalTime(17, 30))

        self.assertEqual(time_range,
                         trx.range_in_parent())

        self.assertEqual(time_range,
                         trx.trimmed_range_in_parent())

        trx = otio.schema.Transition(
            in_offset=otio.opentime.RationalTime(
                value=7,
                rate=30
            ),
            out_offset=otio.opentime.RationalTime(
                value=10,
                rate=30
            ),
        )

        with self.assertRaises(otio.exceptions.NotAChildError):
            trx.range_in_parent()

        with self.assertRaises(otio.exceptions.NotAChildError):
            trx.trimmed_range_in_parent()


if __name__ == '__main__':
    unittest.main()
