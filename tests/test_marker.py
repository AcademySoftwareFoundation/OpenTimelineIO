# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class MarkerTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24)
        )
        m = otio.schema.Marker(
            name="marker_1",
            marked_range=tr,
            color=otio.schema.MarkerColor.GREEN,
            metadata={'foo': 'bar'}
        )
        self.assertEqual(m.name, 'marker_1')
        self.assertEqual(m.metadata['foo'], 'bar')
        self.assertEqual(m.marked_range, tr)
        self.assertEqual(m.color, otio.schema.MarkerColor.GREEN)

        encoded = otio.adapters.otio_json.write_to_string(m)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(m, decoded)

    def test_upgrade(self):
        src = """
        {
            "OTIO_SCHEMA" : "Marker.1",
            "metadata" : {},
            "name" : null,
            "range" : {
                "OTIO_SCHEMA" : "TimeRange.1",
                "start_time" : {
                    "OTIO_SCHEMA" : "RationalTime.1",
                    "rate" : 5,
                    "value" : 0
                },
                "duration" : {
                    "OTIO_SCHEMA" : "RationalTime.1",
                    "rate" : 5,
                    "value" : 0
                }
            }

        }
        """
        marker = otio.adapters.read_from_string(src, "otio_json")
        self.assertEqual(
            marker.marked_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 5),
                otio.opentime.RationalTime(0, 5),
            )
        )

    def test_equality(self):
        m = otio.schema.Marker()
        bo = otio.core.Item()

        self.assertNotEqual(m, bo)
        self.assertNotEqual(bo, m)

    def test_repr(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24)
        )
        m = otio.schema.Marker(
            name="marker_1",
            marked_range=tr,
            color=otio.schema.MarkerColor.GREEN,
            metadata={'foo': 'bar'}
        )

        expected = (
            "otio.schema.Marker(name='marker_1', "
            "marked_range={}, metadata={})".format(
                repr(tr), repr(m.metadata)
            )
        )

        self.assertEqual(repr(m), expected)

    def test_comment(self):
        src = """
        {
            "OTIO_SCHEMA" : "Marker.1",
            "metadata" : {},
            "name" : null,
            "comment": "foo bar",
            "range" : {
                "OTIO_SCHEMA" : "TimeRange.1",
                "start_time" : {
                    "OTIO_SCHEMA" : "RationalTime.1",
                    "rate" : 5,
                    "value" : 0
                },
                "duration" : {
                    "OTIO_SCHEMA" : "RationalTime.1",
                    "rate" : 5,
                    "value" : 0
                }
            }

        }
        """
        marker = otio.adapters.read_from_string(src, "otio_json")
        self.assertEqual(marker.comment, "foo bar")

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24)
        )
        m = otio.schema.Marker(
            name="marker_1",
            marked_range=tr,
            metadata={'foo': 'bar'},
            comment="foo bar2")
        self.assertEqual(m.comment, "foo bar2")

        encoded = otio.adapters.otio_json.write_to_string(m)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(decoded.comment, "foo bar2")

    def test_str(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24)
        )
        m = otio.schema.Marker(
            name="marker_1",
            marked_range=tr,
            color=otio.schema.MarkerColor.GREEN,
            metadata={'foo': 'bar'}
        )

        expected = 'Marker(marker_1, {}, {})'.format(
            str(tr), str(m.metadata)
        )

        self.assertEqual(str(m), expected)


if __name__ == '__main__':
    unittest.main()
