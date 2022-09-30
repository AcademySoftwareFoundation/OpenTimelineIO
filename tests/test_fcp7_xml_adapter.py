# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test final cut pro xml."""

# python
import json
import os
import tempfile
import unittest
from xml.etree import cElementTree

from opentimelineio import (
    adapters,
    opentime,
    schema,
    test_utils,
)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
FCP7_XML_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "premiere_example.xml")
SIMPLE_XML_PATH = os.path.join(SAMPLE_DATA_DIR, "sample_just_track.xml")
EMPTY_ELEMENT_XML_PATH = os.path.join(SAMPLE_DATA_DIR, "empty_name_tags.xml")
HIERO_XML_PATH = os.path.join(SAMPLE_DATA_DIR, "hiero_xml_export.xml")
FILTER_XML_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR, "premiere_example_filter.xml"
)
FILTER_JSON_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR, "premiere_example_filter.json"
)
GENERATOR_XML_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR, "premiere_generators.xml"
)


class TestFcp7XmlUtilities(unittest.TestCase, test_utils.OTIOAssertions):
    adapter = adapters.from_name('fcp_xml').module()

    def test_xml_tree_to_dict(self):
        self.maxDiff = None

        with open(FILTER_JSON_EXAMPLE_PATH) as f:
            ref_dict = json.load(f)

        tree = cElementTree.parse(FILTER_XML_EXAMPLE_PATH)
        filter_element = tree.getroot()
        xml_dict = self.adapter._xml_tree_to_dict(filter_element)

        self.assertEqual(xml_dict, ref_dict)

        out_xml = self.adapter._dict_to_xml_tree(xml_dict, "filter")
        out_xml_string = self.adapter._make_pretty_string(out_xml)

        with open(FILTER_XML_EXAMPLE_PATH) as f:
            orig_xml_string = f.read()

        self.assertEqual(out_xml_string.strip(), orig_xml_string.strip())

        # validate empty tag handling
        empty_element = cElementTree.fromstring(
            "<top><empty/></top>"
        )
        empty_element_dict = self.adapter._xml_tree_to_dict(empty_element)
        self.assertIsNone(empty_element_dict["empty"])

        empty_xml = self.adapter._dict_to_xml_tree(empty_element_dict, "top")
        self.assertIsNone(empty_xml.find("empty").text)

        roundtrip_dict = self.adapter._xml_tree_to_dict(empty_xml)
        self.assertEqual(empty_element_dict, roundtrip_dict)

    def test_bool_value(self):
        truthy_element = cElementTree.fromstring("<ntsc>TRUE</ntsc>")
        self.assertTrue(self.adapter._bool_value(truthy_element))

        falsy_element = cElementTree.fromstring("<ntsc>FALSE</ntsc>")
        self.assertFalse(self.adapter._bool_value(falsy_element))

    def test_backreference_for_id(self):
        item1 = schema.Clip(name="clip1")
        item1_prime = schema.Clip(name="clip1")
        item2 = schema.Clip(name="clip2")

        br_map = {}
        item1_id, item1_is_new = self.adapter._backreference_for_item(
            item1, "clipitem", br_map
        )
        self.assertEqual(item1_id, "clipitem-1")
        self.assertTrue(item1_is_new)

        item2_id, item2_is_new = self.adapter._backreference_for_item(
            item2, "clipitem", br_map
        )
        self.assertEqual(item2_id, "clipitem-2")
        self.assertTrue(item2_is_new)

        (
            item1_prime_id, item1_prime_is_new
        ) = self.adapter._backreference_for_item(
            item1_prime, "clipitem", br_map
        )
        self.assertEqual(item1_prime_id, "clipitem-1")
        self.assertFalse(item1_prime_is_new)

    def test_backreference_for_id_preserved(self):
        item1 = schema.Clip(
            name="clip23",
            metadata={"fcp_xml": {"@id": "clipitem-23"}},
        )
        item2 = schema.Clip(name="clip2")
        conflicting_item = schema.Clip(
            name="conflicting_clip",
            metadata={"fcp_xml": {"@id": "clipitem-1"}},
        )

        # prepopulate the backref map with some ids
        br_map = {
            "clipitem": {
                "bogus_hash": 1, "bogus_hash_2": 2, "bogus_hash_3": 3
            }
        }

        # Make sure the id is preserved
        item1_id, item1_is_new = self.adapter._backreference_for_item(
            item1, "clipitem", br_map
        )
        self.assertEqual(item1_id, "clipitem-23")
        self.assertTrue(item1_is_new)

        # Make sure the next item continues to fill in
        item2_id, item2_is_new = self.adapter._backreference_for_item(
            item2, "clipitem", br_map
        )
        self.assertEqual(item2_id, "clipitem-4")
        self.assertTrue(item2_is_new)

        # Make sure confilcting clips don't stomp existing ones
        item3_id, item3_is_new = self.adapter._backreference_for_item(
            conflicting_item, "clipitem", br_map
        )
        self.assertEqual(item3_id, "clipitem-5")
        self.assertTrue(item3_is_new)

    def test_name_from_element(self):
        sequence_element = cElementTree.fromstring(
            """
            <sequence>
                <name>My Sequence</name>
            </sequence>
            """
        )
        name = self.adapter._name_from_element(sequence_element)
        self.assertEqual(name, "My Sequence")

        empty_element = cElementTree.fromstring("<sequence></sequence>")
        empty_name = self.adapter._name_from_element(empty_element)
        self.assertEqual(empty_name, "")

        empty_name_element = cElementTree.fromstring(
            "<sequence><name></name></sequence>"
        )
        empty_name_2 = self.adapter._name_from_element(empty_name_element)
        self.assertEqual(empty_name_2, "")

    def test_rate_for_element_ntsc_conversion_23976(self):
        rate_element = cElementTree.fromstring(
            """
            <clipitem>
                <rate>
                    <timebase>24</timebase>
                    <ntsc>TRUE</ntsc>
                </rate>
            </clipitem>
            """
        )
        rate = self.adapter._rate_from_context(
            self.adapter._Context(rate_element)
        )

        self.assertEqual(rate, (24000 / 1001.0))

    def test_rate_for_element_ntsc_conversion_24(self):
        rate_element = cElementTree.fromstring(
            """
            <clipitem>
                <rate>
                    <timebase>24</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
            </clipitem>
            """
        )
        rate = self.adapter._rate_from_context(
            self.adapter._Context(rate_element)
        )

        self.assertEqual(rate, 24)

    def test_rate_for_element_ntsc_conversion_2997(self):
        rate_element = cElementTree.fromstring(
            """
            <clipitem>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>TRUE</ntsc>
                </rate>
            </clipitem>
            """
        )
        rate = self.adapter._rate_from_context(
            self.adapter._Context(rate_element)
        )

        self.assertEqual(rate, (30000 / 1001.0))

    def test_rate_for_element_ntsc_conversion_30(self):
        rate_element = cElementTree.fromstring(
            """
            <clipitem>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
            </clipitem>
            """
        )
        rate = self.adapter._rate_from_context(
            self.adapter._Context(rate_element)
        )

        self.assertEqual(rate, 30)

    def test_rate_for_element_no_ntsc(self):
        rate_element = cElementTree.fromstring(
            """
            <clipitem>
                <rate>
                    <timebase>30</timebase>
                </rate>
            </clipitem>
            """
        )
        rate = self.adapter._rate_from_context(
            self.adapter._Context(rate_element)
        )

        self.assertEqual(rate, 30)

    def test_rate_from_context(self):
        sequence_elem = cElementTree.fromstring(
            """
            <sequence>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>TRUE</ntsc>
                </rate>
            </sequence>
            """
        )

        # Fetch rate from one level of context
        sequence_context = self.adapter._Context(sequence_elem)
        sequence_rate = self.adapter._rate_from_context(sequence_context)
        self.assertEqual(sequence_rate, (30000 / 1001.0))

        track_elem = cElementTree.fromstring(
            """
            <track>
              <rate>
                <timebase>24</timebase>
                <ntsc>TRUE</ntsc>
              </rate>
            </track>
            """
        )

        # make sure pushing a context with a new rate overrides the old rate
        track_context = sequence_context.context_pushing_element(track_elem)
        track_noinherit_rate = self.adapter._rate_from_context(track_context)
        self.assertEqual(track_noinherit_rate, (24000 / 1001.0))

        clip_norate_elem = cElementTree.fromstring(
            """
            <clipitem>
            <name>Just soeme clip</name>
            </clipitem>
            """
        )

        # Make sure pushing a context element with no rate inherits the next
        # level up
        clip_context = track_context.context_pushing_element(clip_norate_elem)
        clip_inherit_rate = self.adapter._rate_from_context(clip_context)
        self.assertEqual(clip_inherit_rate, (24000 / 1001.0))

    def test_time_from_timecode_element(self):
        tc_element = cElementTree.fromstring(
            """
            <timecode>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
                <string>01:00:00:00</string>
                <frame>108000</frame>
                <displayformat>NDF</displayformat>
            </timecode>
            """
        )
        time = self.adapter._time_from_timecode_element(tc_element)

        self.assertEqual(time, opentime.RationalTime(108000, 30))

    def test_time_from_timecode_element_drop_frame(self):
        tc_element = cElementTree.fromstring(
            """
            <timecode>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>TRUE</ntsc>
                </rate>
                <string>10:03:00;05</string>
                <frame>1084319</frame>
                <displayformat>DF</displayformat>
            </timecode>
            """
        )
        time = self.adapter._time_from_timecode_element(tc_element)

        self.assertEqual(
            time, opentime.RationalTime(1084319, (30000 / 1001.0))
        )

    def test_time_from_timecode_element_ntsc_non_drop_frame(self):
        tc_element = cElementTree.fromstring(
            """
            <timecode>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>TRUE</ntsc>
                </rate>
                <string>00:59:56:12</string>
                <displayformat>NDF</displayformat>
            </timecode>
            """
        )

        time = self.adapter._time_from_timecode_element(tc_element)
        self.assertEqual(
            time, opentime.RationalTime(107892, (30000 / 1001.0))
        )

    def test_time_from_timecode_element_implicit_ntsc(self):
        clipitem_element = cElementTree.fromstring(
            """
            <clipitem>
              <duration>767</duration>
              <rate>
                <ntsc>TRUE</ntsc>
                <timebase>24</timebase>
              </rate>
              <in>447</in>
              <out>477</out>
              <start>264</start>
              <end>294</end>
              <file>
                <rate>
                  <timebase>24</timebase>
                  <ntsc>TRUE</ntsc>
                </rate>
                <duration>767</duration>
                <timecode>
                  <rate>
                    <timebase>24</timebase>
                  </rate>
                  <string>14:11:44:09</string>
                  <frame>1226505</frame>
                  <displayformat>NDF</displayformat>
                  <source>source</source>
                </timecode>
              </file>
            </clipitem>
            """
        )
        context = self.adapter._Context(clipitem_element)
        timecode_element = clipitem_element.find("./file/timecode")
        time = self.adapter._time_from_timecode_element(
            timecode_element, context
        )
        self.assertEqual(time, opentime.RationalTime(1226505, 24000.0 / 1001))

    def test_track_kind_from_element(self):
        video_element = cElementTree.fromstring("<video/>")
        video_kind = self.adapter._track_kind_from_element(video_element)
        self.assertEqual(video_kind, schema.TrackKind.Video)

        audio_element = cElementTree.fromstring("<audio/>")
        audio_kind = self.adapter._track_kind_from_element(audio_element)
        self.assertEqual(audio_kind, schema.TrackKind.Audio)

        invalid_element = cElementTree.fromstring("<smell/>")
        with self.assertRaises(ValueError):
            self.adapter._track_kind_from_element(invalid_element)

    def test_transition_cut_point(self):
        transition_element = cElementTree.fromstring(
            """
            <transitionitem>
                <start>538</start>
                <end>557</end>
                <alignment>end-black</alignment>
                <cutPointTicks>160876800000</cutPointTicks>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
                <effect>
                    <name>Cross Dissolve</name>
                    <effectid>Cross Dissolve</effectid>
                    <effectcategory>Dissolve</effectcategory>
                    <effecttype>transition</effecttype>
                    <mediatype>video</mediatype>
                    <wipecode>0</wipecode>
                    <wipeaccuracy>100</wipeaccuracy>
                    <startratio>0</startratio>
                    <endratio>1</endratio>
                    <reverse>FALSE</reverse>
                </effect>
            </transitionitem>
            """
        )
        alignment_element = transition_element.find("./alignment")

        track_element = cElementTree.fromstring(
            """
            <track>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
            </track>
            """
        )
        context = self.adapter._Context(track_element)

        cut_point = self.adapter._transition_cut_point(
            transition_element, context
        )
        self.assertEqual(cut_point, opentime.RationalTime(557, 30))

        alignment_element.text = "end-black"
        cut_point = self.adapter._transition_cut_point(
            transition_element, context
        )
        self.assertEqual(cut_point, opentime.RationalTime(557, 30))

        for alignment in ("start", "start-black"):
            alignment_element.text = alignment
            cut_point = self.adapter._transition_cut_point(
                transition_element, context
            )
            self.assertEqual(cut_point, opentime.RationalTime(538, 30))

        # TODO: Mathematically, this cut point falls at 547.5, is the rounding
        #       down behavior "correct"?
        alignment_element.text = "center"
        cut_point = self.adapter._transition_cut_point(
            transition_element, context
        )
        self.assertEqual(cut_point, opentime.RationalTime(547, 30))


class TestFcp7XmlElements(unittest.TestCase, test_utils.OTIOAssertions):
    """ Tests for isolated element parsers. """
    adapter = adapters.from_name('fcp_xml').module()

    def test_timeline_for_sequence(self):
        tree = cElementTree.parse(FCP7_XML_EXAMPLE_PATH)

        # Get the test sequence and pare out the track definitions to keep this
        # test simple.
        seq_elem = tree.find("sequence")
        seq_elem.find("./media").clear()
        seq_elem.find("./timecode/string").text = "01:00:00:00"
        seq_elem.find("./timecode/frame").text = "108000"

        parser = self.adapter.FCP7XMLParser(tree)
        context = self.adapter._Context()
        timeline = parser.timeline_for_sequence(seq_elem, context)

        # Spot-check the sequence
        self.assertEqual(timeline.name, "sc01_sh010_layerA")
        self.assertEqual(
            timeline.global_start_time, opentime.RationalTime(108000, 30)
        )

        # Spot check that metadata translated with a tag and a property
        adapter_metadata = timeline.metadata["fcp_xml"]
        self.assertEqual(
            adapter_metadata["labels"]["label2"], "Forest"
        )
        self.assertEqual(
            adapter_metadata["@MZ.Sequence.VideoTimeDisplayFormat"], "104"
        )

        # make sure the media and name tags were not included in the metadata
        for k in {"name", "media"}:
            with self.assertRaises(KeyError):
                adapter_metadata[k]

    def test_marker_for_element(self):
        marker_element = cElementTree.fromstring(
            """
            <marker>
              <comment>so, this happened</comment>
              <name>My MArker 1</name>
              <in>113</in>
              <out>-1</out>
            </marker>
            """
        )

        marker = self.adapter.marker_for_element(marker_element, 30)

        self.assertEqual(marker.name, "My MArker 1")
        self.assertEqual(
            marker.marked_range,
            opentime.TimeRange(
                start_time=opentime.RationalTime(113, 30),
                duration=opentime.RationalTime(0, 30),
            )
        )
        self.assertEqual(
            marker.metadata["fcp_xml"]["comment"], "so, this happened"
        )
        with self.assertRaises(KeyError):
            marker.metadata["fcp_xml"]["name"]

    def test_markers_from_element(self):
        sequence_element = cElementTree.fromstring(
            """
            <sequence>
              <rate>
                <timebase>30</timebase>
                <ntsc>FALSE</ntsc>
              </rate>
              <marker>
                <comment>so, this happened</comment>
                <name>My MArker 1</name>
                <in>113</in>
                <out>-1</out>
              </marker>
              <marker>
                <comment>fsfsfs</comment>
                <name>dsf</name>
                <in>492</in>
                <out>-1</out>
              </marker>
              <marker>
                <comment/>
                <name/>
                <in>298</in>
                <out>-1</out>
              </marker>
              <labels>
                <label2>Forest</label2>
              </labels>
            </sequence>
            """
        )
        markers = self.adapter.markers_from_element(sequence_element)

        # Note that "None" --
        expected_names = ["My MArker 1", "dsf", ""]
        self.assertEqual([m.name for m in markers], expected_names)

    def test_stack_from_element(self):
        tree = cElementTree.parse(FCP7_XML_EXAMPLE_PATH)

        # Get the test sequence and pare out the track definitions to keep this
        # test simple.
        media_elem = tree.find("./sequence/media")

        parser = self.adapter.FCP7XMLParser(tree)
        context = self.adapter._Context(tree.find("./sequence"))
        tracks = parser.stack_for_element(media_elem, context)

        self.assertEqual(len(tracks), 8)

        audio_tracks = [
            t for t in tracks if t.kind == schema.TrackKind.Audio
        ]
        self.assertEqual(len(audio_tracks), 4)

        video_tracks = [
            t for t in tracks if t.kind == schema.TrackKind.Video
        ]
        self.assertEqual(len(video_tracks), 4)

    def test_track_for_element(self):
        tree = cElementTree.parse(FCP7_XML_EXAMPLE_PATH)

        sequence_elem = tree.find("./sequence[1]")
        context = self.adapter._Context(sequence_elem)
        # The track with "clipitem-2" is a decent and relatively complex
        # test case
        track_elem = sequence_elem.find(".//clipitem[@id='clipitem-2']/..")

        # Make a parser and prime the id cache by parsing the file
        parser = self.adapter.FCP7XMLParser(tree)
        parser.timeline_for_sequence(sequence_elem, self.adapter._Context())

        track = parser.track_for_element(
            track_elem, schema.TrackKind.Video, context
        )

        expected_instance_types = [
            schema.Gap,
            schema.Clip,
            schema.Gap,
            schema.Clip,
            schema.Clip,
            schema.Transition,
            schema.Gap,
            schema.Stack,
        ]
        track_item_types = [i.__class__ for i in track]
        self.assertEqual(track_item_types, expected_instance_types)
        self.assertEqual(len(track), 8)

    def test_media_reference_from_element(self):
        file_element = cElementTree.fromstring(
            """
            <file id="file-3">
              <name>sc01_sh030_anim.mov</name>
              <pathurl>file:///Scratch/media/sc01_sh030_anim.2.mov</pathurl>
              <rate>
                <timebase>30</timebase>
                <ntsc>FALSE</ntsc>
              </rate>
              <duration>400</duration>
              <timecode>
                <rate>
                  <timebase>30</timebase>
                  <ntsc>FALSE</ntsc>
                </rate>
                <string>01:00:00:00</string>
                <frame>108000</frame>
                <displayformat>NDF</displayformat>
                <reel>
                  <name/>
                </reel>
              </timecode>
              <media>
                <video>
                  <samplecharacteristics>
                    <rate>
                      <timebase>30</timebase>
                      <ntsc>FALSE</ntsc>
                    </rate>
                    <width>1280</width>
                    <height>720</height>
                    <anamorphic>FALSE</anamorphic>
                    <pixelaspectratio>square</pixelaspectratio>
                    <fielddominance>none</fielddominance>
                  </samplecharacteristics>
                </video>
                <audio>
                  <samplecharacteristics>
                    <depth>16</depth>
                    <samplerate>48000</samplerate>
                  </samplecharacteristics>
                  <channelcount>2</channelcount>
                </audio>
              </media>
            </file>
            """
        )

        parser = self.adapter.FCP7XMLParser(file_element)
        context = self.adapter._Context()
        ref = parser.media_reference_for_file_element(
            file_element,
            context=context,
        )

        self.assertEqual(
            ref.target_url, "file:///Scratch/media/sc01_sh030_anim.2.mov"
        )
        self.assertEqual(ref.name, "sc01_sh030_anim.mov")
        self.assertEqual(
            ref.available_range,
            opentime.TimeRange(
                start_time=opentime.RationalTime(108000, 30),
                duration=opentime.RationalTime(400, 30),
            )
        )

        # Spot-check a metadata field
        video_metadata = ref.metadata["fcp_xml"]["media"]["video"]
        self.assertEqual(
            video_metadata["samplecharacteristics"]["height"], "720"
        )

    def test_missing_media_reference_from_element(self):
        file_element = cElementTree.fromstring(
            """
            <file id="101_021_0030_FG01">
              <name>101_021_0030_FG01</name>
              <duration>155</duration>
              <rate>
                <ntsc>FALSE</ntsc>
                <timebase>24</timebase>
              </rate>
              <timecode>
                <rate>
                  <ntsc>FALSE</ntsc>
                  <timebase>24</timebase>
                </rate>
                <frame>1308828</frame>
                <displayformat>NDF</displayformat>
                <string>15:08:54:12</string>
                <reel>
                  <name>A173C021_181204_R207</name>
                </reel>
              </timecode>
            </file>
            """
        )

        parser = self.adapter.FCP7XMLParser(file_element)
        context = self.adapter._Context()
        ref = parser.media_reference_for_file_element(
            file_element,
            context=context,
        )

        self.assertTrue(isinstance(ref, schema.MissingReference))
        self.assertEqual(ref.name, "101_021_0030_FG01")
        self.assertEqual(
            ref.available_range,
            opentime.TimeRange(
                start_time=opentime.RationalTime(1308828, 24),
                duration=opentime.RationalTime(155, 24),
            )
        )

        # Spot-check a metadata field
        reelname = ref.metadata["fcp_xml"]["timecode"]["reel"]["name"]
        self.assertEqual(reelname, "A173C021_181204_R207")

    def test_clip_for_element(self):
        tree = cElementTree.parse(FCP7_XML_EXAMPLE_PATH)

        # Use clipitem-3 because it's self-contained and doesn't reference
        # other elements
        sequence_elem = tree.find(".//clipitem[@id='clipitem-3']/../../../..")
        clip_elem = tree.find(".//clipitem[@id='clipitem-3']")
        context = self.adapter._Context(sequence_elem)

        # Make a parser
        parser = self.adapter.FCP7XMLParser(tree)

        clip, time_range = parser.item_and_timing_for_element(
            clip_elem,
            head_transition=None,
            tail_transition=None,
            context=context,
        )

        self.assertEqual(clip.name, "sc01_sh020_anim.mov")

        expected_range = opentime.TimeRange(
            start_time=opentime.RationalTime(165, 30),
            duration=opentime.RationalTime(157, 30),
        )
        self.assertEqual(time_range, expected_range)

        expected_range = opentime.TimeRange(
            start_time=opentime.RationalTime(0, 30),
            duration=opentime.RationalTime(157, 30),
        )
        self.assertEqual(clip.source_range, expected_range)

    def test_generator_for_element(self):
        generator_element = cElementTree.fromstring(
            """
            <generatoritem id="clipitem-29">
              <name>White</name>
              <enabled>TRUE</enabled>
              <duration>1035764</duration>
              <start>383</start>
              <end>432</end>
              <in>86313</in>
              <out>86362</out>
              <rate>
                <timebase>24</timebase>
                <ntsc>TRUE</ntsc>
              </rate>
              <effect>
                <name>Color</name>
                <effectid>Color</effectid>
                <effectcategory>Matte</effectcategory>
                <effecttype>generator</effecttype>
                <mediatype>video</mediatype>
                <parameter authoringApp="PremierePro">
                  <parameterid>fillcolor</parameterid>
                  <name>Color</name>
                  <value>
                    <alpha>0</alpha>
                    <red>255</red>
                    <green>255</green>
                    <blue>255</blue>
                  </value>
                </parameter>
              </effect>
            </generatoritem>
            """
        )
        parent_context_element = cElementTree.fromstring(
            """
            <track>
              <rate>
                <timebase>24</timebase>
                <ntsc>TRUE</ntsc>
              </rate>
            </track>
            """
        )

        context = self.adapter._Context(parent_context_element)

        # Make a parser
        parser = self.adapter.FCP7XMLParser(generator_element)

        clip, time_range = parser.item_and_timing_for_element(
            generator_element,
            head_transition=None,
            tail_transition=None,
            context=context,
        )

        self.assertEqual(clip.name, "White")

        expected_range = opentime.TimeRange(
            start_time=opentime.RationalTime(383, (24000 / 1001.0)),
            duration=opentime.RationalTime(49, (24000 / 1001.0)),
        )
        self.assertEqual(time_range, expected_range)

        expected_source_range = opentime.TimeRange(
            start_time=opentime.RationalTime(86313, (24000 / 1001.0)),
            duration=opentime.RationalTime(49, (24000 / 1001.0)),
        )
        self.assertEqual(clip.source_range, expected_source_range)

        ref = clip.media_reference
        self.assertTrue(
            isinstance(ref, schema.GeneratorReference)
        )
        self.assertEqual(ref.name, "Color")
        self.assertEqual(
            ref.metadata["fcp_xml"]["parameter"]["value"]["red"], "255"
        )

    def test_effect_from_filter_element(self):
        tree = cElementTree.parse(FILTER_XML_EXAMPLE_PATH)

        # Make a parser
        parser = self.adapter.FCP7XMLParser(tree)
        effect = parser.effect_from_filter_element(tree)

        self.assertEqual(effect.name, "Time Remap")

        # spot-check metadata
        effect_meta = effect.metadata["fcp_xml"]
        self.assertEqual(effect_meta["effectid"], "timeremap")
        self.assertEqual(len(effect_meta["parameter"]), 5)

    def test_transition_for_element(self):
        transition_element = cElementTree.fromstring(
            """
            <transitionitem>
              <start>538</start>
              <end>557</end>
              <alignment>end-black</alignment>
              <cutPointTicks>160876800000</cutPointTicks>
              <rate>
                <timebase>30</timebase>
                <ntsc>FALSE</ntsc>
              </rate>
              <effect>
                <name>Cross Dissolve</name>
                <effectid>Cross Dissolve</effectid>
                <effectcategory>Dissolve</effectcategory>
                <effecttype>transition</effecttype>
                <mediatype>video</mediatype>
                <wipecode>0</wipecode>
                <wipeaccuracy>100</wipeaccuracy>
                <startratio>0</startratio>
                <endratio>1</endratio>
                <reverse>FALSE</reverse>
              </effect>
            </transitionitem>
            """
        )

        track_element = cElementTree.fromstring(
            """
            <track>
                <rate>
                    <timebase>30</timebase>
                    <ntsc>FALSE</ntsc>
                </rate>
            </track>
            """
        )
        context = self.adapter._Context(track_element)

        parser = self.adapter.FCP7XMLParser(transition_element)
        transition = parser.transition_for_element(transition_element, context)

        self.assertEqual(transition.name, "Cross Dissolve")
        self.assertEqual(
            transition.transition_type,
            schema.TransitionTypes.SMPTE_Dissolve,
        )


class AdaptersFcp7XmlTest(unittest.TestCase, test_utils.OTIOAssertions):
    adapter = adapters.from_name('fcp_xml').module()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def test_build_empty_file(self):
        media_ref = schema.MissingReference(
            name="test_clip_name",
            available_range=opentime.TimeRange(
                opentime.RationalTime(820489, 24),
                opentime.RationalTime(2087, 24),
            ),
            metadata={
                "fcp_xml": {
                    "timecode": {
                        "rate": {"ntsc": "FALSE", "timebase": "24"},
                        "displayformat": "NDF",
                        "reel": {
                            "name": "test_reel_name",
                        },
                    }
                }
            },
        )

        file_element = self.adapter._build_empty_file(
            media_ref,
            media_ref.available_range.start_time,
            br_map={},
        )

        self.assertEqual(file_element.find("./name").text, "test_clip_name")
        self.assertEqual(file_element.find("./duration").text, "2087")

        rate_element = file_element.find("./rate")
        self.assertEqual(rate_element.find("./ntsc").text, "FALSE")
        self.assertEqual(rate_element.find("./timebase").text, "24")

        tc_element = file_element.find("./timecode")
        self.assertEqual(tc_element.find("./rate/ntsc").text, "FALSE")
        self.assertEqual(tc_element.find("./rate/timebase").text, "24")
        self.assertEqual(tc_element.find("./string").text, "09:29:47:01")
        self.assertEqual(tc_element.find("./reel/name").text, "test_reel_name")

    def test_read(self):
        timeline = adapters.read_from_file(FCP7_XML_EXAMPLE_PATH)

        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 8)

        video_tracks = [
            t for t in timeline.tracks
            if t.kind == schema.TrackKind.Video
        ]
        audio_tracks = [
            t for t in timeline.tracks
            if t.kind == schema.TrackKind.Audio
        ]

        self.assertEqual(len(video_tracks), 4)
        self.assertEqual(len(audio_tracks), 4)

        video_clip_names = (
            ("", 'sc01_sh010_anim.mov'),
            (
                "",
                'sc01_sh010_anim.mov',
                "",
                'sc01_sh020_anim.mov',
                'sc01_sh030_anim.mov',
                'Cross Dissolve',
                "",
                'sc01_sh010_anim'
            ),
            ("", 'test_title'),
            (
                "",
                'sc01_master_layerA_sh030_temp.mov',
                'Cross Dissolve',
                'sc01_sh010_anim.mov'
            )
        )

        for n, track in enumerate(video_tracks):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        audio_clip_names = (
            ("", 'sc01_sh010_anim.mov', "", 'sc01_sh010_anim.mov'),
            ("", 'sc01_placeholder.wav', "", 'sc01_sh010_anim'),
            ("", 'track_08.wav'),
            ("", 'sc01_master_layerA_sh030_temp.mov', 'sc01_sh010_anim.mov')
        )

        for n, track in enumerate(audio_tracks):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                audio_clip_names[n]
            )

        video_clip_durations = (
            ((536, 30.0), (100, 30.0)),
            (
                (13, 30.0),
                (100, 30.0),
                (52, 30.0),
                (157, 30.0),
                (235, 30.0),
                ((19, 30.0), (0, 30.0)),
                (79, 30.0),
                (320, 30.0)
            ),
            ((15, 30.0), (941, 30.0)),
            ((956, 30.0), (208, 30.0), ((12, 30.0), (13, 30.0)), (82, 30.0))
        )

        for t, track in enumerate(video_tracks):
            for c, clip in enumerate(track):
                if isinstance(clip, schema.Transition):
                    self.assertEqual(
                        clip.in_offset,
                        opentime.RationalTime(
                            *video_clip_durations[t][c][0]
                        )
                    )
                    self.assertEqual(
                        clip.out_offset,
                        opentime.RationalTime(
                            *video_clip_durations[t][c][1]
                        )
                    )
                else:
                    self.assertEqual(
                        clip.source_range.duration,
                        opentime.RationalTime(*video_clip_durations[t][c])
                    )

        audio_clip_durations = (
            ((13, 30.0), (100, 30.0), (423, 30.0), (100, 30.0), (423, 30.0)),
            (
                (335, 30.0),
                (170, 30.0),
                (131, 30.0),
                (294, 30.0),
                (34, 30.0),
                (124, 30.0)
            ),
            ((153, 30.0), (198, 30.0)),
            ((956, 30.0), (221, 30.0), (94, 30.0))
        )

        for t, track in enumerate(audio_tracks):
            for c, clip in enumerate(track):
                self.assertEqual(
                    clip.source_range.duration,
                    opentime.RationalTime(*audio_clip_durations[t][c])
                )

        timeline_marker_names = ('My MArker 1', 'dsf', "")

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(marker.name, timeline_marker_names[n])

        timeline_marker_start_times = ((113, 30.0), (492, 30.0), (298, 30.0))

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(
                marker.marked_range.start_time,
                opentime.RationalTime(*timeline_marker_start_times[n])
            )

        timeline_marker_comments = ('so, this happened', 'fsfsfs', None)

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(
                marker.metadata.get('fcp_xml', {}).get('comment'),
                timeline_marker_comments[n]
            )

        clip_with_marker = video_tracks[1][4]
        clip_marker = clip_with_marker.markers[0]
        self.assertEqual(clip_marker.name, "")
        self.assertEqual(
            clip_marker.marked_range.start_time,
            opentime.RationalTime(73, 30.0)
        )
        self.assertEqual(
            clip_marker.metadata.get('fcp_xml', {}).get('comment'),
            None
        )

    def test_roundtrip_mem2disk2mem(self):
        timeline = schema.Timeline('test_timeline')

        RATE = 48.0

        video_reference = schema.ExternalReference(
            target_url="/var/tmp/test1.mov",
            available_range=opentime.TimeRange(
                opentime.RationalTime(value=100, rate=RATE),
                opentime.RationalTime(value=1000, rate=RATE)
            )
        )
        video_reference.name = "test_vid_one"
        audio_reference = schema.ExternalReference(
            target_url="/var/tmp/test1.wav",
            available_range=opentime.TimeRange(
                opentime.RationalTime(value=0, rate=RATE),
                opentime.RationalTime(value=1000, rate=RATE)
            ),
        )
        audio_reference.name = "test_wav_one"
        generator_reference = schema.GeneratorReference(
            name="Color",
            generator_kind="Color",
            metadata={
                "fcp_xml": {
                    "effectcategory": "Matte",
                    "effecttype": "generator",
                    "mediatype": "video",
                    "parameter": {
                        "@authoringApp": "PremierePro",
                        "parameterid": "fillcolor",
                        "name": "Color",
                        "value": {
                            "alpha": "0",
                            "red": "255",
                            "green": "255",
                            "blue": "255",
                        },
                    },
                },
            },
        )

        v0 = schema.Track(kind=schema.track.TrackKind.Video)
        v1 = schema.Track(kind=schema.track.TrackKind.Video)

        timeline.tracks.extend([v0, v1])

        a0 = schema.Track(kind=schema.track.TrackKind.Audio)

        timeline.tracks.append(a0)

        v0.extend(
            [
                schema.Clip(
                    name='test_clip1',
                    media_reference=video_reference,
                    source_range=opentime.TimeRange(
                        opentime.RationalTime(value=112, rate=RATE),
                        opentime.RationalTime(value=40, rate=RATE)
                    )
                ),
                schema.Gap(
                    source_range=opentime.TimeRange(
                        duration=opentime.RationalTime(
                            value=60,
                            rate=RATE
                        )
                    )
                ),
                schema.Clip(
                    name='test_clip2',
                    media_reference=video_reference,
                    source_range=opentime.TimeRange(
                        opentime.RationalTime(value=123, rate=RATE),
                        opentime.RationalTime(value=260, rate=RATE)
                    )
                ),
                schema.Clip(
                    name='test_generator_clip',
                    media_reference=generator_reference,
                    source_range=opentime.TimeRange(
                        opentime.RationalTime(value=292, rate=24.0),
                        opentime.RationalTime(value=183, rate=24.0)
                    )
                ),
            ]
        )

        v1.extend([
            schema.Gap(
                source_range=opentime.TimeRange(
                    duration=opentime.RationalTime(value=500, rate=RATE)
                )
            ),
            schema.Clip(
                name='test_clip3',
                media_reference=video_reference,
                source_range=opentime.TimeRange(
                    opentime.RationalTime(value=112, rate=RATE),
                    opentime.RationalTime(value=55, rate=RATE)
                )
            )
        ])

        a0.extend(
            [
                schema.Gap(
                    source_range=opentime.TimeRange(
                        duration=opentime.RationalTime(value=10, rate=RATE)
                    )
                ),
                schema.Clip(
                    name='test_clip4',
                    media_reference=audio_reference,
                    source_range=opentime.TimeRange(
                        opentime.RationalTime(value=152, rate=RATE),
                        opentime.RationalTime(value=248, rate=RATE)
                    ),
                )
            ]
        )

        timeline.tracks.markers.append(
            schema.Marker(
                name='test_timeline_marker',
                marked_range=opentime.TimeRange(
                    opentime.RationalTime(123, RATE)
                ),
                metadata={'fcp_xml': {'comment': 'my_comment'}}
            )
        )

        v1[1].markers.append(
            schema.Marker(
                name='test_clip_marker',
                marked_range=opentime.TimeRange(
                    opentime.RationalTime(125, RATE)
                ),
                metadata={'fcp_xml': {'comment': 'my_comment'}}
            )
        )

        # make sure that global_start_time.rate survives the round trip
        timeline.global_start_time = opentime.RationalTime(100, RATE)

        result = adapters.write_to_string(
            timeline,
            adapter_name='fcp_xml'
        )
        new_timeline = adapters.read_from_string(
            result,
            adapter_name='fcp_xml'
        )

        # Since FCP XML's "sequence" is a marriage of the timeline and the
        # main tracks stack, the tracks stack loses its name
        new_timeline.tracks.name = timeline.tracks.name

        self.assertEqual(new_timeline.name, 'test_timeline')

        # Before comparing, scrub ignorable metadata introduced in
        # serialization (things like unique ids minted by the adapter)
        # Since we seeded metadata for the generator, keep that metadata
        del new_timeline.metadata["fcp_xml"]
        for child in new_timeline.tracks.children_if():
            try:
                del child.metadata["fcp_xml"]
            except KeyError:
                pass

            try:
                is_generator = isinstance(
                    child.media_reference, schema.GeneratorReference
                )
                if not is_generator:
                    del child.media_reference.metadata["fcp_xml"]
            except (AttributeError, KeyError):
                pass

        self.assertJsonEqual(new_timeline, timeline)

    def test_roundtrip_disk2mem2disk(self):
        # somefile.xml -> OTIO
        timeline = adapters.read_from_file(FCP7_XML_EXAMPLE_PATH)
        tmp_path = tempfile.mkstemp(suffix=".xml", text=True)[1]

        # somefile.xml -> OTIO -> tempfile.xml
        adapters.write_to_file(timeline, tmp_path)

        # somefile.xml -> OTIO -> tempfile.xml -> OTIO
        result = adapters.read_from_file(tmp_path)

        # TODO: OTIO doesn't support linking items for the moment, so the
        # adapter reads links to the metadata, but doesn't write them.
        # See _dict_to_xml_tree for more information.
        def scrub_md_dicts(timeline):
            def scrub_displayformat(md_dict):
                for ignore_key in {"link"}:
                    try:
                        del md_dict[ignore_key]
                    except KeyError:
                        pass

                for value in list(md_dict.values()):
                    try:
                        value.items()
                        scrub_displayformat(value)
                    except AttributeError:
                        pass

            for child in timeline.tracks.children_if():
                scrub_displayformat(child.metadata)
                try:
                    scrub_displayformat(child.media_reference.metadata)
                except AttributeError:
                    pass

        # media reference bug, ensure that these match
        self.assertJsonEqual(
            result.tracks[0][1].media_reference,
            timeline.tracks[0][1].media_reference
        )

        scrub_md_dicts(result)
        scrub_md_dicts(timeline)

        self.assertJsonEqual(result, timeline)
        self.assertIsOTIOEquivalentTo(result, timeline)

        # But the xml text on disk is not identical because otio has a subset
        # of features to xml and we drop all the nle specific preferences.
        with open(FCP7_XML_EXAMPLE_PATH) as original_file:
            with open(tmp_path) as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())

    def test_hiero_flavored_xml(self):
        timeline = adapters.read_from_file(HIERO_XML_PATH)
        self.assertTrue(len(timeline.tracks), 1)
        self.assertTrue(timeline.tracks[0].name == 'Video 1')

        clips = [c for c in timeline.tracks[0].clip_if()]
        self.assertTrue(len(clips), 2)

        self.assertTrue(clips[0].name == 'A160C005_171213_R0MN')
        self.assertTrue(clips[1].name == '/')

        self.assertTrue(
            isinstance(
                clips[0].media_reference,
                schema.ExternalReference
            )
        )

        self.assertTrue(
            isinstance(
                clips[1].media_reference,
                schema.MissingReference
            )
        )

        source_range = opentime.TimeRange(
            start_time=opentime.RationalTime(1101071, 24),
            duration=opentime.RationalTime(1055, 24)
        )
        self.assertTrue(clips[0].source_range == source_range)

        available_range = opentime.TimeRange(
            start_time=opentime.RationalTime(1101071, 24),
            duration=opentime.RationalTime(1055, 24)
        )
        self.assertTrue(clips[0].available_range() == available_range)

        clip_1_range = clips[1].available_range()
        self.assertEqual(
            clip_1_range,
            opentime.TimeRange(
                opentime.RationalTime(),
                opentime.RationalTime(1, 24),
            )
        )

        # Test serialization
        tmp_path = tempfile.mkstemp(suffix=".xml", text=True)[1]
        adapters.write_to_file(timeline, tmp_path)

        # Similar to the test_roundtrip_disk2mem2disk above
        # the track name element among others will not be present in a new xml.
        with open(HIERO_XML_PATH) as original_file:
            with open(tmp_path) as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())

    def test_xml_with_empty_elements(self):
        timeline = adapters.read_from_file(EMPTY_ELEMENT_XML_PATH)

        # Spot-check the EDL, this one would throw exception on load before
        self.assertEqual(len(timeline.video_tracks()), 12)
        self.assertEqual(len(timeline.video_tracks()[0]), 34)

    def test_read_generators(self):
        timeline = adapters.read_from_file(GENERATOR_XML_EXAMPLE_PATH)

        video_track = timeline.tracks[0]
        audio_track = timeline.tracks[3]
        self.assertEqual(len(video_track), 6)
        self.assertEqual(len(audio_track), 3)

        # Check all video items are generators
        self.assertTrue(
            all(
                isinstance(item.media_reference, schema.GeneratorReference)
                for item in video_track
            )
        )

        # Check the video generator kinds
        self.assertEqual(
            [clip.media_reference.generator_kind for clip in video_track],
            ["Slug", "Slug", "Color", "Slug", "Slug", "GraphicAndType"],
        )

        # Check all non-gap audio items are generators
        self.assertTrue(
            all(
                isinstance(item.media_reference, schema.GeneratorReference)
                for item in video_track if not isinstance(item, schema.Gap)
            )
        )


if __name__ == '__main__':
    unittest.main()
