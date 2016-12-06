#!/usr/bin/env python

"""
Test harness for Media References.
"""

import opentimelineio as otio

import unittest


class MediaReferenceTests(unittest.TestCase):

    def test_cons(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24),
            otio.opentime.RationalTime(10, 24.0)
        )
        mr = otio.media_reference.MissingReference(
            available_range=tr,
            metadata={'show': 'OTIOTheMovie'}
        )

        self.assertEqual(mr.available_range, tr)

        mr = otio.media_reference.MissingReference()
        self.assertIsNone(mr.available_range)

    def test_str_missing(self):
        missing = otio.media_reference.MissingReference()
        self.assertMultiLineEqual(str(missing), "MissingReference()")
        self.assertMultiLineEqual(
            repr(missing),
            "otio.media_reference.MissingReference()"
        )

        encoded = otio.adapters.otio_json.write_to_string(missing)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(missing, decoded)

    def test_filepath(self):
        filepath = otio.media_reference.External("/var/tmp/foo.mov")
        self.assertMultiLineEqual(
            str(filepath),
            'External("/var/tmp/foo.mov")'
        )
        self.assertMultiLineEqual(
            repr(filepath),
            "otio.media_reference.External("
            "target_url='/var/tmp/foo.mov'"
            ")"
        )

        # round trip serialize
        encoded = otio.adapters.otio_json.write_to_string(filepath)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(filepath, decoded)

    def test_equality(self):
        filepath = otio.media_reference.External(target_url="/var/tmp/foo.mov")
        filepath2 = otio.media_reference.External(
            target_url="/var/tmp/foo.mov")
        self.assertEqual(filepath, filepath2)

        bl = otio.media_reference.MissingReference()
        self.assertNotEqual(filepath, bl)

        filepath = otio.media_reference.External(target_url="/var/tmp/foo.mov")
        filepath2 = otio.media_reference.External(
            target_url="/var/tmp/foo2.mov")
        self.assertNotEqual(filepath, filepath2)
        self.assertEqual(filepath == filepath2, False)

        bl = otio.media_reference.MissingReference()
        self.assertNotEqual(filepath, bl)


if __name__ == '__main__':
    unittest.main()
