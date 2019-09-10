#
# Copyright (C) 2019 Igalia S.L
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

import os
import tempfile
import unittest
from fractions import Fraction
from xml.etree import ElementTree

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
XGES_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "xges_example.xges")
XGES_TIMING_PATH = os.path.join(SAMPLE_DATA_DIR, "xges_timing_example.xges")

SCHEMA = otio.schema.schemadef.module_from_name("xges")
# TODO: remove once python2 has ended:
# (problem is that python2 needs a source code encoding
# definition to include utf8 text!!!)
if str is bytes:
    UTF8_NAME = 'Ri"\',;=)(+9@{\xcf\x93\xe7\xb7\xb6\xe2\x98\xba'\
        '\xef\xb8\x8f  l\xd1\xa6\xf1\xbd\x9a\xbb\xf1\xa6\x84\x83  \\'
else:
    UTF8_NAME = str(
        b'Ri"\',;=)(+9@{\xcf\x93\xe7\xb7\xb6\xe2\x98\xba\xef\xb8'
        b'\x8f  l\xd1\xa6\xf1\xbd\x9a\xbb\xf1\xa6\x84\x83  \\',
        encoding="utf8")


def rat_tm(val):
    return otio.opentime.RationalTime(val * 25.0, 25.0)


def tm_range(start, dur):
    return otio.opentime.TimeRange(
        otio.opentime.RationalTime(start * 25.0, 25.0),
        otio.opentime.RationalTime(dur * 25.0, 25.0))


class AdaptersXGESTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_read(self):
        timeline = otio.adapters.read_from_file(XGES_EXAMPLE_PATH)[0]
        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 6)

        video_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Video
        ]
        audio_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Audio
        ]

        self.assertEqual(len(video_tracks), 3)
        self.assertEqual(len(audio_tracks), 3)

    def test_timing(self):
        # example input layer is of the form:
        #       [------]
        #           [---------------]
        #                   [-----------]       [--][--]
        #
        #   0   1   2   3   4   5   6   7   8   9   10  11
        #                   time in seconds
        #
        # where [----] are clips. The first clip has an inpoint of
        # 15 seconds, and the second has an inpoint of 25 seconds. The
        # rest have an inpoint of 0
        timeline = otio.adapters.read_from_file(XGES_TIMING_PATH)[0]
        self.assertIsNotNone(timeline)
        track = timeline.tracks[0]

        self.assertEqual(len(track), 9)
        self.assertIsInstance(track[0], otio.schema.Gap)
        self.assertIsInstance(track[1], otio.schema.Clip)
        self.assertIsInstance(track[2], otio.schema.Transition)
        self.assertIsInstance(track[3], otio.schema.Clip)
        self.assertIsInstance(track[4], otio.schema.Transition)
        self.assertIsInstance(track[5], otio.schema.Clip)
        self.assertIsInstance(track[6], otio.schema.Gap)
        self.assertIsInstance(track[7], otio.schema.Clip)
        # should be no gap or transition between these last two clips,
        # since the latter starts exactly when the former ends
        self.assertIsInstance(track[8], otio.schema.Clip)

        self.assertEqual(
            track[0].range_in_parent(), tm_range(0, 1))
        # expect the clip length to be shortened by half a second, since
        # the following transition lasts one second
        self.assertEqual(
            track[1].range_in_parent(), tm_range(1, 1.5))
        # expect the media inpoint to remain the same, since there is no
        # preceding transition
        self.assertEqual(
            track[1].source_range.start_time, rat_tm(15))
        self.assertEqual(
            track[2].in_offset + track[2].out_offset, rat_tm(1))
        # expect the start to be delayed by half a second due to the
        # previous transition and shortened by another second by the
        # following transition, which lasts two seconds
        self.assertEqual(
            track[3].range_in_parent(), tm_range(2.5, 2.5))
        # expect the inpoint to be delayed by half a second due to the
        # previous transition
        self.assertEqual(
            track[3].source_range.start_time, rat_tm(25.5))
        self.assertEqual(
            track[4].in_offset + track[4].out_offset, rat_tm(2))
        self.assertEqual(
            track[5].range_in_parent(), tm_range(5, 2))
        self.assertEqual(
            track[6].range_in_parent(), tm_range(7, 2))
        self.assertEqual(
            track[7].range_in_parent(), tm_range(9, 1))
        self.assertEqual(
            track[8].range_in_parent(), tm_range(10, 1))

        xges_xml = ElementTree.fromstring(
            otio.adapters.write_to_string(timeline, "xges"))

        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESUriClip'][@start='1000000000']"
            "[@duration='2000000000'][@inpoint='15000000000']"))
        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESTransitionClip'][@start='2000000000']"
            "[@duration='1000000000']"))
        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESUriClip'][@start='2000000000']"
            "[@duration='4000000000'][@inpoint='25000000000']"))
        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESTransitionClip'][@start='4000000000']"
            "[@duration='2000000000']"))
        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESUriClip'][@start='4000000000']"
            "[@duration='3000000000']"))
        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESUriClip'][@start='9000000000']"
            "[@duration='1000000000']"))
        self.assertIsNotNone(xges_xml.find(
            ".//clip[@type-name='GESUriClip'][@start='10000000000']"
            "[@duration='1000000000']"))

    def test_XgesTrack(self):
        vid = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Video)
        self.assertEqual(vid.track_type, 4)
        aud = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Audio)
        self.assertEqual(aud.track_type, 2)

    def test_serialize_string(self):
        serialize = SCHEMA.GstStructure.serialize_string(UTF8_NAME)
        deserialize = SCHEMA.GstStructure.deserialize_string(serialize)
        self.assertEqual(deserialize, UTF8_NAME)

    def test_GstStructure_parsing(self):
        struct = SCHEMA.GstStructure(
            " properties  , String-1 = ( string ) test , "
            "String-2=(string)\"test\", String-3= (  string) {}  , "
            "Int  =(int) -5  , Uint =(uint) 5 , Float-1=(float)0.5, "
            "Float-2= (float  ) 2, Boolean-1 =(boolean  ) true, "
            "Boolean-2=(boolean)No, Boolean-3=( boolean) 0  ,   "
            "Fraction=(fraction) 2/5 ; hidden!!!".format(
                SCHEMA.GstStructure.serialize_string(UTF8_NAME))
        )
        self.assertEqual(struct.name, "properties")
        self.assertEqual(struct["String-1"], "test")
        self.assertEqual(struct["String-2"], "test")
        self.assertEqual(struct["String-3"], UTF8_NAME)
        self.assertEqual(struct["Int"], -5)
        self.assertEqual(struct["Uint"], 5)
        self.assertEqual(struct["Float-1"], 0.5)
        self.assertEqual(struct["Float-2"], 2.0)
        self.assertEqual(struct["Boolean-1"], True)
        self.assertEqual(struct["Boolean-2"], False)
        self.assertEqual(struct["Boolean-3"], False)
        self.assertEqual(struct["Fraction"], "2/5")

    def test_GstStructure_dictionary_def(self):
        struct = SCHEMA.GstStructure(
            "properties", {
                "String-1": ("string", "test"),
                "String-2": ("string", "test space"),
                "Int": ("int", -5),
                "Uint": ("uint", 5),
                "Float": ("float", 2.0),
                "Boolean": ("boolean", True),
                "Fraction": ("fraction", "2/5")
            }
        )
        self.assertEqual(struct.name, "properties")
        write = str(struct)
        self.assertIn("String-1=(string)test", write)
        self.assertIn("String-2=(string)\"test\\ space\"", write)
        self.assertIn("Int=(int)-5", write)
        self.assertIn("Uint=(uint)5", write)
        self.assertIn("Float=(float)2.0", write)
        self.assertIn("Boolean=(boolean)true", write)
        self.assertIn("Fraction=(fraction)2/5", write)

    def test_GstStructure_editing_string(self):
        struct = SCHEMA.GstStructure('properties, name=(string)before;')
        self.assertEqual(struct["name"], "before")
        struct.set("name", "string", "after")
        self.assertEqual(struct["name"], "after")
        self.assertEqual(str(struct), 'properties, name=(string)after;')

    def test_GstStructure_empty_string(self):
        struct = SCHEMA.GstStructure('properties, name=(string)"";')
        self.assertEqual(struct["name"], "")

    def test_GstStructure_NULL_string(self):
        struct = SCHEMA.GstStructure('properties, name=(string)NULL;')
        self.assertEqual(struct["name"], None)
        struct = SCHEMA.GstStructure("properties;")
        struct.set("name", "string", None)
        self.assertEqual(str(struct), 'properties, name=(string)NULL;')
        struct = SCHEMA.GstStructure('properties, name=(string)\"NULL\";')
        self.assertEqual(struct["name"], "NULL")
        self.assertEqual(str(struct), 'properties, name=(string)\"NULL\";')

    def test_GstStructure_fraction(self):
        struct = SCHEMA.GstStructure('properties, framerate=(fraction)2/5;')
        self.assertEqual(struct["framerate"], "2/5")
        struct.set("framerate", "fraction", Fraction("3/5"))
        self.assertEqual(struct["framerate"], "3/5")
        struct.set("framerate", "fraction", "4/5")
        self.assertEqual(struct["framerate"], "4/5")

    def SKIP_test_roundtrip_disk2mem2disk(self):
        self.maxDiff = None
        timeline = otio.adapters.read_from_file(XGES_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".xges", text=True)[1]

        otio.adapters.write_to_file(timeline, tmp_path)
        result = otio.adapters.read_from_file(tmp_path)

        original_json = otio.adapters.write_to_string(timeline, 'otio_json')
        output_json = otio.adapters.write_to_string(result, 'otio_json')
        self.assertMultiLineEqual(original_json, output_json)

        self.assertIsOTIOEquivalentTo(timeline, result)

        # But the xml text on disk is not identical because otio has a subset
        # of features to xges and we drop all the nle specific preferences.
        with open(XGES_EXAMPLE_PATH, "r") as original_file:
            with open(tmp_path, "r") as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())


if __name__ == '__main__':
    unittest.main()
