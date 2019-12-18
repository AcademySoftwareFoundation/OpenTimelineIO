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

"""Unit tests for the JSON format OTIO Serializes to."""

import unittest
import json

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

# local to test dir
from tests import baseline_reader


class TestJsonFormat(unittest.TestCase, otio_test_utils.OTIOAssertions):

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

        self.assertJsonEqual(obj, baseline_data)

    def test_rationaltime(self):
        rt = otio.opentime.RationalTime()
        self.check_against_baseline(rt, "empty_rationaltime")

    def test_timerange(self):
        tr = otio.opentime.TimeRange()
        self.check_against_baseline(tr, "empty_timerange")

    def test_timetransform(self):
        tt = otio.opentime.TimeTransform()
        self.check_against_baseline(tt, "empty_timetransform")

    def test_track(self):
        st = otio.schema.Track(
            name="test_track",
            metadata={
                "comments": "adding some stuff to metadata to try out",
                "a number": 1.0
            }
        )
        self.check_against_baseline(st, "empty_track")

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
        tl.tracks.metadata.update({
            "comments": "adding some stuff to metadata to try out",
            "a number": 1.0
        })
        self.check_against_baseline(tl, "empty_timeline")

    def test_clip(self):
        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.schema.MissingReference()
        )
        self.check_against_baseline(cl, "empty_clip")

    def test_gap(self):
        fl = otio.schema.Gap()
        self.check_against_baseline(fl, "empty_gap")

    def test_missing_reference(self):
        mr = otio.schema.MissingReference()
        self.check_against_baseline(mr, "empty_missingreference")

    def test_external_reference(self):
        mr = otio.schema.ExternalReference(target_url="foo.bar")
        self.check_against_baseline(mr, "empty_external_reference")

    def test_marker(self):
        mr = otio.schema.Marker()
        self.check_against_baseline(mr, "empty_marker")

    def test_transition(self):
        trx = otio.schema.Transition()
        self.check_against_baseline(trx, "empty_transition")

    def test_serializable_collection(self):
        tr = otio.schema.SerializableCollection(
            name="test",
            metadata={"foo": "bar"}
        )
        self.check_against_baseline(tr, "empty_serializable_collection")

    def test_generator_reference(self):
        trx = otio.schema.GeneratorReference()
        self.check_against_baseline(trx, "empty_generator_reference")


if __name__ == '__main__':
    unittest.main()
