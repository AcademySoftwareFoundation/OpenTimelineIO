#!/usr/bin/env python

""" Unit tests for the JSON format OTIO Serializes to.  """

import unittest
import json

import opentimelineio as otio

# local to test dir
import baseline_reader


class TestJsonFormat(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def check_against_baseline(self, obj, testname):
        baseline = baseline_reader.json_baseline(testname)
        self.assertDictEqual(
            baseline_reader.json_from_string(
                otio.adapters.otio_json.write_to_string(obj)
            ),
            baseline
        )
        baseline_data = otio.adapters.otio_json.read_from_string(
            json.dumps(baseline)
        )
        if isinstance(baseline_data, dict):
            raise TypeError("did not deserialize correctly")
        self.assertEqual(obj, baseline_data)

    def test_rationaltime(self):
        rt = otio.opentime.RationalTime()
        self.check_against_baseline(rt, "empty_rationaltime")

    def test_timerange(self):
        tr = otio.opentime.TimeRange()
        self.check_against_baseline(tr, "empty_timerange")

    def test_timetransform(self):
        tt = otio.opentime.TimeTransform()
        self.check_against_baseline(tt, "empty_timetransform")

    def test_sequence(self):
        st = otio.schema.Sequence(
            name="test_track",
            metadata={
                "comments": "adding some stuff to metadata to try out",
                "a number": 1.0
            }
        )
        self.check_against_baseline(st, "empty_sequence")

    def test_stack(self):
        st = otio.schema.Stack(
            name="tracks",
            metadata={
                "comments": "adding some stuff to metadata to try out",
                "a number": 1.0
            }
        )
        self.check_against_baseline(st, "empty_stack")

    def test_timeline(self):
        tl = otio.schema.Timeline(
            name="Example Timeline",
            metadata={
                "comments": "adding some stuff to metadata to try out",
                "a number": 1.0
            }
        )
        tl.tracks.metadata = {
            "comments": "adding some stuff to metadata to try out",
            "a number": 1.0
        }
        self.check_against_baseline(tl, "empty_timeline")

    def test_clip(self):
        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.media_reference.MissingReference()
        )
        self.check_against_baseline(cl, "empty_clip")

    def test_filler(self):
        fl = otio.schema.Filler()
        self.check_against_baseline(fl, "empty_filler")

    def test_missing_reference(self):
        mr = otio.media_reference.MissingReference()
        self.check_against_baseline(mr, "empty_missingreference")

    def test_external_reference(self):
        mr = otio.media_reference.External(target_url="foo.bar")
        self.check_against_baseline(mr, "empty_external_reference")

    def test_marker(self):
        mr = otio.schema.Marker()
        self.check_against_baseline(mr, "empty_marker")


if __name__ == '__main__':
    unittest.main()
