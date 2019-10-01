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
from opentimelineio.schema import (
    Timeline,
    Stack,
    Track,
    Transition,
    Clip,
    Gap,
    ExternalReference,
    TrackKind)

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


def _rat_tm_from_secs(val, rate=25.0):
    """Return a RationalTime for the given timestamp (in seconds)."""
    return otio.opentime.from_seconds(val).rescaled_to(rate)


def _tm_range_from_secs(start, dur, rate=25.0):
    """
    Return a TimeRange for the given timestamp and duration (in
    seconds).
    """
    return otio.opentime.TimeRange(
        _rat_tm_from_secs(start), _rat_tm_from_secs(dur))


def _make_media_ref(uri="file:///example", start=0, duration=1, name=""):
    """Return an ExternalReference."""
    ref = ExternalReference(
        target_url=uri,
        available_range=_tm_range_from_secs(start, duration))
    ref.name = name
    return ref


def _make_clip(uri="file:///example", start=0, duration=1, name=""):
    """Return a Clip."""
    ref = _make_media_ref(uri, start, duration)
    return Clip(name=name, media_reference=ref)


class XgesElement(object):
    """
    Generates an xges string to be converted to an otio timeline.
    """

    def __init__(self, name=None):
        self.ges = ElementTree.Element("ges")
        self.project = ElementTree.SubElement(self.ges, "project")
        if name is not None:
            self.project.attrib["metadatas"] = \
                "metadatas, name=(string){};".format(
                    SCHEMA.GstStructure.serialize_string(name))
        self.ressources = ElementTree.SubElement(
            self.project, "ressources")
        self.timeline = ElementTree.SubElement(
            self.project, "timeline")
        self.layer_priority = 0
        self.track_id = 0
        self.clip_id = 0
        self.layer = None

    def add_audio_track(self):
        """Add a basic Audio track."""
        track = ElementTree.SubElement(
            self.timeline, "track", {
                "caps": "audio/x-raw(ANY)",
                "track-type": "2",
                "track-id": str(self.track_id),
                "properties":
                    r'properties, restriction-caps=(string)'
                    r'"audio/x-raw\,\ format\=\(string\)S32LE\,\ '
                    r'channels\=\(int\)2\,\ rate\=\(int\)44100\,\ '
                    r'layout\=\(string\)interleaved", '
                    r'mixing=(boolean)true;'})
        self.track_id += 1
        return track

    def add_video_track(self, framerate=None):
        """Add a basic Video track."""
        res_caps = \
            r"video/x-raw\,\ width\=\(int\)300\,\ height\=\(int\)250"
        if framerate:
            res_caps += r"\,\ framerate\=\(fraction\){}".format(framerate)
        track = ElementTree.SubElement(
            self.timeline, "track", {
                "caps": "video/x-raw(ANY)",
                "track-type": "4",
                "track-id": str(self.track_id),
                "properties":
                    'properties, restriction-caps=(string)'
                    '"{}", mixing=(boolean)true;'.format(res_caps)})
        self.track_id += 1
        return track

    def add_layer(self):
        """Append a (lower priority) layer to the timeline."""
        self.layer = ElementTree.SubElement(
            self.timeline, "layer",
            {"priority": str(self.layer_priority)})
        self.layer_priority += 1
        return self.layer

    def add_asset(self, asset_id, extract_type, duration=None):
        """Add an asset to the project if it does not already exist."""
        asset = self.ressources.find(
            "./asset[@id='{}'][@extractable-type-name='{}']".format(
                asset_id, extract_type))
        if asset is not None:
            return asset
        asset = ElementTree.SubElement(
            self.ressources, "asset",
            {"id": asset_id, "extractable-type-name": extract_type})
        if duration is not None:
            asset.attrib["properties"] = \
                "properties, duration=(guint64){:d};".format(
                    duration * GST_SECOND)
        return asset

    def add_clip(
            self, start, duration, inpoint, type_name, track_types,
            asset_id=None, name=None, asset_duration=-1,
            properties=None, metadatas=None):
        """Add a clip to the most recent layer."""
        layer_priority = self.layer.get("priority")
        if asset_id is None:
            if type_name == "GESUriClip":
                asset_id = "file:///example"
            elif type_name == "GESTransitionClip":
                asset_id = "crossfade"
            else:
                asset_id = type_name
        if asset_duration == -1 and type_name == "GESUriClip":
            asset_duration = 100
        clip = ElementTree.SubElement(
            self.layer, "clip", {
                "id": str(self.clip_id),
                "asset-id": asset_id,
                "type-name": type_name,
                "track-types": str(track_types),
                "layer-priority": str(layer_priority),
                "start": str(start * GST_SECOND),
                "inpoint": str(inpoint * GST_SECOND),
                "duration": str(duration * GST_SECOND)})
        self.add_asset(asset_id, type_name, asset_duration)
        if properties is not None:
            clip.attrib["properties"] = str(properties)
        if metadatas is not None:
            clip.attrib["metadatas"] = str(metadatas)
        if name is not None:
            if properties is None:
                properties = SCHEMA.GstStructure("properties;")
            properties.set("name", "string", name)
            clip.attrib["properties"] = str(properties)
        self.clip_id += 1
        return clip

    def get_otio_timeline(self):
        """Return a Timeline using otio's read_from_string method."""
        string = ElementTree.tostring(self.ges, encoding="UTF-8")
        return otio.adapters.read_from_string(string, "xges")


class CustomOtioAssertions(object):
    """Custom Assertions to perform on otio objects"""

    @staticmethod
    def _typed_name(otio_obj):
        name = otio_obj.name
        if not name:
            name = '""'
        return "{} {}".format(otio_obj.schema_name(), name)

    @classmethod
    def _otio_id(cls, otio_obj):
        otio_id = cls._typed_name(otio_obj)
        if isinstance(otio_obj, otio.core.Composable):
            otio_parent = otio_obj.parent()
            if otio_parent is None:
                otio_id += " (No Parent)"
            else:
                index = otio_parent.index(otio_obj)
                otio_id += " (Child {:d} of {})".format(
                    index, cls._typed_name(otio_parent))
        return otio_id

    @staticmethod
    def _tm(rat_tm):
        return "{:g}/{:g}({:g}s)".format(
            rat_tm.value, rat_tm.rate, rat_tm.value / rat_tm.rate)

    @classmethod
    def _range(cls, tm_range):
        return "start_time:" + cls._tm(tm_range.start_time) \
            + ", duration:" + cls._tm(tm_range.duration)

    @classmethod
    def _val_str(cls, val):
        if isinstance(val, otio.opentime.RationalTime):
            return cls._tm(val)
        if isinstance(val, otio.opentime.TimeRange):
            return cls._range(val)
        return str(val)

    def assertOtioHasAttr(self, otio_obj, attr_name):
        """Assert that the otio object has an attribute."""
        if not hasattr(otio_obj, attr_name):
            raise AssertionError(
                "{} has no attribute {}".format(
                    self._otio_id(otio_obj), attr_name))

    def assertOtioAttrIsNone(self, otio_obj, attr_name):
        """Assert that the otio object attribute is None."""
        self.assertOtioHasAttr(otio_obj, attr_name)
        val = getattr(otio_obj, attr_name)
        if val is not None:
            raise AssertionError(
                "{} {}: {} is not None".format(
                    self._otio_id(otio_obj), attr_name,
                    self._val_str(val)))

    def assertOtioAttrPathEqual(self, otio_obj, attr_path, compare):
        """
        Assert that the otio object attribute:
            attr_path[0].attr_path[1].---.attr_path[-1]
        is equal to 'compare'.
        If an attribute is callable, it will be called (with no
        arguments) before comparing.
        """
        first = True
        attr_str = ""
        val = otio_obj
        for attr_name in attr_path:
            if not hasattr(val, attr_name):
                raise AssertionError(
                    "{}{} has no attribute {}".format(
                        self._otio_id(otio_obj), attr_str, attr_name))
            val = getattr(val, attr_name)
            if callable(val):
                val = val()
            if first:
                first = False
                attr_str += " " + attr_name
            else:
                attr_str += "." + attr_name
        if val != compare:
            raise AssertionError(
                "{}{}: {} != {}".format(
                    self._otio_id(otio_obj), attr_str,
                    self._val_str(val), self._val_str(compare)))

    def assertOtioAttrEqual(self, otio_obj, attr_name, compare):
        """
        Assert that the otio object attribute is equal to 'compare'.
        If an attribute is callable, it will be called (with no
        arguments) before comparing.
        """
        self.assertOtioAttrPathEqual(otio_obj, [attr_name], compare)

    def assertOtioIsInstance(self, otio_obj, otio_class):
        """
        Assert that the otio object is an instance of the given class.
        """
        if not isinstance(otio_obj, otio_class):
            raise AssertionError(
                "{} is not an otio {} instance".format(
                    self._otio_id(otio_obj), otio_class.__name__))

    def assertOtioAttrIsInstance(self, otio_obj, attr_name, otio_class):
        """
        Assert that the otio object attribute is an instance of the
        given class.
        """
        self.assertOtioHasAttr(otio_obj, attr_name)
        val = getattr(otio_obj, attr_name)
        if not isinstance(val, otio_class):
            raise AssertionError(
                "{} {} is not an otio {} instance".format(
                    self._otio_id(otio_obj), attr_name,
                    otio_class.__name__))

    def assertOtioOffsetTotal(self, otio_trans, compare):
        """
        Assert that the Transition has a certain total offset.
        """
        in_set = otio_trans.in_offset
        out_set = otio_trans.out_offset
        if in_set + out_set != compare:
            raise AssertionError(
                "{} in_offset + out_offset: {} + {} != {}".format(
                    self._otio_id(otio_trans),
                    self._val_str(in_set), self._val_str(out_set),
                    self._val_str(compare)))

    def assertOtioNumChildren(self, otio_obj, compare):
        """
        Assert that the otio object has a certain number of children.
        """
        self.assertOtioIsInstance(otio_obj, otio.core.Composable)
        num = len(otio_obj)
        if num != compare:
            raise AssertionError(
                "{} has {:d} children != {}".format(
                    self._otio_id(otio_obj), num,
                    self._val_str(compare)))


class OtioTest(object):
    """Tests to be used by OtioTestNode and OtioTestTree."""

    @staticmethod
    def none_source(inst, otio_item):
        """Test that the source_range is None."""
        inst.assertOtioAttrIsNone(otio_item, "source_range")

    @staticmethod
    def is_audio(inst, otio_track):
        """Test that a Track is Audio."""
        inst.assertOtioAttrEqual(otio_track, "kind", TrackKind.Audio)

    @staticmethod
    def is_video(inst, otio_track):
        """Test that a Track is Video."""
        inst.assertOtioAttrEqual(otio_track, "kind", TrackKind.Video)

    @staticmethod
    def has_ex_ref(inst, otio_clip):
        """Test that a clip has an ExternalReference."""
        inst.assertOtioAttrIsInstance(
            otio_clip, "media_reference", ExternalReference)

    @staticmethod
    def start_time(start):
        """
        Return an equality test for an Item's source_range.start_time.
        Argument should be a timestamp in seconds.
        """
        return lambda inst, otio_item: inst.assertOtioAttrPathEqual(
            otio_item, ["source_range", "start_time"],
            _rat_tm_from_secs(start))

    @staticmethod
    def duration(dur):
        """
        Return an equality test for an Item's source_range.duration.
        Argument should be a timestamp in seconds.
        """
        return lambda inst, otio_item: inst.assertOtioAttrPathEqual(
            otio_item, ["source_range", "duration"],
            _rat_tm_from_secs(dur))

    @staticmethod
    def _test_both_rate(inst, otio_item, _rate):
        inst.assertOtioAttrPathEqual(
            otio_item, ["source_range", "start_time", "rate"], _rate)
        inst.assertOtioAttrPathEqual(
            otio_item, ["source_range", "duration", "rate"], _rate)

    @classmethod
    def rate(cls, _rate):
        """
        Return an equality test for an Item's
        source_range.start_time.rate and source_range.duration.rate.
        """
        return lambda inst, otio_item: cls._test_both_rate(
            inst, otio_item, _rate)

    @staticmethod
    def range(start, dur):
        """
        Return an equality test for an Item's source_range.
        Arguments should be timestamps in seconds.
        """
        return lambda inst, otio_item: inst.assertOtioAttrEqual(
            otio_item, "source_range", _tm_range_from_secs(start, dur))

    @staticmethod
    def range_in_parent(start, dur):
        """
        Return an equality test for an Item's range_in_parent().
        Arguments should be timestamps in seconds.
        """
        return lambda inst, otio_item: inst.assertOtioAttrEqual(
            otio_item, "range_in_parent", _tm_range_from_secs(start, dur))

    @staticmethod
    def offset_total(total):
        """
        Return an equality test for a Transition's total offset/range.
        Argument should be a timestamp in seconds.
        """
        return lambda inst, otio_trans: inst.assertOtioOffsetTotal(
            otio_trans, _rat_tm_from_secs(total))

    @staticmethod
    def name(name):
        """Return an equality test for an Otio Object's name."""
        return lambda inst, otio_item: inst.assertOtioAttrEqual(
            otio_item, "name", name)


class OtioTestNode(object):
    """
    An OtioTestTree Node that corresponds to some expected otio class.
    This holds information about the children of the node, as well as
    a list of additional tests to perform on the corresponding otio
    object. These tests should come from OtioTest.
    """

    def __init__(self, expect_type, children=[], tests=[]):
        if expect_type is Timeline:
            if len(children) != 1:
                raise ValueError("A Timeline must have one child")
        elif not issubclass(expect_type, otio.core.Composition):
            if children:
                raise ValueError(
                    "No children are allowed if not a Timeline or "
                    "Composition type")
        self.expect_type = expect_type
        self.children = children
        self.tests = tests


class OtioTestTree(object):
    """
    Test an otio object has the correct type structure, and perform
    additional tests along the way."""

    def __init__(self, unittest_inst, base, type_tests=None):
        """
        First argument is a unittest instance which will perform all
        tests.
        Second argument is a dictionary of classes who's values are a
        list of tests to perform whenever a node is found that is an
        instance of that class. These tests should come from OtioTest.
        Third argument is the base OtioTestNode, where the comparison
        will begin.
        """
        self.unittest_inst = unittest_inst
        if type_tests is None:
            self.type_tests = {}
        else:
            self.type_tests = type_tests
        self.base = base

    def test_compare(self, otio_obj):
        """
        Test that the given otio object has the expected tree structure
        and run all tests that are found.
        """
        self._sub_test_compare(otio_obj, self.base)

    def _sub_test_compare(self, otio_obj, node):
        self.unittest_inst.assertOtioIsInstance(
            otio_obj, node.expect_type)
        if isinstance(otio_obj, Timeline):
            self._sub_test_compare(otio_obj.tracks, node.children[0])
        elif isinstance(otio_obj, otio.core.Composition):
            self.unittest_inst.assertOtioNumChildren(
                otio_obj, len(node.children))
            for sub_obj, child in zip(otio_obj, node.children):
                self._sub_test_compare(sub_obj, child)
        for otio_type in self.type_tests:
            if isinstance(otio_obj, otio_type):
                for test in self.type_tests[otio_type]:
                    test(self.unittest_inst, otio_obj)
        for test in node.tests:
            test(self.unittest_inst, otio_obj)


class CustomXgesAssertions(object):
    """Custom Assertions to perform on a ges xml object"""

    @staticmethod
    def _xges_id(xml_el):
        xges_id = "Element <" + xml_el.tag
        for key, val in xml_el.attrib.items():
            xges_id += " " + key + "='" + val + "'"
        xges_id += " />\n"
        return xges_id

    def assertXgesNumElementsAtPath(self, xml_el, path, compare):
        """
        Assert that the xml element has a certain number of descendants
        at the given xml path.
        Returns the matching descendants.
        """
        found = xml_el.findall(path) or []
        num = len(found)
        if num != compare:
            raise AssertionError(
                "{}Number of elements found at path {}: "
                "{:d} != {:d}".format(
                    self._xges_id(xml_el), path, num, compare))
        return found

    def assertXgesOneElementAtPath(self, xml_el, path):
        """
        Assert that the xml element has exactly one descendants at the
        given xml path.
        Returns the matching descendent.
        """
        return self.assertXgesNumElementsAtPath(xml_el, path, 1)[0]

    def assertXgesHasTag(self, xml_el, tag):
        """Assert that the xml element has a certain tag."""
        if xml_el.tag != tag:
            raise AssertionError(
                "{}does not have the tag {}".format(
                    self._xges_id(xml_el), tag))

    def assertXgesHasAttr(self, xml_el, attr_name):
        """
        Assert that the xml element has a certain attribute.
        Returns its value.
        """
        if attr_name not in xml_el.attrib:
            raise AssertionError(
                "{}has no attribute {}".format(
                    self._xges_id(xml_el), attr_name))
        return xml_el.attrib[attr_name]

    def assertXgesNumElementsAtPathWithAttr(
            self, xml_el, path_base, attrs, compare):
        """
        Assert that the xml element has a certain number of descendants
        at the given xml path with the given attributes.
        Returns the matching descendants.
        """
        path = path_base
        for key, val in attrs.items():
            if key in ("start", "duration", "inpoint"):
                val *= GST_SECOND
            path += "[@{}='{!s}']".format(key, val)
        return self.assertXgesNumElementsAtPath(xml_el, path, compare)

    def assertXgesOneElementAtPathWithAttr(
            self, xml_el, path_base, attrs):
        """
        Assert that the xml element has exactly one descendants at the
        given xml path with the given attributes.
        Returns the matching descendent.
        """
        return self.assertXgesNumElementsAtPathWithAttr(
            xml_el, path_base, attrs, 1)[0]

    def assertXgesIsGesElement(self, ges_el):
        """
        Assert that the xml element has the expected basic structure of
        a ges element.
        """
        self.assertXgesHasTag(ges_el, "ges")
        self.assertXgesOneElementAtPath(ges_el, "./project")
        self.assertXgesOneElementAtPath(ges_el, "./project/ressources")
        self.assertXgesOneElementAtPath(ges_el, "./project/timeline")

    def assertXgesAttrEqual(self, xml_el, attr_name, compare):
        """
        Assert that the xml element's attribute is equal to 'compare'.
        """
        val = self.assertXgesHasAttr(xml_el, attr_name)
        compare = str(compare)
        if val != compare:
            raise AssertionError(
                "{}attribute {}: {} != {}".format(
                    self._xges_id(xml_el), attr_name, val, compare))

    def assertXgesHasInStructure(
            self, xml_el, struct_name, field_name, field_type):
        """
        Assert that the xml element has a GstStructure attribute that
        contains the given field.
        Returns the value.
        """
        struct = self.assertXgesHasAttr(xml_el, struct_name)
        struct = SCHEMA.GstStructure(struct)
        if field_name not in struct.fields:
            raise AssertionError(
                "{}attribute {} does not contain the field {}".format(
                    self._xges_id(xml_el), struct_name, field_name))
        if struct.fields[field_name][0] != field_type:
            raise AssertionError(
                "{}attribute {}'s field {} is not of the type {}".format(
                    self._xges_id(xml_el), struct_name, field_name,
                    field_type))
        return struct.fields[field_name][1]

    def assertXgesHasProperty(self, xml_el, prop_name, prop_type):
        """
        Assert that the xml element has the given property.
        Returns the value.
        """
        return self.assertXgesHasInStructure(
            xml_el, "properties", prop_name, prop_type)

    def assertXgesHasMetadata(self, xml_el, meta_name, meta_type):
        """
        Assert that the xml element has the given metadata.
        Returns the value.
        """
        return self.assertXgesHasInStructure(
            xml_el, "metadatas", meta_name, meta_type)

    def assertXgesPropertyEqual(
            self, xml_el, prop_name, prop_type, compare):
        """
        Assert that a certain xml element property is equal to
        'compare'.
        """
        val = self.assertXgesHasProperty(xml_el, prop_name, prop_type)
        # TODO: remove once python2 has ended
        if prop_type == "string":
            if type(val) is not str and isinstance(val, type(u"")):
                val = val.encode("utf8")
        if val != compare:
            raise AssertionError(
                "{}property {}: {!s} != {!s}".format(
                    self._xges_id(xml_el), prop_name, val, compare))

    def assertXgesMetadataEqual(
            self, xml_el, meta_name, meta_type, compare):
        """
        Assert that a certain xml element metadata is equal to
        'compare'.
        """
        val = self.assertXgesHasMetadata(xml_el, meta_name, meta_type)
        # TODO: remove once python2 has ended
        if meta_type == "string":
            if type(val) is not str and isinstance(val, type(u"")):
                val = val.encode("utf8")
        if val != compare:
            raise AssertionError(
                "{}metadata {}: {!s} != {!s}".format(
                    self._xges_id(xml_el), meta_name, val, compare))

    def assertXgesPropertiesEqual(self, xml_el, compare):
        """
        Assert that the xml element properties is equal to 'compare'.
        """
        properties = self.assertXgesHasAttr(xml_el, "properties")
        properties = SCHEMA.GstStructure(properties)
        if not isinstance(compare, SCHEMA.GstStructure):
            compare = SCHEMA.GstStructure(compare)
        if not properties.is_equivalent_to(compare):
            raise AssertionError(
                "{}properties:\n{!s}\n!=\n{!s}".format(
                    self._xges_id(xml_el), properties, compare))

    def assertXgesTrackTypes(self, ges_el, *track_types):
        """
        Assert that the ges element contains one track for each given
        track type, and no more.
        """
        for track_type in track_types:
            self.assertXgesOneElementAtPathWithAttr(
                ges_el, "./project/timeline/track",
                {"track-type": str(track_type)})
        self.assertXgesNumElementsAtPath(
            ges_el, "./project/timeline/track", len(track_types))

    def assertXgesNumLayers(self, ges_el, compare):
        """
        Assert that the ges element contains the expected number of
        layers.
        Returns the layers.
        """
        return self.assertXgesNumElementsAtPath(
            ges_el, "./project/timeline/layer", compare)

    def assertXgesLayer(self, ges_el, priority):
        return self.assertXgesOneElementAtPathWithAttr(
            ges_el, "./project/timeline/layer",
            {"priority": str(priority)})

    def assertXgesNumClips(self, ges_el, compare):
        """
        Assert that the ges element contains the expected number of
        clips.
        Returns the clips.
        """
        return self.assertXgesNumElementsAtPath(
            ges_el, "./project/timeline/layer/clip", compare)

    def assertXgesNumClipsInLayer(self, layer_el, compare):
        """
        Assert that the layer element contains the expected number of
        clips.
        Returns the clips.
        """
        return self.assertXgesNumElementsAtPath(
            layer_el, "./clip", compare)

    def assertXgesClip(self, ges_el, attrs):
        """
        Assert that the ges element contains only one clip with the
        given attributes.
        Returns the matching clip.
        """
        return self.assertXgesOneElementAtPathWithAttr(
            ges_el, "./project/timeline/layer/clip", attrs)

    def assertXgesAsset(self, ges_el, asset_id, extract_type):
        """
        Assert that the ges element contains only one asset with the
        given id and extract type.
        Returns the matching asset.
        """
        return self.assertXgesOneElementAtPathWithAttr(
            ges_el, "./project/ressources/asset",
            {"id": asset_id, "extractable-type-name": extract_type})

    def assertXgesClipHasAsset(self, ges_el, clip_el):
        """
        Assert that the ges clip has a corresponding asset.
        Returns the asset.
        """
        asset_id = self.assertXgesHasAttr(clip_el, "asset-id")
        extract_type = self.assertXgesHasAttr(clip_el, "type-name")
        return self.assertXgesAsset(ges_el, asset_id, extract_type)


class AdaptersXGESTest(
        unittest.TestCase, otio_test_utils.OTIOAssertions,
        CustomOtioAssertions, CustomXgesAssertions):

    def _get_xges_from_otio_timeline(self, timeline):
        ges_el = ElementTree.fromstring(
            otio.adapters.write_to_string(timeline, "xges"))
        self.assertIsNotNone(ges_el)
        self.assertXgesIsGesElement(ges_el)
        return ges_el

    def test_read(self):
        timeline = otio.adapters.read_from_file(XGES_EXAMPLE_PATH)
        test_tree = OtioTestTree(
            self, type_tests={
                Stack: [OtioTest.none_source],
                Track: [OtioTest.none_source],
                Clip: [OtioTest.has_ex_ref]},
            base=OtioTestNode(Stack, children=[
                OtioTestNode(
                    Track, tests=[OtioTest.is_audio],
                    children=[OtioTestNode(Clip)]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_video],
                    children=[
                        OtioTestNode(Gap), OtioTestNode(Clip),
                        OtioTestNode(Transition), OtioTestNode(Clip)
                    ]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_video],
                    children=[
                        OtioTestNode(Gap), OtioTestNode(Clip),
                        OtioTestNode(Gap), OtioTestNode(Clip)
                    ]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_audio],
                    children=[OtioTestNode(Gap), OtioTestNode(Clip)]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_video],
                    children=[OtioTestNode(Gap), OtioTestNode(Clip)]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_audio],
                    children=[OtioTestNode(Gap), OtioTestNode(Clip)])
            ]))
        test_tree.test_compare(timeline.tracks)

        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el, 2, 4)
        self.assertXgesNumLayers(ges_el, 5)
        for priority, expect_num, expect_track_types in zip(
                range(5), [1, 1, 2, 3, 1], [6, 2, 4, 4, 2]):
            layer = self.assertXgesLayer(ges_el, priority)
            clips = self.assertXgesNumClipsInLayer(layer, expect_num)
            for clip in clips:
                self.assertXgesAttrEqual(
                    clip, "track-types", expect_track_types)
                if clip.get("type-name") == "GESUriClip":
                    self.assertXgesClipHasAsset(ges_el, clip)

    def test_project_name(self):
        xges_el = XgesElement(UTF8_NAME)
        timeline = xges_el.get_otio_timeline()
        self.assertOtioAttrEqual(timeline, "name", UTF8_NAME)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        project_el = ges_el.find("./project")
        # already asserted that project_el exists with IsGesElement in
        # _get_xges_from_otio_timeline
        self.assertXgesMetadataEqual(
            project_el, "name", "string", UTF8_NAME)

    def test_clip_names(self):
        xges_el = XgesElement()
        xges_el.add_audio_track()
        xges_el.add_layer()
        names = [UTF8_NAME, "T", "C"]
        xges_el.add_clip(0, 2, 0, "GESUriClip", 6, name=names[0])
        xges_el.add_clip(1, 1, 0, "GESTransitionClip", 6, name=names[1])
        xges_el.add_clip(1, 2, 0, "GESUriClip", 6, name=names[2])
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(Stack, children=[
                OtioTestNode(Track, children=[
                    OtioTestNode(
                        Clip, tests=[OtioTest.name(names[0])]),
                    OtioTestNode(
                        Transition, tests=[OtioTest.name(names[1])]),
                    OtioTestNode(
                        Clip, tests=[OtioTest.name(names[2])])
                ]),
                OtioTestNode(Track, children=[
                    OtioTestNode(
                        Clip, tests=[OtioTest.name(names[0])]),
                    OtioTestNode(
                        Transition, tests=[OtioTest.name(names[1])]),
                    OtioTestNode(
                        Clip, tests=[OtioTest.name(names[2])])
                ]),
            ]))
        test_tree.test_compare(timeline.tracks)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesNumClips(ges_el, 3)
        for clip_id, name in zip(range(3), names):
            clip = self.assertXgesClip(ges_el, {"id": clip_id})
            self.assertXgesPropertyEqual(
                clip, "name", "string", name)

    def test_asset(self):
        xges_el = XgesElement()
        xges_el.add_layer()
        asset_id = "file:///ex%%mple"
        duration = 235
        xges_el.add_asset(asset_id, "GESUriClip", duration)
        xges_el.add_clip(0, 1, 5, "GESUriClip", 2, asset_id=asset_id)
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(Stack, children=[
                OtioTestNode(Track, children=[
                    OtioTestNode(
                        Clip, tests=[OtioTest.has_ex_ref])
                ])
            ]))
        test_tree.test_compare(timeline.tracks)
        self.assertOtioAttrPathEqual(
            timeline.tracks[0][0], ["media_reference", "target_url"],
            asset_id)
        self.assertOtioAttrPathEqual(
            timeline.tracks[0][0],
            ["media_reference", "available_range"],
            _tm_range_from_secs(0, duration))
        ges_el = self._get_xges_from_otio_timeline(timeline)
        asset = self.assertXgesAsset(ges_el, asset_id, "GESUriClip")
        self.assertXgesPropertyEqual(
            asset, "duration", "guint64", duration * GST_SECOND)

    def test_framerate(self):
        xges_el = XgesElement()
        framerate = 45.0
        xges_el.add_video_track(framerate)
        xges_el.add_layer()
        xges_el.add_clip(0, 1, 0, "GESUriClip", 4)
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(Stack, children=[
                OtioTestNode(Track, children=[
                    OtioTestNode(Clip, tests=[
                        OtioTest.range(0, 1),
                        OtioTest.rate(framerate)])
                ])
            ]))
        test_tree.test_compare(timeline.tracks)

    def test_clip_properties_and_metadatas(self):
        xges_el = XgesElement()
        xges_el.add_layer()
        props = SCHEMA.GstStructure(
            "properties", {
                "field2": ("int", 5), "field1": ("string", UTF8_NAME)})
        metas = SCHEMA.GstStructure(
            "metadatas", {
                "field3": ("int", 6), "field4": ("boolean", True)})
        xges_el.add_clip(
            0, 1, 0, "GESUriClip", 4, properties=props, metadatas=metas)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        clip = self.assertXgesClip(ges_el, {})
        self.assertXgesPropertyEqual(clip, "field1", "string", UTF8_NAME)
        self.assertXgesPropertyEqual(clip, "field2", "int", 5)
        self.assertXgesMetadataEqual(clip, "field3", "int", 6)
        self.assertXgesMetadataEqual(clip, "field4", "boolean", True)

    def test_empty_timeline(self):
        xges_el = XgesElement()
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(
                Stack, tests=[OtioTest.none_source]))
        test_tree.test_compare(timeline.tracks)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesNumLayers(ges_el, 0)

    def SKIP_test_empty_layer(self):
        # Test will fail since empty layers are lost!
        xges_el = XgesElement()
        xges_el.add_layer()
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(
                Stack, tests=[OtioTest.none_source], children=[
                    OtioTestNode(Track, tests=[OtioTest.none_source])]))
        test_tree.test_compare(timeline.tracks)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        layer_el = self.assertXgesNumLayers(ges_el, 1)[0]
        self.assertXgesNumClipsInLayer(layer_el, 0)

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
        xges_el = XgesElement()
        xges_el.add_audio_track()
        xges_el.add_layer()
        xges_el.add_clip(1, 2, 15, "GESUriClip", 2)
        xges_el.add_clip(2, 1, 0, "GESTransitionClip", 2)
        xges_el.add_clip(2, 4, 25, "GESUriClip", 2)
        xges_el.add_clip(4, 2, 0, "GESTransitionClip", 2)
        xges_el.add_clip(4, 3, 0, "GESUriClip", 2)
        xges_el.add_clip(9, 1, 0, "GESUriClip", 2)
        xges_el.add_clip(10, 1, 0, "GESUriClip", 2)
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, type_tests={
                Stack: [OtioTest.none_source],
                Track: [
                    OtioTest.none_source, OtioTest.is_audio],
                Clip: [OtioTest.has_ex_ref]},
            base=OtioTestNode(Stack, children=[
                OtioTestNode(Track, children=[
                    OtioTestNode(Gap, tests=[
                        OtioTest.range_in_parent(0, 1)]),
                    OtioTestNode(Clip, tests=[
                        OtioTest.range_in_parent(1, 1.5),
                        OtioTest.start_time(15)]),
                    OtioTestNode(Transition, tests=[
                        OtioTest.offset_total(1)]),
                    OtioTestNode(Clip, tests=[
                        OtioTest.range_in_parent(2.5, 2.5),
                        OtioTest.start_time(25.5)]),
                    OtioTestNode(Transition, tests=[
                        OtioTest.offset_total(2)]),
                    OtioTestNode(Clip, tests=[
                        OtioTest.range_in_parent(5, 2)]),
                    OtioTestNode(Gap, tests=[
                        OtioTest.range_in_parent(7, 2)]),
                    OtioTestNode(Clip, tests=[
                        OtioTest.range_in_parent(9, 1)]),
                    OtioTestNode(Clip, tests=[
                        OtioTest.range_in_parent(10, 1)])
                ])
            ]))
        test_tree.test_compare(timeline.tracks)

        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el, 2)
        self.assertXgesNumClips(ges_el, 7)
        self.assertXgesClip(
            ges_el, {
                "start": 1, "duration": 2, "inpoint": 15,
                "type-name": "GESUriClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 2, "duration": 1, "inpoint": 0,
                "type-name": "GESTransitionClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 2, "duration": 4, "inpoint": 25,
                "type-name": "GESUriClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 4, "duration": 2, "inpoint": 0,
                "type-name": "GESTransitionClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 4, "duration": 3, "inpoint": 0,
                "type-name": "GESUriClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 9, "duration": 1, "inpoint": 0,
                "type-name": "GESUriClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 10, "duration": 1, "inpoint": 0,
                "type-name": "GESUriClip", "track-types": 2})

    def test_nested_projects_and_stacks(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        xges_el.add_layer()
        asset = xges_el.add_asset("file:///example.xges", "GESTimeline")
        xges_el.add_clip(
            7, 2, 1, "GESUriClip", 4, "file:///example.xges")
        sub_xges_el = XgesElement()
        sub_xges_el.add_video_track()
        sub_xges_el.add_layer()
        sub_xges_el.add_clip(5, 4, 3, "GESUriClip", 4)
        asset.append(sub_xges_el.ges)

        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, type_tests={
                Track: [OtioTest.none_source, OtioTest.is_video],
                Clip: [OtioTest.has_ex_ref]},
            base=OtioTestNode(
                Stack, tests=[OtioTest.none_source], children=[
                    OtioTestNode(Track, children=[
                        OtioTestNode(Gap, tests=[OtioTest.duration(7)]),
                        OtioTestNode(
                            Stack, tests=[OtioTest.range(1, 2)],
                            children=[
                                OtioTestNode(Track, children=[
                                    OtioTestNode(Gap, tests=[
                                        OtioTest.duration(5)]),
                                    OtioTestNode(Clip, tests=[
                                        OtioTest.range(3, 4)])
                                ])
                            ])
                    ])
                ]))
        test_tree.test_compare(timeline.tracks)
        self._xges_has_nested_clip(timeline, 7, 2, 1, 5, 4, 3)

    def _xges_has_nested_clip(
            self, timeline, top_start, top_duration, top_inpoint,
            orig_start, orig_duration, orig_inpoint):
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el, 4)
        top_clip = self.assertXgesClip(
            ges_el, {
                "start": top_start, "duration": top_duration,
                "inpoint": top_inpoint, "type-name": "GESUriClip",
                "track-types": 4})
        self.assertXgesClipHasAsset(ges_el, top_clip)
        ges_asset = self.assertXgesAsset(
            ges_el, top_clip.get("asset-id"), "GESTimeline")
        ges_el = self.assertXgesOneElementAtPath(ges_asset, "ges")
        self.assertXgesIsGesElement(ges_el)
        self.assertXgesNumClips(ges_el, 1)
        orig_clip = self.assertXgesClip(
            ges_el, {
                "start": orig_start, "duration": orig_duration,
                "inpoint": orig_inpoint, "type-name": "GESUriClip",
                "track-types": 4})
        self.assertXgesClipHasAsset(ges_el, orig_clip)

    def test_source_range_stack(self):
        timeline = Timeline()
        track = Track()
        track.kind = TrackKind.Video
        timeline.tracks.append(track)
        track.append(_make_clip(start=2, duration=5))
        timeline.tracks.source_range = _tm_range_from_secs(1, 3)
        self._xges_has_nested_clip(timeline, 0, 3, 1, 0, 5, 2)

    def test_source_range_track(self):
        timeline = Timeline()
        track = Track()
        track.kind = TrackKind.Video
        timeline.tracks.append(track)
        track.append(_make_clip(start=2, duration=5))
        track.source_range = _tm_range_from_secs(1, 3)
        self._xges_has_nested_clip(timeline, 0, 3, 1, 0, 5, 2)

    def test_double_track(self):
        timeline = Timeline()
        track1 = Track()
        track1.kind = TrackKind.Video
        timeline.tracks.append(track1)
        track2 = Track()
        track2.kind = TrackKind.Video
        track1.append(_make_clip(start=4, duration=9))
        track1.append(track2)
        track2.append(_make_clip(start=2, duration=5))
        self._xges_has_nested_clip(timeline, 9, 5, 0, 0, 5, 2)

    def test_double_stack(self):
        timeline = Timeline()
        stack = Stack()
        stack.source_range = _tm_range_from_secs(1, 3)
        track = Track()
        track.kind = TrackKind.Video
        track.append(_make_clip(start=2, duration=5))
        stack.append(track)
        track = Track()
        track.kind = TrackKind.Video
        track.append(_make_clip())
        timeline.tracks.append(track)
        timeline.tracks.append(stack)
        self._xges_has_nested_clip(timeline, 0, 3, 1, 0, 5, 2)

    def test_track_merge(self):
        timeline = Timeline()
        for kind in [
                TrackKind.Audio,
                TrackKind.Video]:
            track = Track()
            track.kind = kind
            track.metadata["example-non-xges"] = str(kind)
            track.metadata["XGES"] = {
                "data": SCHEMA.GstStructure(
                    "name, key1=(string)hello, key2=(int)9;")}
            track.append(_make_clip(start=2, duration=5))
            timeline.tracks.append(track)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesClip(
            ges_el, {
                "start": 0, "duration": 5, "inpoint": 2,
                "type-name": "GESUriClip", "track-types": 6})

        # make tracks have different XGES metadata
        for track in timeline.tracks:
            track.metadata["XGES"]["data"].set(
                "key1", "string", str(track.kind))
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesClip(
            ges_el, {
                "start": 0, "duration": 5, "inpoint": 2,
                "type-name": "GESUriClip", "track-types": 2})
        self.assertXgesClip(
            ges_el, {
                "start": 0, "duration": 5, "inpoint": 2,
                "type-name": "GESUriClip", "track-types": 4})

    def test_timeline_is_unchanged(self):
        timeline = Timeline(name="example")
        timeline.tracks.source_range = _tm_range_from_secs(4, 5)
        track = Track("Track", source_range=_tm_range_from_secs(2, 3))
        track.metadata["key"] = 5
        track.append(_make_clip())
        timeline.tracks.append(track)

        before = timeline.deepcopy()
        otio.adapters.write_to_string(timeline, "xges")
        self.assertIsOTIOEquivalentTo(before, timeline)

    def test_XgesTrack_usage(self):
        xges_el = XgesElement()
        xges_el.add_layer()
        xges_el.add_clip(0, 1, 0, "GESUriClip", 4)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el)  # assert no tracks!

        props_before = xges_el.add_video_track().get("properties")
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el, 4)
        track = self.assertXgesOneElementAtPath(
            ges_el, "./project/timeline/track")
        self.assertXgesPropertiesEqual(track, props_before)

    def test_XgesTrack_from_kind(self):
        vid = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(TrackKind.Video)
        self.assertEqual(vid.track_type, 4)
        aud = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(TrackKind.Audio)
        self.assertEqual(aud.track_type, 2)

    def test_XgesTrack_equality(self):
        vid1 = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(TrackKind.Video)
        vid2 = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(TrackKind.Video)
        aud = SCHEMA.XgesTrack.\
            new_from_otio_track_kind(TrackKind.Audio)
        self.assertTrue(vid1.is_equivalent_to(vid2))
        self.assertFalse(vid1.is_equivalent_to(aud))

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
            "name, prop1=(str)4, prop2=(gint)4;")
        struct4 = SCHEMA.GstStructure(
            "name-alt, prop1=(string)4, prop2=(int)4;")
        struct5 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop3=(int)4;")
        struct6 = SCHEMA.GstStructure(
            "name, prop1=(int)4, prop2=(int)4;")
        struct7 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop2=(int)5;")
        struct8 = SCHEMA.GstStructure(
            "name, prop1=(string)4, prop2=(int)4, prop3=(bool)true;")
        struct9 = SCHEMA.GstStructure(
            "name, prop1=(string)4;")
        self.assertTrue(struct1.is_equivalent_to(struct2))
        self.assertTrue(struct1.is_equivalent_to(struct3))
        self.assertFalse(struct1.is_equivalent_to(struct4))
        self.assertFalse(struct1.is_equivalent_to(struct5))
        self.assertFalse(struct1.is_equivalent_to(struct6))
        self.assertFalse(struct1.is_equivalent_to(struct7))
        self.assertFalse(struct1.is_equivalent_to(struct8))
        self.assertFalse(struct1.is_equivalent_to(struct9))

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

    def test_GstStructure_type_aliases(self):
        struct = SCHEMA.GstStructure(
            "properties,String-1=(str)test,String-2=(s)\"test\","
            "Int-1=(i)-5,Int-2=(gint)-5,Uint-1=(u)5,Uint-2=(guint)5,"
            "Float-1=(f)0.5,Float-2=(gfloat)0.5,Double-1=(d)0.7,"
            "Double-2=(gdouble)0.7,Boolean-1=(bool)true,"
            "Boolean-2=(b)true,Boolean-3=(gboolean)true,"
            "Fraction=(GstFraction)2/5")
        self.assertEqual(struct.name, "properties")
        self.assertEqual(struct["String-1"], "test")
        self.assertEqual(struct["String-2"], "test")
        self.assertEqual(struct["Int-1"], -5)
        self.assertEqual(struct["Int-2"], -5)
        self.assertEqual(struct["Uint-1"], 5)
        self.assertEqual(struct["Uint-2"], 5)
        self.assertEqual(struct["Float-1"], 0.5)
        self.assertEqual(struct["Float-2"], 0.5)
        self.assertEqual(struct["Double-1"], 0.7)
        self.assertEqual(struct["Double-2"], 0.7)
        self.assertEqual(struct["Boolean-1"], True)
        self.assertEqual(struct["Boolean-2"], True)
        self.assertEqual(struct["Boolean-3"], True)
        self.assertEqual(struct["Fraction"], "2/5")
        struct = SCHEMA.GstStructure("properties")
        struct.set("prop", "s", "test test")
        self.assertEqual(struct["prop"], "test test")
        self.assertEqual(struct.fields["prop"][0], "string")
        struct.set("prop", "str", "test test")
        self.assertEqual(struct["prop"], "test test")
        self.assertEqual(struct.fields["prop"][0], "string")
        struct.set("prop", "i", -5)
        self.assertEqual(struct["prop"], -5)
        self.assertEqual(struct.fields["prop"][0], "int")
        struct.set("prop", "gint", -5)
        self.assertEqual(struct["prop"], -5)
        self.assertEqual(struct.fields["prop"][0], "int")
        struct.set("prop", "u", 5)
        self.assertEqual(struct["prop"], 5)
        self.assertEqual(struct.fields["prop"][0], "uint")
        struct.set("prop", "guint", 5)
        self.assertEqual(struct["prop"], 5)
        self.assertEqual(struct.fields["prop"][0], "uint")
        struct.set("prop", "f", 0.5)
        self.assertEqual(struct["prop"], 0.5)
        self.assertEqual(struct.fields["prop"][0], "float")
        struct.set("prop", "gfloat", 0.5)
        self.assertEqual(struct["prop"], 0.5)
        self.assertEqual(struct.fields["prop"][0], "float")
        struct.set("prop", "d", 0.7)
        self.assertEqual(struct["prop"], 0.7)
        self.assertEqual(struct.fields["prop"][0], "double")
        struct.set("prop", "gdouble", 0.7)
        self.assertEqual(struct["prop"], 0.7)
        self.assertEqual(struct.fields["prop"][0], "double")
        struct.set("prop", "b", True)
        self.assertEqual(struct["prop"], True)
        self.assertEqual(struct.fields["prop"][0], "boolean")
        struct.set("prop", "bool", True)
        self.assertEqual(struct["prop"], True)
        self.assertEqual(struct.fields["prop"][0], "boolean")
        struct.set("prop", "gboolean", True)
        self.assertEqual(struct["prop"], True)
        self.assertEqual(struct.fields["prop"][0], "boolean")
        struct.set("prop", "GstFraction", Fraction("2/5"))
        self.assertEqual(struct["prop"], "2/5")
        self.assertEqual(struct.fields["prop"][0], "fraction")

    def test_GstStructure_invalid_parse(self):
        # invalid names:
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("0name, prop=(int)4;")
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("{}, prop=(int)4;".format(UTF8_NAME))
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("0name", {"prop": ("int", 4)})
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("0name", "ignore, prop=(int)4;")
        # invalid fieldnames:
        struct = SCHEMA.GstStructure("name")
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop erty=(int)4;")
        with self.assertRaises(ValueError):
            struct.set("prop erty", "int", 4)
        with self.assertRaises(ValueError):
            # the following would cause problems with serializing
            # followed by de-serializing, since it would create two
            # different fields!
            struct.set("prop=(int)4, other=", "string", "test")
        # invalid type names
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop=(my type)4;")
        with self.assertRaises(ValueError):
            struct.set("prop", "int ", 4)
        with self.assertRaises(ValueError):
            struct.set("prop", " int", 4)
        with self.assertRaises(ValueError):
            struct.set("prop", "my type", 4)
        # invalid serialized values
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop=(int)4.5")
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop=(float)7.0s")
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure('name, prop=(string);')
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop=(boolean)yesyes;")
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop=(fraction)1/2.0;")
        with self.assertRaises(ValueError):
            # no comma in list
            SCHEMA.GstStructure("name, prop=(list){ 5, 6 7 };")
        with self.assertRaises(ValueError):
            SCHEMA.GstStructure("name, prop=(list){ 5, 6, 7;")
        # invalid setting values
        with self.assertRaises(TypeError):
            struct.set("prop", "int", 4.5)
        with self.assertRaises(TypeError):
            struct.set("prop", "float", "4.5")
        with self.assertRaises(TypeError):
            struct.set("prop", "string", 4)
        with self.assertRaises(TypeError):
            struct.set("prop", "boolean", 0)
        with self.assertRaises(TypeError):
            struct.set("prop", "fraction", 1)
        with self.assertRaises(TypeError):
            struct.set("prop", "mytype", 4)
        with self.assertRaises(ValueError):
            struct.set("prop", "mytype", "test ")
        with self.assertRaises(ValueError):
            struct.set("prop", "mytype", "&")
        with self.assertRaises(ValueError):
            struct.set("prop", "mytype", "(int)4")
        with self.assertRaises(ValueError):
            struct.set("prop", "mytype", "4, other_prop=(string)insert")
        with self.assertRaises(ValueError):
            struct.set("prop", "mytype", "4;")  # would hide rest!
        with self.assertRaises(ValueError):
            struct.set("prop", "list", "{ 5, 6 7 }")  # no comma
        with self.assertRaises(ValueError):
            struct.set("prop", "list", "{ {5}, { 6 7} }")  # no comma

    def test_GstStructure_unknown_type(self):
        # TODO: remove once python2 has ended
        # Python2 does not have assertWarns
        if str is bytes:
            return
        struct = SCHEMA.GstStructure("properties")
        with self.assertRaises(ValueError):
            struct.set(
                "prop", "MyType", "test, other_field=(string)insert")
            # would cause errors when trying to reserialize!
        with self.assertRaises(ValueError):
            struct.set("prop", "MyType ", "test ")
            # don't want trailing whitespaces
        with self.assertWarns(UserWarning):
            struct.set("prop", "MyType", "test")
        self.assertEqual(struct["prop"], "test")
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure(
                "properties, prop= ( MyOtherType )  4-5  ;")
        self.assertEqual(struct["prop"], "4-5")
        self.assertEqual(
            str(struct), "properties, prop=(MyOtherType)4-5;")
        with self.assertWarns(UserWarning):
            SCHEMA.GstStructure("properties", struct)
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure(
                'properties, prop=(string) {  "spa\\ ce"  ,  ( string )'
                '  test }  ;')
        self.assertEqual(
            struct["prop"], '{ "spa\\ ce", (string)test }')
        self.assertEqual(
            str(struct), 'properties, prop=(string){ "spa\\ ce", '
            '(string)test };')
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure(
                "properties, prop=(int)<1,3,4,5>;")
        self.assertEqual(struct["prop"], "< 1, 3, 4, 5 >")
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure(
                "properties, prop=(int)[1,3];")
        self.assertEqual(struct["prop"], "[ 1, 3 ]")
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure(
                "properties, prop=(MyType){(MyType){1,2},"
                "(MyType){3a3,4,5}};")
        self.assertEqual(
            struct["prop"],
            "{ (MyType){ 1, 2 }, (MyType){ 3a3, 4, 5 } }")

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
