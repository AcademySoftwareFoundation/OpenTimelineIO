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
XGES_NESTED_PATH = os.path.join(SAMPLE_DATA_DIR, "xges_nested_example.xges")

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
GST_SECOND = 1000000000


def rat_tm(val):
    return otio.opentime.RationalTime(val * 25.0, 25.0)


def tm_range(start, dur):
    return otio.opentime.TimeRange(
        otio.opentime.RationalTime(start * 25.0, 25.0),
        otio.opentime.RationalTime(dur * 25.0, 25.0))


def make_media_ref(uri="file:///example", start=0, duration=1, name=""):
    ref = otio.schema.ExternalReference()
    ref.name = name
    ref.target_url = uri
    ref.available_range = tm_range(start, duration)
    return ref


def make_clip(uri="file:///example", start=0, duration=1, name=""):
    ref = make_media_ref(uri, start, duration)
    clip = otio.schema.Clip()
    clip.name = name
    clip.media_reference = ref
    return clip


def get_xges_clips(
        xges_xml, start=None, duration=None, inpoint=None,
        type_name=None, track_types=None, clip_id=None):
    path = "./project/timeline/layer/clip"
    if start is not None:
        path += "[@start='%i']" % (start * GST_SECOND)
    if duration is not None:
        path += "[@duration='%i']" % (duration * GST_SECOND)
    if inpoint is not None:
        path += "[@inpoint='%i']" % (inpoint * GST_SECOND)
    if type_name is not None:
        path += "[@type-name='%s']" % (type_name)
    if track_types is not None:
        path += "[@track-types='%i']" % (track_types)
    if clip_id is not None:
        path += "[@id='%i']" % (clip_id)
    found = xges_xml.findall(path)
    if found is None:
        return []
    return found


def get_xges_clip(
        xges_xml, start=None, duration=None, inpoint=None,
        type_name=None, track_types=None, clip_id=None):
    els = get_xges_clips(
        xges_xml, start, duration, inpoint, type_name, track_types,
        clip_id)
    if len(els) == 1:
        return els[0]
    return None


def get_xges_asset(xges_xml, asset_id, extract_type):
    return xges_xml.find(
        "./project/ressources/asset[@id='%s']"
        "[@extractable-type-name='%s']" % (asset_id, extract_type))


class AdaptersXGESTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_read(self):
        timeline = otio.adapters.read_from_file(XGES_EXAMPLE_PATH)
        self.assertIsInstance(timeline.tracks, otio.schema.Stack)
        self.assertEqual(len(timeline.tracks), 6)

        for track in timeline.tracks:
            self.assertIsInstance(track, otio.schema.Track)

        video_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Video
        ]
        audio_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Audio
        ]

        def check_types(tracks, expect_types):
            for track, otio_types in zip(tracks, expect_types):
                self.assertEqual(len(track), len(otio_types))
                for composable, otio_type in zip(track, otio_types):
                    self.assertIsInstance(composable, otio_type)
                    if isinstance(composable, otio.schema.Clip):
                        ref = composable.media_reference
                        self.assertIsInstance(
                            ref, otio.schema.ExternalReference)

        self.assertEqual(len(video_tracks), 3)
        # Note that the otio tracks are orderer such that the higher
        # priority clips are later in the list
        check_types(
            video_tracks, [
                [
                    otio.schema.Gap, otio.schema.Clip,
                    otio.schema.Transition, otio.schema.Clip],
                [
                    otio.schema.Gap, otio.schema.Clip,
                    otio.schema.Gap, otio.schema.Clip],
                [
                    otio.schema.Gap, otio.schema.Clip]])

        self.assertEqual(len(audio_tracks), 3)
        check_types(
            audio_tracks, [
                [otio.schema.Clip],
                [otio.schema.Gap, otio.schema.Clip],
                [otio.schema.Gap, otio.schema.Clip]])

        xges_xml = ElementTree.fromstring(
            otio.adapters.write_to_string(timeline, "xges"))

        self.assertIsNotNone(
            xges_xml.find(
                "./project/timeline/track[@track-type='4']"))
        self.assertIsNotNone(
            xges_xml.find(
                "./project/timeline/track[@track-type='2']"))
        layers = xges_xml.findall("./project/timeline/layer")
        self.assertIsNotNone(layers)
        layers.sort(key=lambda lay: lay.get("priority"))
        self.assertEqual(len(layers), 5)
        for layer, expect_num, expect_track_types in zip(
                layers, [1, 1, 2, 3, 1], ["6", "2", "4", "4", "2"]):
            clips = layer.findall("./clip")
            self.assertIsNotNone(clips)
            self.assertEqual(len(clips), expect_num)
            for clip in clips:
                self.assertEqual(
                    clip.get("track-types"), expect_track_types)
                if clip.get("type-name") == "GESUriClip":
                    self.assertIsNotNone(
                        xges_xml.find(
                            "./project/ressources/asset[@id='%s']"
                            "[@extractable-type-name='GESUriClip']"
                            % clip.get("asset-id")))

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
        timeline = otio.adapters.read_from_file(XGES_TIMING_PATH)
        self.assertIsInstance(timeline.tracks, otio.schema.Stack)
        self.assertIsNone(timeline.tracks.source_range)
        self.assertEqual(len(timeline.tracks), 1)
        track = timeline.tracks[0]
        self.assertEqual(track.kind, otio.schema.TrackKind.Audio)
        self.assertIsInstance(track, otio.schema.Track)
        self.assertIsNone(track.source_range)

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

        clips = get_xges_clips(xges_xml)
        self.assertEqual(len(clips), 7)

        self.assertIsNotNone(
            get_xges_clip(xges_xml, 1, 2, 15, "GESUriClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 2, 1, 0, "GESTransitionClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 2, 4, 25, "GESUriClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 4, 2, 0, "GESTransitionClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 4, 3, 0, "GESUriClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 9, 1, 0, "GESUriClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 10, 1, 0, "GESUriClip", 2))

    def test_nested_projects_and_stacks(self):
        timeline = otio.adapters.read_from_file(XGES_NESTED_PATH)
        self.assertIsInstance(timeline.tracks, otio.schema.Stack)
        self.assertEqual(len(timeline.tracks), 1)
        track = timeline.tracks[0]
        self.assertIsInstance(track, otio.schema.Track)
        self.assertEqual(track.kind, otio.schema.TrackKind.Video)
        self.assertEqual(len(track), 2)
        gap = track[0]
        self.assertIsInstance(gap, otio.schema.Gap)
        self.assertEqual(gap.source_range.duration, rat_tm(7))
        stack = track[1]
        self.assertIsInstance(stack, otio.schema.Stack)
        self.assertEqual(stack.source_range, tm_range(1, 2))
        self.assertEqual(len(stack), 1)
        track = stack[0]
        self.assertIsInstance(track, otio.schema.Track)
        self.assertEqual(track.kind, otio.schema.TrackKind.Video)
        self.assertEqual(len(track), 2)
        gap = track[0]
        self.assertIsInstance(gap, otio.schema.Gap)
        self.assertEqual(gap.source_range.duration, rat_tm(5))
        clip = track[1]
        self.assertIsInstance(clip, otio.schema.Clip)
        self.assertEqual(clip.source_range, tm_range(3, 4))
        self.assertIsInstance(
            clip.media_reference, otio.schema.ExternalReference)

        self._xges_has_nested_clip(timeline, 7, 2, 1, 5, 4, 3)

    def _xges_has_nested_clip(
            self, timeline, top_start, top_duration, top_inpoint,
            orig_start, orig_duration, orig_inpoint):
        xges_xml = ElementTree.fromstring(
            otio.adapters.write_to_string(timeline, "xges"))
        top_clip = get_xges_clip(
            xges_xml, top_start, top_duration, top_inpoint,
            "GESUriClip", 4)
        self.assertIsNotNone(top_clip)
        asset_id = top_clip.get("asset-id")
        self.assertIsNotNone(asset_id)
        self.assertIsNotNone(
            get_xges_asset(xges_xml, asset_id, "GESUriClip"))
        ges_asset = get_xges_asset(xges_xml, asset_id, "GESTimeline")
        self.assertIsNotNone(ges_asset)
        xges_xml = ges_asset.find("./ges")
        self.assertIsNotNone(xges_xml)
        orig_clip = get_xges_clip(
            xges_xml, orig_start, orig_duration, orig_inpoint,
            "GESUriClip", 4)
        self.assertIsNotNone(orig_clip)
        self.assertIsNotNone(
            get_xges_asset(
                xges_xml, orig_clip.get("asset-id"), "GESUriClip"))

    def test_source_range_stack(self):
        timeline = otio.schema.Timeline()
        track = otio.schema.Track()
        track.kind = otio.schema.TrackKind.Video
        timeline.tracks.append(track)
        track.append(make_clip(start=2, duration=5))
        timeline.tracks.source_range = tm_range(1, 3)
        self._xges_has_nested_clip(timeline, 0, 3, 1, 0, 5, 2)

    def test_source_range_track(self):
        timeline = otio.schema.Timeline()
        track = otio.schema.Track()
        track.kind = otio.schema.TrackKind.Video
        timeline.tracks.append(track)
        track.append(make_clip(start=2, duration=5))
        track.source_range = tm_range(1, 3)
        self._xges_has_nested_clip(timeline, 0, 3, 1, 0, 5, 2)

    def test_double_track(self):
        timeline = otio.schema.Timeline()
        track1 = otio.schema.Track()
        track1.kind = otio.schema.TrackKind.Video
        timeline.tracks.append(track1)
        track2 = otio.schema.Track()
        track2.kind = otio.schema.TrackKind.Video
        track1.append(make_clip(start=4, duration=9))
        track1.append(track2)
        track2.append(make_clip(start=2, duration=5))
        self._xges_has_nested_clip(timeline, 9, 5, 0, 0, 5, 2)

    def test_double_stack(self):
        timeline = otio.schema.Timeline()
        stack = otio.schema.Stack()
        stack.source_range = tm_range(1, 3)
        track = otio.schema.Track()
        track.kind = otio.schema.TrackKind.Video
        track.append(make_clip(start=2, duration=5))
        stack.append(track)
        track = otio.schema.Track()
        track.kind = otio.schema.TrackKind.Video
        track.append(make_clip())
        timeline.tracks.append(track)
        timeline.tracks.append(stack)
        self._xges_has_nested_clip(timeline, 0, 3, 1, 0, 5, 2)

    def test_track_merge(self):
        timeline = otio.schema.Timeline()
        for kind in [
                otio.schema.TrackKind.Audio,
                otio.schema.TrackKind.Video]:
            track = otio.schema.Track()
            track.kind = kind
            track.metadata["example-non-xges"] = str(kind)
            track.metadata["XGES"] = {
                "data": SCHEMA.GstStructure(
                    "name, key1=(string)hello, key2=(int)9;")}
            track.append(make_clip(start=2, duration=5))
            timeline.tracks.append(track)
        xges_xml = ElementTree.fromstring(
            otio.adapters.write_to_string(timeline, "xges"))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 0, 5, 2, "GESUriClip", 6))

        # make tracks have different XGES metadata
        for track in timeline.tracks:
            track.metadata["XGES"]["data"].set(
                "key1", "string", str(track.kind))
        xges_xml = ElementTree.fromstring(
            otio.adapters.write_to_string(timeline, "xges"))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 0, 5, 2, "GESUriClip", 2))
        self.assertIsNotNone(
            get_xges_clip(xges_xml, 0, 5, 2, "GESUriClip", 4))

    def test_timeline_is_unchanged(self):
        timeline = otio.schema.Timeline(name="example")
        timeline.tracks.source_range = tm_range(4, 5)
        track = otio.schema.Track("Track", source_range=tm_range(2, 3))
        track.metadata["key"] = 5
        track.append(make_clip())
        timeline.tracks.append(track)

        before = timeline.deepcopy()
        otio.adapters.write_to_string(timeline, "xges")
        self.assertTrue(before.is_equivalent_to(timeline))
        self.assertTrue(timeline.is_equivalent_to(before))

    def test_XgesTrack(self):
        vid = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Video)
        self.assertEqual(vid.track_type, 4)
        aud = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Audio)
        self.assertEqual(aud.track_type, 2)

    def test_XgesTrack_equality(self):
        vid1 = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Video)
        vid2 = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Video)
        aud = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(otio.schema.TrackKind.Audio)
        self.assertEqual(vid1, vid2)
        self.assertNotEqual(vid1, aud)

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

    def test_GstStructure_from_other(self):
        struct = SCHEMA.GstStructure(
            "name, prop1=(string)test, prop2=(int)4;")
        self.assertEqual(struct.name, "name")
        struct = SCHEMA.GstStructure("new-name", struct)
        self.assertEqual(struct.name, "new-name")
        struct = SCHEMA.GstStructure(
            "new-name", "name, prop1=(string)test, prop2=(int)4;")
        self.assertEqual(struct.name, "new-name")

    def test_GstStructure_equality(self):
        struct1 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop2=(int)4;")
        struct2 = SCHEMA.GstStructure(
            "name, prop2=(int)4, prop1=(string)4;")
        struct3 = SCHEMA.GstStructure(
            "name-alt, prop1=(string)4, prop2=(int)4;")
        struct4 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop3=(int)4;")
        struct5 = SCHEMA.GstStructure(
            "name, prop1=(int)4, prop2=(int)4;")
        struct6 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop2=(int)5;")
        struct7 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop2=(int)4, prop3=(bool)true;")
        struct8 = SCHEMA.GstStructure(
            "name, prop1=(string)4;")
        self.assertEqual(struct1, struct2)
        self.assertNotEqual(struct1, struct3)
        self.assertNotEqual(struct1, struct4)
        self.assertNotEqual(struct1, struct5)
        self.assertNotEqual(struct1, struct6)
        self.assertNotEqual(struct1, struct7)
        self.assertNotEqual(struct1, struct8)

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
