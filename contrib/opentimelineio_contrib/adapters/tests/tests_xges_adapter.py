# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

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
    TrackKind,
    Effect,
    Marker,
    MarkerColor)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
XGES_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "xges_example.xges")
XGES_TIMING_PATH = os.path.join(SAMPLE_DATA_DIR, "xges_timing_example.xges")
XGES_NESTED_PATH = os.path.join(SAMPLE_DATA_DIR, "xges_nested_example.xges")
IMAGE_SEQUENCE_EXAMPLE_PATH = os.path.join(
    SAMPLE_DATA_DIR, "image_sequence_example.otio")

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


def _add_marker(otio_item, name, color, start, duration):
    """Add a marker to an otio item"""
    otio_item.markers.append(Marker(
        name=name, color=color,
        marked_range=_tm_range_from_secs(start, duration)))


def _make_ges_marker(
        position, otio_color=None, comment=None, metadatas=None):
    """
    Return a GESMarker with the given timeline position (in seconds).
    """
    if comment is not None:
        metadatas = metadatas or SCHEMA.GstStructure("metadatas")
        metadatas.set("comment", "string", comment)
    ges_marker = SCHEMA.GESMarker(position * GST_SECOND, metadatas)
    if otio_color is not None:
        ges_marker.set_color_from_otio_color(otio_color)
    return ges_marker


class XgesElement:
    """
    Generates an xges string to be converted to an otio timeline.
    """

    def __init__(self, name=None, marker_list=None):
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
        if marker_list is not None:
            self.timeline.attrib["metadatas"] = \
                "metadatas, markers=(GESMarkerList){};".format(
                    SCHEMA.GstStructure.serialize_marker_list(marker_list))
        self.layer_priority = 0
        self.track_id = 0
        self.clip_id = 0
        self.layer = None
        self.clip = None

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
            res_caps += fr"\,\ framerate\=\(fraction\){framerate}"
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

    def add_text_track(self):
        """Add a basic Audio track."""
        track = ElementTree.SubElement(
            self.timeline, "track", {
                "caps": "text/x-raw(ANY)",
                "track-type": "8",
                "track-id": str(self.track_id),
                "properties":
                    'properties, mixing=(boolean)false;'})
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
            asset_id=None, name=None, asset_duration=None,
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
        if asset_duration is None and type_name == "GESUriClip":
            asset_duration = 100
        self.clip = ElementTree.SubElement(
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
            self.clip.attrib["properties"] = str(properties)
        if metadatas is not None:
            self.clip.attrib["metadatas"] = str(metadatas)
        if name is not None:
            if properties is None:
                properties = SCHEMA.GstStructure("properties")
            properties.set("name", "string", name)
            self.clip.attrib["properties"] = str(properties)
        self.clip_id += 1
        return self.clip

    def add_effect(
            self, effect_name, track_type, track_id,
            type_name=None, properties=None, metadatas=None,
            children_properties=None):
        """Add an effect to the most recent clip."""
        if type_name is None:
            type_name = "GESEffect"
        clip_id = self.clip.get("id")
        effect = ElementTree.SubElement(
            self.clip, "effect", {
                "asset-id": effect_name,
                "clip-id": str(clip_id),
                "type-name": type_name,
                "track-type": str(track_type),
                "track-id": str(track_id)})
        if properties is not None:
            effect.attrib["properties"] = str(properties)
        if metadatas is not None:
            effect.attrib["metadatas"] = str(metadatas)
        if children_properties is not None:
            effect.attrib["children-properties"] = str(
                children_properties)
        return effect

    def get_otio_timeline(self):
        """Return a Timeline using otio's read_from_string method."""
        string = ElementTree.tostring(self.ges, encoding="UTF-8")
        return otio.adapters.read_from_string(string, "xges")


class CustomOtioAssertions:
    """Custom Assertions to perform on otio objects"""

    @staticmethod
    def _typed_name(otio_obj):
        name = otio_obj.name
        if not name:
            name = '""'
        return f"{otio_obj.schema_name()} {name}"

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

    def assertOtioHasAttrPath(self, otio_obj, attr_path):
        """
        Assert that the otio object has the attribute:
            attr_path[0].attr_path[1].---.attr_path[-1]
        and returns the value and an attribute string.
        If an attribute is callable, it will be called (with no
        arguments) before returning.
        If an int is given in the attribute path, it will be treated as
        a list index to call.
        """
        first = True
        attr_str = ""
        val = otio_obj
        for attr_name in attr_path:
            if isinstance(attr_name, int):
                if not hasattr(val, "__getitem__"):
                    raise AssertionError(
                        "{}{} is not a list".format(
                            self._otio_id(otio_obj), attr_str))
                try:
                    val = val[attr_name]
                except Exception as err:
                    raise AssertionError(
                        "{}{}: can't access item {:d}:\n{!s}".format(
                            self._otio_id(otio_obj), attr_str,
                            attr_name, err))
                if first:
                    first = False
                    attr_str += " "
                attr_str += f"[{attr_name:d}]"
            else:
                if not hasattr(val, attr_name):
                    raise AssertionError(
                        "{}{} has no attribute {}".format(
                            self._otio_id(otio_obj), attr_str, attr_name))
                val = getattr(val, attr_name)
                if first:
                    first = False
                    attr_str += " " + attr_name
                else:
                    attr_str += "." + attr_name
            if callable(val):
                val = val()
        return val, attr_str

    def assertOtioAttrPathEqual(self, otio_obj, attr_path, compare):
        """
        Assert that the otio object has the attribute:
            attr_path[0].attr_path[1].---.attr_path[-1]
        equal to 'compare'.
        See assertOtioHasAttrPath for special cases for the attr_path.
        """
        val, attr_str = self.assertOtioHasAttrPath(otio_obj, attr_path)
        if val != compare:
            raise AssertionError(
                "{}{}: {} != {}".format(
                    self._otio_id(otio_obj), attr_str,
                    self._val_str(val), self._val_str(compare)))

    def assertOtioAttrPathEqualList(
            self, otio_obj, list_path, attr_path, compare_list):
        """
        Assert that the otio object has the attribute:
            list_path[0].---.list_path[-1][i]
                .attr_path[0].---.attr_path[-1]
            == compare_list[i]
        See assertOtioHasAttrPath for special cases for the attr_path
        and list_path.
        """
        _list, list_str = self.assertOtioHasAttrPath(otio_obj, list_path)
        try:
            num = len(_list)
        except Exception as err:
            raise AssertionError(
                "{}{} has no len:\n{!s}".format(
                    self._otio_id(otio_obj), list_str, err))
        num_cmp = len(compare_list)
        if num != num_cmp:
            raise AssertionError(
                "{}{} has a length of {:d} != {:d}".format(
                    self._otio_id(otio_obj), list_str, num, num_cmp))
        for index, compare in enumerate(compare_list):
            self.assertOtioAttrPathEqual(
                otio_obj, list_path + [index] + attr_path, compare)

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


class OtioTest:
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
    def no_effects(inst, otio_item):
        """Test that an item has no effects."""
        inst.assertOtioAttrPathEqualList(otio_item, ["effects"], [], [])

    @staticmethod
    def no_markers(inst, otio_item):
        """Test that an item has no markers."""
        inst.assertOtioAttrPathEqualList(otio_item, ["markers"], [], [])

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

    @staticmethod
    def effects(*effect_names):
        """Return a test that the otio_item contains the effects"""
        return lambda inst, otio_item: inst.assertOtioAttrPathEqualList(
            otio_item, ["effects"], ["effect_name"], list(effect_names))

    @staticmethod
    def _test_marker_details(inst, otio_item, marker_details):
        inst.assertOtioAttrPathEqualList(
            otio_item, ["markers"], ["name"],
            [mrk["name"] for mrk in marker_details])
        inst.assertOtioAttrPathEqualList(
            otio_item, ["markers"], ["color"],
            [mrk["color"] for mrk in marker_details])
        inst.assertOtioAttrPathEqualList(
            otio_item, ["markers"], ["marked_range", "start_time"],
            [_rat_tm_from_secs(mrk["start"]) for mrk in marker_details])
        inst.assertOtioAttrPathEqualList(
            otio_item, ["markers"], ["marked_range", "duration"],
            [_rat_tm_from_secs(mrk["duration"]) for mrk in marker_details])

    @classmethod
    def markers(cls, *marker_details):
        """
        Return a test that the otio_item contains the markers specified by
        the marker_details, which are dictionaries with the keys:
            color: (the marker color),
            name: (the name of the marker),
            start: (the start time of the marker in seconds),
            duration: (the range of the marker in seconds)
        """
        return lambda inst, otio_item: cls._test_marker_details(
            inst, otio_item, marker_details)


class OtioTestNode:
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


class OtioTestTree:
    """
    Test an otio object has the correct type structure, and perform
    additional tests along the way."""

    def __init__(self, unittest_inst, base, type_tests=None):
        """
        First argument is a unittest instance which will perform all
        tests.
        'type_test' argument is a dictionary of classes who's values are a
        list of tests to perform whenever a node is found that is an
        instance of that class. These tests should come from OtioTest.
        'base' argument is the base OtioTestNode, where the comparison
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


class CustomXgesAssertions:
    """Custom Assertions to perform on a ges xml object"""

    @staticmethod
    def _xges_id(xml_el):
        xges_id = f"Element <{xml_el.tag}"
        for key, val in xml_el.attrib.items():
            xges_id += f" {key}='{val}'"
        xges_id += " /> "
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

    def assertXgesHasAllAttrs(self, xml_el, *attr_names):
        """
        Assert that the xml element has all given attributes.
        """
        for attr_name in attr_names:
            self.assertXgesHasAttr(xml_el, attr_name)

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
            path += f"[@{key}='{val!s}']"
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
        project = self.assertXgesOneElementAtPath(ges_el, "./project")
        self.assertXgesHasAllAttrs(project, "properties", "metadatas")
        self.assertXgesOneElementAtPath(ges_el, "./project/ressources")
        timeline = self.assertXgesOneElementAtPath(
            ges_el, "./project/timeline")
        self.assertXgesHasAllAttrs(timeline, "properties", "metadatas")

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
        struct = SCHEMA.GstStructure.new_from_str(struct)
        if field_name not in struct.fields:
            raise AssertionError(
                "{}attribute {} does not contain the field {}".format(
                    self._xges_id(xml_el), struct_name, field_name))
        if struct.get_type_name(field_name) != field_type:
            raise AssertionError(
                "{}attribute {}'s field {} is not of the type {}".format(
                    self._xges_id(xml_el), struct_name, field_name,
                    field_type))
        return struct[field_name]

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

    def assertXgesStructureFieldEqual(
            self, xml_el, struct_name, field_name, field_type, compare):
        """
        Assert that a certain xml element structure field is equal to
        'compare'.
        """
        val = self.assertXgesHasInStructure(
            xml_el, struct_name, field_name, field_type)
        # TODO: remove once python2 has ended
        if field_type == "string":
            if type(val) is not str and isinstance(val, str):
                val = val.encode("utf8")
        if isinstance(val, otio.core.SerializableObject):
            equal = val.is_equivalent_to(compare)
        else:
            equal = val == compare
        if not equal:
            raise AssertionError(
                "{}{} {}:\n{!s}\n!=\n{!s}".format(
                    self._xges_id(xml_el), struct_name, field_name,
                    val, compare))

    def assertXgesPropertyEqual(
            self, xml_el, prop_name, prop_type, compare):
        """
        Assert that a certain xml element property is equal to
        'compare'.
        """
        self.assertXgesStructureFieldEqual(
            xml_el, "properties", prop_name, prop_type, compare)

    def assertXgesMetadataEqual(
            self, xml_el, meta_name, meta_type, compare):
        """
        Assert that a certain xml element metadata is equal to
        'compare'.
        """
        self.assertXgesStructureFieldEqual(
            xml_el, "metadatas", meta_name, meta_type, compare)

    def assertXgesStructureEqual(self, xml_el, attr_name, compare):
        """
        Assert that the xml element structure is equal to 'compare'.
        """
        struct = self.assertXgesHasAttr(xml_el, attr_name)
        struct = SCHEMA.GstStructure.new_from_str(struct)
        if not isinstance(compare, SCHEMA.GstStructure):
            compare = SCHEMA.GstStructure.new_from_str(compare)
        if not struct.is_equivalent_to(compare):
            raise AssertionError(
                "{}{}:\n{!r}\n!=\n{!r}".format(
                    self._xges_id(xml_el), attr_name, struct, compare))

    def assertXgesTrackTypes(self, ges_el, *track_types):
        """
        Assert that the ges element contains one track for each given
        track type, and no more.
        Returns the tracks in the same order as the types.
        """
        tracks = []
        for track_type in track_types:
            track = self.assertXgesOneElementAtPathWithAttr(
                ges_el, "./project/timeline/track",
                {"track-type": str(track_type)})
            self.assertXgesHasAllAttrs(
                track, "caps", "track-type", "track-id",
                "properties", "metadatas")
            tracks.append(track)
        self.assertXgesNumElementsAtPath(
            ges_el, "./project/timeline/track", len(track_types))
        return tracks

    def assertXgesNumLayers(self, ges_el, compare):
        """
        Assert that the ges element contains the expected number of
        layers.
        Returns the layers.
        """
        layers = self.assertXgesNumElementsAtPath(
            ges_el, "./project/timeline/layer", compare)
        for layer in layers:
            self.assertXgesHasAllAttrs(layer, "priority")
        return layers

    def assertXgesLayer(self, ges_el, priority):
        return self.assertXgesOneElementAtPathWithAttr(
            ges_el, "./project/timeline/layer",
            {"priority": str(priority)})

    def assertXgesNumClipsAtPath(self, xml_el, path, compare):
        """
        Assert that the xml element contains the expected number of
        clips at the given path.
        Returns the clips.
        """
        clips = self.assertXgesNumElementsAtPath(xml_el, path, compare)
        for clip in clips:
            self.assertXgesHasAllAttrs(
                clip, "id", "asset-id", "type-name", "layer-priority",
                "track-types", "start", "duration", "inpoint", "rate",
                "properties", "metadatas")
        return clips

    def assertXgesNumClips(self, ges_el, compare):
        """
        Assert that the ges element contains the expected number of
        clips.
        Returns the clips.
        """
        return self.assertXgesNumClipsAtPath(
            ges_el, "./project/timeline/layer/clip", compare)

    def assertXgesNumClipsInLayer(self, layer_el, compare):
        """
        Assert that the layer element contains the expected number of
        clips.
        Returns the clips.
        """
        return self.assertXgesNumClipsAtPath(layer_el, "./clip", compare)

    def assertXgesClip(self, ges_el, attrs):
        """
        Assert that the ges element contains only one clip with the
        given attributes.
        Returns the matching clip.
        """
        clip = self.assertXgesOneElementAtPathWithAttr(
            ges_el, "./project/timeline/layer/clip", attrs)
        self.assertXgesHasAllAttrs(
            clip, "id", "asset-id", "type-name", "layer-priority",
            "track-types", "start", "duration", "inpoint", "rate",
            "properties", "metadatas")
        return clip

    def assertXgesAsset(self, ges_el, asset_id, extract_type):
        """
        Assert that the ges element contains only one asset with the
        given id and extract type.
        Returns the matching asset.
        """
        asset = self.assertXgesOneElementAtPathWithAttr(
            ges_el, "./project/ressources/asset",
            {"id": asset_id, "extractable-type-name": extract_type})
        self.assertXgesHasAllAttrs(
            asset, "id", "extractable-type-name", "properties",
            "metadatas")
        return asset

    def assertXgesClipHasAsset(self, ges_el, clip_el):
        """
        Assert that the ges clip has a corresponding asset.
        Returns the asset.
        """
        asset_id = self.assertXgesHasAttr(clip_el, "asset-id")
        extract_type = self.assertXgesHasAttr(clip_el, "type-name")
        return self.assertXgesAsset(ges_el, asset_id, extract_type)

    def assertXgesClipIsSubproject(self, ges_el, clip_el):
        """
        Assert that the ges clip corresponds to a subproject.
        Retruns the subprojects ges element.
        """
        self.assertXgesClipHasAsset(ges_el, clip_el)
        ges_asset = self.assertXgesAsset(
            ges_el, clip_el.get("asset-id"), "GESTimeline")
        sub_ges_el = self.assertXgesOneElementAtPath(ges_asset, "ges")
        self.assertXgesIsGesElement(sub_ges_el)
        return sub_ges_el

    def assertXgesNumClipEffects(self, clip_el, compare):
        """
        Assert that the clip element contains the expected number of
        effects.
        Returns the effects.
        """
        effects = self.assertXgesNumElementsAtPath(
            clip_el, "./effect", compare)
        for effect in effects:
            self.assertXgesHasAllAttrs(
                effect, "asset-id", "clip-id", "type-name",
                "track-type", "track-id", "properties", "metadatas",
                "children-properties")
        return effects

    def assertXgesTimelineMarkerListEqual(self, ges_el, marker_list):
        timeline = self.assertXgesOneElementAtPath(
            ges_el, "./project/timeline")
        self.assertXgesMetadataEqual(
            timeline, "markers", "GESMarkerList", marker_list)


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
        ids = []
        for priority, expect_num, expect_track_types in zip(
                range(5), [1, 1, 2, 3, 1], [6, 2, 4, 4, 2]):
            layer = self.assertXgesLayer(ges_el, priority)
            clips = self.assertXgesNumClipsInLayer(layer, expect_num)
            for clip in clips:
                ids.append(clip.get("id"))
                self.assertXgesAttrEqual(
                    clip, "track-types", expect_track_types)
                self.assertXgesAttrEqual(
                    clip, "layer-priority", priority)
                if clip.get("type-name") == "GESUriClip":
                    self.assertXgesClipHasAsset(ges_el, clip)
        # check that ids are unique
        for clip_id in ids:
            self.assertIsNotNone(clip_id)
            self.assertEqual(ids.count(clip_id), 1)

    def test_unsupported_track_type(self):
        # want to test that a project with an unsupported track type
        # will still give results for the supported tracks
        xges_el = XgesElement()
        xges_el.add_audio_track()
        # text is unsupported
        xges_el.add_text_track()
        xges_el.add_video_track()
        xges_el.add_layer()
        xges_el.add_clip(0, 2, 0, "GESUriClip", 14, name="mixed")
        xges_el.add_clip(1, 1, 0, "GESTransitionClip", 6)
        xges_el.add_clip(1, 2, 0, "GESUriClip", 6, name="audio-video")
        xges_el.add_clip(3, 2, 0, "GESUriClip", 8, name="text")

        if str is not bytes:
            # TODO: remove str is not bytes test when python2 ends
            # Python2 does not have assertWarns
            # warning because unsupported text track type
            with self.assertWarns(UserWarning):
                timeline = xges_el.get_otio_timeline()
        else:
            timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(Stack, children=[
                OtioTestNode(
                    Track, tests=[OtioTest.is_video], children=[
                        OtioTestNode(Clip), OtioTestNode(Transition),
                        OtioTestNode(Clip)]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_audio], children=[
                        OtioTestNode(Clip), OtioTestNode(Transition),
                        OtioTestNode(Clip)])
            ]))
        test_tree.test_compare(timeline.tracks)

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
        xges_el.add_video_track()
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

    def test_clip_names_unique(self):
        xges_el = XgesElement()
        xges_el.add_audio_track()
        xges_el.add_layer()
        xges_el.add_clip(0, 1, 0, "GESUriClip", 2, name="clip2")
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, base=OtioTestNode(Stack, children=[
                OtioTestNode(Track, children=[
                    OtioTestNode(
                        Clip, tests=[OtioTest.name("clip2")])
                ])
            ]))
        test_tree.test_compare(timeline.tracks)
        timeline.tracks[0].append(_make_clip(name="clip2"))
        timeline.tracks[0].append(_make_clip(name="clip2"))
        ges_el = self._get_xges_from_otio_timeline(timeline)
        clips = self.assertXgesNumClips(ges_el, 3)
        clip_names = []
        for clip in clips:
            name = self.assertXgesHasProperty(clip, "name", "string")
            self.assertNotIn(name, clip_names)
            clip_names.append(name)

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

    def test_effects(self):
        xges_el = XgesElement()
        xges_el.add_audio_track()
        xges_el.add_video_track()
        xges_el.add_layer()
        xges_el.add_clip(0, 1, 0, "GESUriClip", 6)

        video_effect_attribs = [{
            "asset-id": "agingtv",
            "track-type": 4,
            "track-id": 0,
            "children-properties": SCHEMA.GstStructure.new_from_str(
                "properties, GstAgingTV::color-aging=(boolean)true, "
                "GstAgingTV::dusts=(boolean)true, "
                "GstAgingTV::pits=(boolean)true, "
                "GstBaseTransform::qos=(boolean)true, "
                "GstAgingTV::scratch-lines=(uint)7;")}, {
            "asset-id": "videobalance",
            "track-type": 4,
            "track-id": 0,
            "children-properties": SCHEMA.GstStructure.new_from_str(
                "properties, GstVideoBalance::brightness=(double)0, "
                "GstVideoBalance::contrast=(double)0.5, "
                "GstVideoBalance::hue=(double)0, "
                "GstBaseTransform::qos=(boolean)true, "
                "GstVideoBalance::saturation=(double)1;")}]
        audio_effect_attribs = [{
            "asset-id": "audiokaraoke",
            "track-type": 2,
            "track-id": 1,
            "children-properties": SCHEMA.GstStructure.new_from_str(
                "properties, GstAudioKaraoke::filter-band=(float)220, "
                "GstAudioKaraoke::filter-width=(float)100, "
                "GstAudioKaraoke::level=(float)1, "
                "GstAudioKaraoke::mono-level=(float)1, "
                "GstBaseTransform::qos=(boolean)false;")}]
        effect_attribs = [
            video_effect_attribs[0], audio_effect_attribs[0],
            video_effect_attribs[1]]
        for attrs in effect_attribs:
            xges_el.add_effect(
                attrs["asset-id"], attrs["track-type"],
                attrs["track-id"],
                children_properties=attrs["children-properties"])
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, type_tests={
                Stack: [OtioTest.no_effects],
                Track: [OtioTest.no_effects]},
            base=OtioTestNode(Stack, children=[
                OtioTestNode(
                    Track, tests=[OtioTest.is_video], children=[
                        OtioTestNode(
                            Clip, tests=[OtioTest.effects(
                                "agingtv", "videobalance")])
                    ]),
                OtioTestNode(
                    Track, tests=[OtioTest.is_audio], children=[
                        OtioTestNode(
                            Clip, tests=[OtioTest.effects(
                                "audiokaraoke")])
                    ])
            ]))
        test_tree.test_compare(timeline.tracks)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        tracks = self.assertXgesTrackTypes(ges_el, 2, 4)
        audio_track = tracks[0]
        video_track = tracks[1]
        layers = self.assertXgesNumLayers(ges_el, 2)
        # expect 2 layers since re-merging of the tracks will be
        # prevented by the different effects for different track types
        clip = self.assertXgesNumClipsInLayer(layers[0], 1)[0]
        audio_effects = self.assertXgesNumClipEffects(
            clip, len(audio_effect_attribs))
        for effect, attrs in zip(audio_effects, audio_effect_attribs):
            self.assertXgesAttrEqual(
                effect, "asset-id", attrs["asset-id"])
            self.assertXgesAttrEqual(effect, "track-type", 2)
            self.assertXgesAttrEqual(
                effect, "track-id", audio_track.get("track-id"))
            self.assertXgesStructureEqual(
                effect, "children-properties",
                attrs["children-properties"])
        clip = self.assertXgesNumClipsInLayer(layers[1], 1)[0]
        video_effects = self.assertXgesNumClipEffects(
            clip, len(video_effect_attribs))
        for effect, attrs in zip(video_effects, video_effect_attribs):
            self.assertXgesAttrEqual(
                effect, "asset-id", attrs["asset-id"])
            self.assertXgesAttrEqual(effect, "track-type", 4)
            self.assertXgesAttrEqual(
                effect, "track-id", video_track.get("track-id"))
            self.assertXgesStructureEqual(
                effect, "children-properties",
                attrs["children-properties"])

    def test_track_effects(self):
        timeline = Timeline()
        effect_names = ["agingtv", "videobalance"]
        track = Track()
        track.kind = TrackKind.Video
        timeline.tracks.append(track)
        for name in effect_names:
            track.effects.append(Effect(effect_name=name))
        track.append(Gap(source_range=_tm_range_from_secs(0, 3)))
        track.append(_make_clip(start=2, duration=5))
        track.append(_make_clip(start=0, duration=4))

        if str is not bytes:
            # TODO: remove str is not bytes test when python2 ends
            # Python2 does not have assertWarns
            # TODO: warning is for the fact that we do not yet have a
            # smart way to convert effect names into bin-descriptions
            # Should be removed once this is sorted
            with self.assertWarns(UserWarning):
                ges_el = self._get_xges_from_otio_timeline(timeline)
        else:
            ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el, 4)
        layer = self.assertXgesNumLayers(ges_el, 1)[0]
        self.assertXgesNumClipsInLayer(layer, 4)
        ids = []
        ids.append(self.assertXgesClip(
            ges_el, {
                "start": 3, "duration": 5, "inpoint": 2,
                "type-name": "GESUriClip", "track-types": 4}).get("id"))
        ids.append(self.assertXgesClip(
            ges_el, {
                "start": 8, "duration": 4, "inpoint": 0,
                "type-name": "GESUriClip", "track-types": 4}).get("id"))
        ids.append(self.assertXgesClip(
            ges_el, {
                "start": 3, "duration": 9, "inpoint": 0,
                "asset-id": effect_names[0],
                "type-name": "GESEffectClip", "track-types": 4}).get("id"))
        ids.append(self.assertXgesClip(
            ges_el, {
                "start": 3, "duration": 9, "inpoint": 0,
                "asset-id": effect_names[1],
                "type-name": "GESEffectClip", "track-types": 4}).get("id"))
        # check that ids are unique
        for clip_id in ids:
            self.assertIsNotNone(clip_id)
            self.assertEqual(ids.count(clip_id), 1)

    def test_markers(self):
        marker_list = SCHEMA.GESMarkerList(
            _make_ges_marker(23, MarkerColor.RED),
            _make_ges_marker(30),
            _make_ges_marker(
                77, MarkerColor.BLUE, UTF8_NAME, SCHEMA.GstStructure(
                    "metadatas", {"Int": ("int", 30)})))
        # Note, the second marker is not colored, so we don't expect a
        # corresponding otio marker
        marker_list[2].set_color_from_otio_color(MarkerColor.BLUE)
        xges_el = XgesElement(marker_list=marker_list)
        xges_el.add_audio_track()
        xges_el.add_layer()
        xges_el.add_clip(1, 1, 0, "GESUriClip", 2)
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, type_tests={
                Track: [OtioTest.no_markers],
                Clip: [OtioTest.no_markers],
                Gap: [OtioTest.no_markers]},
            base=OtioTestNode(
                Stack, tests=[OtioTest.markers({
                    "name": "", "color": MarkerColor.RED,
                    "start": 23, "duration": 0}, {
                    "name": UTF8_NAME, "color": MarkerColor.BLUE,
                    "start": 77, "duration": 0})],
                children=[
                    OtioTestNode(Track, children=[
                        OtioTestNode(Gap),
                        OtioTestNode(Clip)
                    ])
                ]))
        test_tree.test_compare(timeline.tracks)
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertXgesTrackTypes(ges_el, 2)
        layer = self.assertXgesNumLayers(ges_el, 1)[0]
        self.assertXgesNumClipsInLayer(layer, 1)[0]
        self.assertXgesTimelineMarkerListEqual(ges_el, marker_list)

    def _add_test_properties_and_metadatas(self, el):
        el.attrib["properties"] = str(SCHEMA.GstStructure(
            "properties", {
                "field2": ("int", 5),
                "field1": ("string", UTF8_NAME)}))
        el.attrib["metadatas"] = str(SCHEMA.GstStructure(
            "metadatas", {
                "field3": ("int", 6),
                "field4": ("boolean", True)}))

    def _has_test_properties_and_metadatas(self, el):
        self.assertXgesPropertyEqual(el, "field1", "string", UTF8_NAME)
        self.assertXgesPropertyEqual(el, "field2", "int", 5)
        self.assertXgesMetadataEqual(el, "field3", "int", 6)
        self.assertXgesMetadataEqual(el, "field4", "boolean", True)

    def test_clip_properties_and_metadatas(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        xges_el.add_layer()
        clip = xges_el.add_clip(0, 1, 0, "GESUriClip", 4)
        self._add_test_properties_and_metadatas(clip)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesClip(ges_el, {}))

    def test_transition_properties_and_metadatas(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        xges_el.add_layer()
        xges_el.add_clip(0, 2, 0, "GESUriClip", 4)
        transition = xges_el.add_clip(1, 1, 0, "GESTransitionClip", 4)
        self._add_test_properties_and_metadatas(transition)
        xges_el.add_clip(1, 2, 0, "GESUriClip", 4)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(self.assertXgesClip(
            ges_el, {"type-name": "GESTransitionClip"}))

    def test_project_properties_and_metadatas(self):
        xges_el = XgesElement()
        self._add_test_properties_and_metadatas(xges_el.project)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesOneElementAtPath(ges_el, "./project"))

    def test_timeline_properties_and_metadatas(self):
        xges_el = XgesElement()
        self._add_test_properties_and_metadatas(xges_el.timeline)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesOneElementAtPath(
                ges_el, "./project/timeline"))

    def test_layer_properties_and_metadatas(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        layer = xges_el.add_layer()
        self._add_test_properties_and_metadatas(layer)
        # NOTE: need a non-empty layer
        xges_el.add_clip(0, 2, 0, "GESUriClip", 4)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesNumLayers(ges_el, 1)[0])

    def test_uri_clip_asset_properties_and_metadatas(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        xges_el.add_layer()
        asset_id = "file:///example-file"
        asset = xges_el.add_asset(asset_id, "GESUriClip")
        self._add_test_properties_and_metadatas(asset)
        xges_el.add_clip(0, 1, 0, "GESUriClip", 4, asset_id)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesAsset(ges_el, asset_id, "GESUriClip"))

    def _subproject_asset_props_and_metas_for_type(self, extract_type):
        xges_el = self._make_nested_project()
        asset = xges_el.ressources.find(
            f"./asset[@extractable-type-name='{extract_type}']")
        self.assertIsNotNone(asset)
        asset_id = asset.get("id")
        self.assertIsNotNone(asset_id)
        self._add_test_properties_and_metadatas(asset)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesAsset(ges_el, asset_id, extract_type))

    def test_subproject_asset_properties_and_metadatas(self):
        self._subproject_asset_props_and_metas_for_type("GESUriClip")
        self._subproject_asset_props_and_metas_for_type("GESTimeline")

    def test_track_properties_and_metadatas(self):
        xges_el = XgesElement()
        track = xges_el.add_audio_track()
        self._add_test_properties_and_metadatas(track)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        self._has_test_properties_and_metadatas(
            self.assertXgesOneElementAtPath(
                ges_el, "./project/timeline/track"))

    def test_effect_properties_and_metadatas(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        xges_el.add_layer()
        xges_el.add_clip(0, 1, 0, "GESUriClip", 4)
        effect = xges_el.add_effect("videobalance", 4, 0)
        self._add_test_properties_and_metadatas(effect)
        timeline = xges_el.get_otio_timeline()
        ges_el = self._get_xges_from_otio_timeline(timeline)
        clip = self.assertXgesClip(ges_el, {})
        self._has_test_properties_and_metadatas(
            self.assertXgesNumClipEffects(clip, 1)[0])

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

    def _make_nested_project(self):
        xges_el = XgesElement()
        xges_el.add_video_track()
        xges_el.add_audio_track()
        xges_el.add_layer()
        asset = xges_el.add_asset("file:///example.xges", "GESTimeline")
        xges_el.add_clip(
            70, 20, 10, "GESUriClip", 6, "file:///example.xges")
        sub_xges_el = XgesElement()
        sub_xges_el.add_video_track()
        sub_xges_el.add_layer()
        sub_xges_el.add_clip(50, 40, 30, "GESUriClip", 6)
        asset.append(sub_xges_el.ges)
        return xges_el

    def test_nested_projects_and_stacks(self):
        xges_el = self._make_nested_project()
        timeline = xges_el.get_otio_timeline()
        test_tree = OtioTestTree(
            self, type_tests={
                Track: [OtioTest.none_source],
                Clip: [OtioTest.has_ex_ref]},
            base=OtioTestNode(
                Stack, tests=[OtioTest.none_source], children=[
                    OtioTestNode(
                        Track, tests=[OtioTest.is_video],
                        children=[
                            OtioTestNode(
                                Gap,
                                tests=[OtioTest.duration(70)]),
                            OtioTestNode(
                                Stack,
                                tests=[OtioTest.range(10, 20)],
                                children=[
                                    OtioTestNode(
                                        Track,
                                        tests=[OtioTest.is_video],
                                        children=[
                                            OtioTestNode(Gap, tests=[
                                                OtioTest.duration(50)]),
                                            OtioTestNode(Clip, tests=[
                                                OtioTest.range(30, 40)])
                                        ]),
                                    OtioTestNode(
                                        Track,
                                        tests=[OtioTest.is_audio],
                                        children=[
                                            OtioTestNode(Gap, tests=[
                                                OtioTest.duration(50)]),
                                            OtioTestNode(Clip, tests=[
                                                OtioTest.range(30, 40)])
                                        ])
                                ])
                        ]),
                    OtioTestNode(
                        Track, tests=[OtioTest.is_audio],
                        children=[
                            OtioTestNode(
                                Gap,
                                tests=[OtioTest.duration(70)]),
                            OtioTestNode(
                                Stack,
                                tests=[OtioTest.range(10, 20)],
                                children=[
                                    OtioTestNode(
                                        Track,
                                        tests=[OtioTest.is_video],
                                        children=[
                                            OtioTestNode(Gap, tests=[
                                                OtioTest.duration(50)]),
                                            OtioTestNode(Clip, tests=[
                                                OtioTest.range(30, 40)])
                                        ]),
                                    OtioTestNode(
                                        Track,
                                        tests=[OtioTest.is_audio],
                                        children=[
                                            OtioTestNode(Gap, tests=[
                                                OtioTest.duration(50)]),
                                            OtioTestNode(Clip, tests=[
                                                OtioTest.range(30, 40)])
                                        ])
                                ])
                        ])
                ]))
        test_tree.test_compare(timeline.tracks)
        self._xges_has_nested_clip(timeline, 70, 20, 10, 6, 50, 40, 30, 6)

    def test_nested_projects_and_stacks_edited(self):
        xges_el = self._make_nested_project()
        timeline = xges_el.get_otio_timeline()
        # Previous test will assert the correct structure

        # Change the gap before the video sub-stack to 30 seconds
        timeline.tracks[0][0].source_range = _tm_range_from_secs(0, 30)

        # The sub-project should be the same, but we now have two
        # different clips referencing the same sub-project

        # Now have an audio clip, with the new start time
        first_top_clip, _ = self._xges_has_nested_clip(
            timeline, 30, 20, 10, 4, 50, 40, 30, 6)
        # And the video clip, with the old start time
        second_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 20, 10, 2, 50, 40, 30, 6)
        # They both reference the same project
        first_id = self.assertXgesHasAttr(first_top_clip, "asset-id")
        self.assertXgesAttrEqual(second_top_clip, "asset-id", first_id)

        # Restore the timing
        timeline.tracks[0][0].source_range = _tm_range_from_secs(0, 70)
        # Change the video sub-stack to reference an earlier point
        timeline.tracks[0][1].source_range = _tm_range_from_secs(0, 10)

        # The sub-project should be the same, but we now have two
        # different clips referencing the same sub-project

        # Now have a video clip, with the new duration and inpoint
        first_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 10, 0, 4, 50, 40, 30, 6)
        # And an audio clip, with the old start time
        second_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 20, 10, 2, 50, 40, 30, 6)
        # They both reference the same project
        first_id = self.assertXgesHasAttr(first_top_clip, "asset-id")
        self.assertXgesAttrEqual(second_top_clip, "asset-id", first_id)

        # Restore the timing
        timeline.tracks[0][1].source_range = _tm_range_from_secs(10, 20)
        # Change the content of the video sub-stack by reducing the gap
        timeline.tracks[0][1][0][0].source_range = _tm_range_from_secs(0, 20)
        timeline.tracks[0][1][1][0].source_range = _tm_range_from_secs(0, 20)

        # The sub-project should now be different, so we should have two
        # separate assets
        first_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 20, 10, 4, 20, 40, 30, 6)
        second_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 20, 10, 2, 50, 40, 30, 6)
        # They now reference different projects
        first_id = self.assertXgesHasAttr(first_top_clip, "asset-id")
        second_id = self.assertXgesHasAttr(second_top_clip, "asset-id")
        self.assertNotEqual(first_id, second_id)

        # Restore the stack's timing
        timeline.tracks[0][1][0][0].source_range = _tm_range_from_secs(0, 50)
        timeline.tracks[0][1][1][0].source_range = _tm_range_from_secs(0, 50)
        # Change the content of the video sub-stack by referencing
        # different times for its clip
        timeline.tracks[0][1][0][1].source_range = _tm_range_from_secs(10, 60)
        timeline.tracks[0][1][1][1].source_range = _tm_range_from_secs(10, 60)

        # The sub-project should now be different, so we should have two
        # separate assets
        first_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 20, 10, 4, 50, 60, 10, 6)
        second_top_clip, _ = self._xges_has_nested_clip(
            timeline, 70, 20, 10, 2, 50, 40, 30, 6)
        # They now reference different projects
        first_id = self.assertXgesHasAttr(first_top_clip, "asset-id")
        second_id = self.assertXgesHasAttr(second_top_clip, "asset-id")
        self.assertNotEqual(first_id, second_id)

    def _xges_has_nested_clip(
            self, timeline,
            top_start, top_duration, top_inpoint, top_track_types,
            orig_start, orig_duration, orig_inpoint, orig_track_types,
            effect_names=None):
        """Returns the top clip and nested clip"""
        if effect_names is None:
            effect_names = []

        if effect_names and str is not bytes:
            # TODO: remove the str is not bytes check once python2 has
            # ended. Python2 does not have assertWarns
            # TODO: warning is for the fact that we do not yet have a
            # smart way to convert effect names into bin-descriptions
            # Should be removed once this is sorted
            with self.assertWarns(UserWarning):
                ges_el = self._get_xges_from_otio_timeline(timeline)
        else:
            ges_el = self._get_xges_from_otio_timeline(timeline)
        if orig_track_types == 6:
            self.assertXgesTrackTypes(ges_el, 2, 4)
        else:
            self.assertXgesTrackTypes(ges_el, top_track_types)
        top_clip = self.assertXgesClip(
            ges_el, {
                "start": top_start, "duration": top_duration,
                "inpoint": top_inpoint, "type-name": "GESUriClip",
                "track-types": top_track_types})
        effects = self.assertXgesNumClipEffects(
            top_clip, len(effect_names))
        for effect, name in zip(effects, effect_names):
            self.assertXgesAttrEqual(effect, "asset-id", name)

        ges_el = self.assertXgesClipIsSubproject(ges_el, top_clip)
        self.assertXgesNumClips(ges_el, 1)
        orig_clip = self.assertXgesClip(
            ges_el, {
                "start": orig_start, "duration": orig_duration,
                "inpoint": orig_inpoint, "type-name": "GESUriClip",
                "track-types": orig_track_types})
        self.assertXgesNumClipEffects(orig_clip, 0)
        self.assertXgesClipHasAsset(ges_el, orig_clip)
        return top_clip, orig_clip

    def test_effect_stack(self):
        timeline = Timeline()
        effect_names = ["agingtv", "videobalance"]
        for name in effect_names:
            timeline.tracks.effects.append(Effect(effect_name=name))
        track = Track()
        track.kind = TrackKind.Video
        timeline.tracks.append(track)
        track.append(_make_clip(start=20, duration=50))
        self._xges_has_nested_clip(
            timeline, 0, 50, 0, 4, 0, 50, 20, 4, effect_names)

    def test_source_range_stack(self):
        timeline = Timeline()
        track = Track()
        track.kind = TrackKind.Video
        timeline.tracks.append(track)
        track.append(_make_clip(start=20, duration=50))
        timeline.tracks.source_range = _tm_range_from_secs(10, 30)
        self._xges_has_nested_clip(timeline, 0, 30, 10, 4, 0, 50, 20, 4)

    def test_source_range_track(self):
        timeline = Timeline()
        track = Track()
        track.kind = TrackKind.Video
        timeline.tracks.append(track)
        track.append(_make_clip(start=20, duration=50))
        track.source_range = _tm_range_from_secs(10, 30)
        self._xges_has_nested_clip(timeline, 0, 30, 10, 4, 0, 50, 20, 4)

    def test_double_track(self):
        timeline = Timeline()
        track1 = Track()
        track1.kind = TrackKind.Video
        timeline.tracks.append(track1)
        track2 = Track()
        track2.kind = TrackKind.Video
        track1.append(_make_clip(start=40, duration=90))
        track1.append(track2)
        track2.append(_make_clip(start=20, duration=50))
        self._xges_has_nested_clip(timeline, 90, 50, 0, 4, 0, 50, 20, 4)

    def test_double_stack(self):
        timeline = Timeline()
        stack = Stack()
        stack.source_range = _tm_range_from_secs(10, 30)
        track = Track()
        track.kind = TrackKind.Video
        track.append(_make_clip(start=20, duration=50))
        stack.append(track)
        track = Track()
        track.kind = TrackKind.Video
        track.append(_make_clip())
        timeline.tracks.append(track)
        timeline.tracks.append(stack)
        self._xges_has_nested_clip(timeline, 0, 30, 10, 4, 0, 50, 20, 4)

    def test_track_merge(self):
        timeline = Timeline()
        for kind in [
                TrackKind.Audio,
                TrackKind.Video]:
            track = Track()
            track.kind = kind
            track.metadata["example-non-xges"] = str(kind)
            track.metadata["XGES"] = {
                "data": SCHEMA.GstStructure.new_from_str(
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

    def test_markers_from_otio(self):
        timeline = Timeline()
        _add_marker(timeline.tracks, "top marker", MarkerColor.PINK, 1, 0)
        _add_marker(timeline.tracks, "", MarkerColor.ORANGE, 5, 3)
        # duplicates are to be ignored
        _add_marker(timeline.tracks, "top marker", MarkerColor.PINK, 1, 0)
        _add_marker(timeline.tracks, "", MarkerColor.ORANGE, 5, 3)
        track = Track()
        timeline.tracks.append(track)
        _add_marker(track, "track marker", MarkerColor.PURPLE, 2, 2)
        _add_marker(track, "", MarkerColor.BLACK, 2, 0)
        clip = _make_clip(duration=4)
        track.append(clip)
        _add_marker(clip, "clip1", MarkerColor.YELLOW, 1, 0)
        gap = Gap(source_range=_tm_range_from_secs(0, 2))
        track.append(gap)
        _add_marker(gap, "gap", MarkerColor.WHITE, 1, 0)
        clip = _make_clip(duration=5)
        track.append(clip)
        _add_marker(clip, "clip2", MarkerColor.ORANGE, 2, 0)
        _add_marker(clip, "", MarkerColor.GREEN, 1, 2)

        stack = Stack()
        track.append(stack)
        _add_marker(stack, "sub-stack", MarkerColor.RED, 1, 0)
        track = Track()
        stack.append(track)
        _add_marker(track, "sub-track", MarkerColor.BLUE, 2, 0)
        track.append(_make_clip(duration=3))
        clip = _make_clip(duration=2)
        track.append(clip)
        _add_marker(clip, "sub-clip", MarkerColor.MAGENTA, 1, 1)

        ges_el = self._get_xges_from_otio_timeline(timeline)
        layer = self.assertXgesNumLayers(ges_el, 1)[0]
        clips = self.assertXgesNumClipsInLayer(layer, 3)
        self.assertXgesTimelineMarkerListEqual(
            ges_el, SCHEMA.GESMarkerList(
                _make_ges_marker(1, MarkerColor.PINK, "top marker"),
                _make_ges_marker(5, MarkerColor.ORANGE),
                _make_ges_marker(8, MarkerColor.ORANGE),
                # 8 is the end of the marker range
                _make_ges_marker(2, MarkerColor.PURPLE, "track marker"),
                _make_ges_marker(4, MarkerColor.PURPLE, "track marker"),
                _make_ges_marker(2, MarkerColor.BLACK),
                _make_ges_marker(1, MarkerColor.YELLOW, "clip1"),
                _make_ges_marker(5, MarkerColor.WHITE, "gap"),
                # 5 = 4 + 1, since we want the position relative to the
                # timeline, rather than the gap
                _make_ges_marker(8, MarkerColor.ORANGE, "clip2"),
                # Note, this matches the color and position of another
                # marker, but we want both since this has a different
                # comment
                _make_ges_marker(7, MarkerColor.GREEN),
                _make_ges_marker(9, MarkerColor.GREEN)))

        sub_ges_el = self.assertXgesClipIsSubproject(ges_el, clips[2])
        layer = self.assertXgesNumLayers(sub_ges_el, 1)[0]
        clips = self.assertXgesNumClipsInLayer(layer, 2)
        self.assertXgesTimelineMarkerListEqual(
            sub_ges_el, SCHEMA.GESMarkerList(
                _make_ges_marker(1, MarkerColor.RED, "sub-stack"),
                _make_ges_marker(2, MarkerColor.BLUE, "sub-track"),
                _make_ges_marker(4, MarkerColor.MAGENTA, "sub-clip"),
                _make_ges_marker(5, MarkerColor.MAGENTA, "sub-clip")))

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
        self.assertXgesStructureEqual(track, "properties", props_before)

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

    def test_GstCaps_parsing(self):
        caps = SCHEMA.GstCaps.new_from_str("ANY")
        self.assertTrue(caps.is_any())
        self.assertEqual(len(caps), 0)
        caps = SCHEMA.GstCaps.new_from_str(
            "First(  memory:SystemMemory,   other:az09AZ) ,  "
            "field1 = ( int  )  5  ,field2=(string){};"
            "Second, fieldA=(fraction)3/67, fieldB=(boolean)true;  "
            "Third(ANY), fieldX=(int)-2".format(
                SCHEMA.GstStructure.serialize_string(UTF8_NAME)))
        self.assertFalse(caps.is_any())
        self.assertEqual(len(caps), 3)
        struct = caps[0]
        features = caps.get_features(0)
        self.assertEqual(features.is_any, False)
        self.assertEqual(len(features), 2)
        self.assertEqual(features[0], "memory:SystemMemory")
        self.assertEqual(features[1], "other:az09AZ")
        self.assertEqual(struct.name, "First")
        self.assertEqual(struct["field1"], 5)
        self.assertEqual(struct["field2"], UTF8_NAME)
        struct = caps[1]
        features = caps.get_features(1)
        self.assertEqual(features.is_any, False)
        self.assertEqual(len(features), 0)
        self.assertEqual(struct.name, "Second")
        self.assertEqual(struct["fieldA"], "3/67")
        self.assertEqual(struct["fieldB"], True)
        struct = caps[2]
        features = caps.get_features(2)
        self.assertEqual(features.is_any, True)
        self.assertEqual(len(features), 0)
        self.assertEqual(struct.name, "Third")
        self.assertEqual(struct["fieldX"], -2)

    def test_GstCaps_to_str(self):
        caps_list = [
            {"caps": SCHEMA.GstCaps.new_any(), "str": "ANY"},
            {
                "caps": SCHEMA.GstCaps(
                    SCHEMA.GstStructure("video/x-raw"),
                    SCHEMA.GstCapsFeatures.new_any()),
                "str": "video/x-raw(ANY)"},
            {
                "caps": SCHEMA.GstCaps(
                    SCHEMA.GstStructure(
                        "First", {"field1": ("string", UTF8_NAME)}),
                    SCHEMA.GstCapsFeatures(
                        "memory:SystemMemory", "other:az09AZ"),
                    SCHEMA.GstStructure(
                        "Second", {"fieldA": ("boolean", True)}),
                    None,
                    SCHEMA.GstStructure("Third", {"fieldX": ("int", -2)}),
                    SCHEMA.GstCapsFeatures.new_any()),
                "str":
                    "First(memory:SystemMemory, other:az09AZ), "
                    "field1=(string){}; "
                    "Second, fieldA=(boolean)true; "
                    "Third(ANY), fieldX=(int)-2".format(
                        SCHEMA.GstStructure.serialize_string(UTF8_NAME))}]
        for caps in caps_list:
            string = str(caps["caps"])
            self.assertEqual(string, caps["str"])
            self.assertTrue(caps["caps"].is_equivalent_to(
                SCHEMA.GstCaps.new_from_str(string)))

    def test_empty_GstCaps(self):
        caps = SCHEMA.GstCaps()
        self.assertEqual(len(caps), 0)
        self.assertFalse(caps.is_any())
        self.assertEqual(str(caps), "EMPTY")
        caps = SCHEMA.GstCaps.new_from_str("")
        self.assertEqual(len(caps), 0)
        self.assertFalse(caps.is_any())
        caps = SCHEMA.GstCaps.new_from_str("EMPTY")
        self.assertEqual(len(caps), 0)

    def test_GstCapsFeatures_parsing(self):
        features = SCHEMA.GstCapsFeatures.new_from_str("ANY")
        self.assertEqual(features.is_any, True)
        self.assertEqual(len(features), 0)
        features = SCHEMA.GstCapsFeatures.new_from_str(
            "  memory:SystemMemory,   other:az09AZ")
        self.assertEqual(features.is_any, False)
        self.assertEqual(len(features), 2)
        self.assertEqual(features[0], "memory:SystemMemory")
        self.assertEqual(features[1], "other:az09AZ")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstCapsFeatures.new_from_str("ANY ")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstCapsFeatures.new_from_str("memory")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstCapsFeatures.new_from_str("memory:")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstCapsFeatures.new_from_str("memory:0")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstCapsFeatures.new_from_str("mem0:a")

    def test_GESMarker_colors(self):
        marker = SCHEMA.GESMarker(20)
        self.assertEqual(marker.position, 20)
        self.assertFalse(marker.is_colored())
        argb = 0x850fe409
        marker.set_color_from_argb(argb)
        self.assertTrue(marker.is_colored())
        self.assertEqual(marker.get_argb_color(), argb)
        marker = SCHEMA.GESMarker(20)
        with self.assertRaises(otio.exceptions.OTIOError):
            marker.set_color_from_argb(-1)
        with self.assertRaises(otio.exceptions.OTIOError):
            # too big
            marker.set_color_from_argb(0xffffffff + 1)

    def test_GESMarker_color_to_otio_color(self):
        marker = SCHEMA.GESMarker(20)
        for otio_color in [col for col in dir(MarkerColor)
                           if col.isupper()]:
            # should catch if otio adds a new color
            marker.set_color_from_otio_color(otio_color)
            self.assertTrue(marker.is_colored())
            nearest_otio = marker.get_nearest_otio_color()
            self.assertEqual(otio_color, nearest_otio)

    def test_GESMarkerList_ordering(self):
        marker_list = SCHEMA.GESMarkerList()
        marker_list.add(SCHEMA.GESMarker(224))
        marker_list.add(SCHEMA.GESMarker(226))
        marker_list.add(SCHEMA.GESMarker(223))
        marker_list.add(SCHEMA.GESMarker(224))
        marker_list.add(SCHEMA.GESMarker(225))
        self.assertEqual(len(marker_list), 5)
        self.assertEqual(marker_list[0].position, 223)
        self.assertEqual(marker_list[1].position, 224)
        self.assertEqual(marker_list[2].position, 224)
        self.assertEqual(marker_list[3].position, 225)
        self.assertEqual(marker_list[4].position, 226)

    def test_GstCapsFeatures_to_str(self):
        features = SCHEMA.GstCapsFeatures.new_any()
        string = str(features)
        self.assertEqual(string, "ANY")
        self.assertTrue(features.is_equivalent_to(
            SCHEMA.GstCapsFeatures.new_from_str(string)))
        features = SCHEMA.GstCapsFeatures(
            "memory:SystemMemory", "other:az09AZ")
        string = str(features)
        self.assertEqual(
            string, "memory:SystemMemory, other:az09AZ")
        self.assertTrue(features.is_equivalent_to(
            SCHEMA.GstCapsFeatures.new_from_str(string)))

    def test_serialize_string(self):
        serialize = SCHEMA.GstStructure.serialize_string(UTF8_NAME)
        deserialize = SCHEMA.GstStructure.deserialize_string(serialize)
        self.assertEqual(deserialize, UTF8_NAME)

    def test_GstStructure_parsing(self):
        struct = SCHEMA.GstStructure.new_from_str(
            " properties  , String-1 = ( string ) test , "
            "String-2=(string)\"test\", String-3= (  string) {}  , "
            "Int  =(int) -5  , Uint =(uint) 5 , Float-1=(float)0.5, "
            "Float-2= (float  ) 2, Boolean-1 =(boolean  ) true, "
            "Boolean-2=(boolean)No, Boolean-3=( boolean) 0  ,   "
            "Fraction=(fraction) 2/5, Structure = (structure) "
            "\"Name\\,\\ val\\=\\(string\\)\\\"test\\\\\\ test\\\"\\;\", "
            "Caps =(GstCaps)\"Struct1\\(memory:SystemMemory\\)\\,\\ "
            "val\\=\\(string\\)\\\"test\\\\\\ test\\\"\","
            "markers=(GESMarkerList)\"marker-times, position=(guint64)"
            "2748; metadatas, val=(string)\\\"test\\\\ test\\\"; "
            "marker-times, position=(guint64)1032; "
            "metadatas, val=(int)-5\";"
            "hidden!!!".format(
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
        self.assertTrue(struct["Structure"].is_equivalent_to(
            SCHEMA.GstStructure(
                "Name", {"val": ("string", "test test")})))
        self.assertTrue(struct["Caps"].is_equivalent_to(
            SCHEMA.GstCaps(
                SCHEMA.GstStructure(
                    "Struct1", {"val": ("string", "test test")}),
                SCHEMA.GstCapsFeatures("memory:SystemMemory"))))
        self.assertTrue(struct["markers"].is_equivalent_to(
            SCHEMA.GESMarkerList(
                SCHEMA.GESMarker(1032, SCHEMA.GstStructure(
                    "metadatas", {"val": ("int", -5)})),
                SCHEMA.GESMarker(2748, SCHEMA.GstStructure(
                    "metadatas", {"val": ("string", "test test")})))))

    def test_GstStructure_to_str_and_back(self):
        # TODO: remove once python2 has ended
        # Python2 does not have assertWarns
        if str is bytes:
            return
        with self.assertWarns(UserWarning):
            struct_before = SCHEMA.GstStructure(
                "Struct:/Name0a", {
                    "str-ing": ("string", UTF8_NAME),
                    "i/nt": ("int", 67),
                    "f.lo+t": ("float", -0.78),
                    "frac_tion": ("fraction", "4/67"),
                    "my-type": ("mytype", "test"),
                    "a_list": ("list", "{ 0, 2, 1 }"),
                    "stru-cture": ("structure", SCHEMA.GstStructure(
                        "Name", {"val": ("string", UTF8_NAME)})),
                    "ca/ps": ("GstCaps", SCHEMA.GstCaps(
                        SCHEMA.GstStructure(
                            "Struct1", {"val": ("string", UTF8_NAME)}),
                        SCHEMA.GstCapsFeatures("memory:SystemMemory"))),
                    "markers+": ("GESMarkerList", SCHEMA.GESMarkerList(
                        SCHEMA.GESMarker(
                            2039, SCHEMA.GstStructure(
                                "metadatas",
                                {"val": ("string", UTF8_NAME)})),
                        SCHEMA.GESMarker(
                            209389023, SCHEMA.GstStructure(
                                "metadatas",
                                {"val": ("float", -0.96)}))))
                })
        with self.assertWarns(UserWarning):
            struct_after = SCHEMA.GstStructure.new_from_str(
                str(struct_before))
        self.assertTrue(struct_before.is_equivalent_to(struct_after))

    def test_GstStructure_dictionary_def(self):
        struct = SCHEMA.GstStructure(
            "properties", {
                "String-1": ("string", "test"),
                "String-2": ("string", "test space"),
                "Int": ("int", -5),
                "Uint": ("uint", 5),
                "Float": ("float", 2.0),
                "Boolean": ("boolean", True),
                "Fraction": ("fraction", "2/5"),
                "Structure": ("structure", SCHEMA.GstStructure(
                    "Name", {"val": ("string", "test space")})),
                "Caps": ("GstCaps", SCHEMA.GstCaps(
                    SCHEMA.GstStructure(
                        "Struct1",
                        {"val": ("string", "test space")}),
                    SCHEMA.GstCapsFeatures("memory:SystemMemory"))),
                "Markers": ("GESMarkerList", SCHEMA.GESMarkerList(
                    SCHEMA.GESMarker(
                        2039, SCHEMA.GstStructure(
                            "metadatas",
                            {"val": ("string", "test space")})),
                    SCHEMA.GESMarker(
                        209389023, SCHEMA.GstStructure(
                            "metadatas",
                            {"val": ("float", -0.96)}))))
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
        self.assertIn(
            "Structure=(structure)\"Name\\,\\ "
            "val\\=\\(string\\)\\\"test\\\\\\ space\\\"\\;\"",
            write)
        self.assertIn(
            "Caps=(GstCaps)\"Struct1\\(memory:SystemMemory\\)\\,\\ "
            "val\\=\\(string\\)\\\"test\\\\\\ space\\\"\"",
            write)
        self.assertIn(
            "Markers=(GESMarkerList)\"marker-times, position=(guint64)"
            "2039; metadatas, val=(string)\\\"test\\\\ space\\\"; "
            "marker-times, position=(guint64)209389023; "
            "metadatas, val=(float)-0.96\"",
            write)

    def test_GstStructure_equality(self):
        struct1 = SCHEMA.GstStructure.new_from_str(
            "name, prop1=(string)4, prop2=(int)4;")
        struct2 = SCHEMA.GstStructure.new_from_str(
            "name, prop2=(int)4, prop1=(string)4;")
        struct3 = SCHEMA.GstStructure.new_from_str(
            "name, prop1=(str)4, prop2=(gint)4;")
        struct4 = SCHEMA.GstStructure.new_from_str(
            "name-alt, prop1=(string)4, prop2=(int)4;")
        struct5 = SCHEMA.GstStructure.new_from_str(
            "name, prop1=(string)4, prop3=(int)4;")
        struct6 = SCHEMA.GstStructure.new_from_str(
            "name, prop1=(int)4, prop2=(int)4;")
        struct7 = SCHEMA.GstStructure.new_from_str(
            "name, prop1=(string)4, prop2=(int)5;")
        struct8 = SCHEMA.GstStructure.new_from_str(
            "name, prop1=(string)4, prop2=(int)4, prop3=(bool)true;")
        struct9 = SCHEMA.GstStructure.new_from_str(
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
        struct = SCHEMA.GstStructure.new_from_str(
            'properties, name=(string)before;')
        self.assertEqual(struct["name"], "before")
        struct.set("name", "string", "after")
        self.assertEqual(struct["name"], "after")
        self.assertEqual(str(struct), 'properties, name=(string)after;')

    def test_GstStructure_empty_string(self):
        struct = SCHEMA.GstStructure.new_from_str(
            'properties, name=(string)"";')
        self.assertEqual(struct["name"], "")

    def test_GstStructure_NULL_string(self):
        struct = SCHEMA.GstStructure.new_from_str(
            'properties, name=(string)NULL;')
        self.assertEqual(struct["name"], None)
        struct = SCHEMA.GstStructure.new_from_str("properties")
        struct.set("name", "string", None)
        self.assertEqual(str(struct), 'properties, name=(string)NULL;')
        struct = SCHEMA.GstStructure.new_from_str(
            'properties, name=(string)\"NULL\";')
        self.assertEqual(struct["name"], "NULL")
        self.assertEqual(str(struct), 'properties, name=(string)\"NULL\";')

    def test_GstStructure_fraction(self):
        struct = SCHEMA.GstStructure.new_from_str(
            'properties, framerate=(fraction)2/5;')
        self.assertEqual(struct["framerate"], "2/5")
        struct.set("framerate", "fraction", Fraction("3/5"))
        self.assertEqual(struct["framerate"], "3/5")
        struct.set("framerate", "fraction", "4/5")
        self.assertEqual(struct["framerate"], "4/5")

    def test_GstStructure_type_aliases(self):
        struct = SCHEMA.GstStructure.new_from_str(
            "properties,String-1=(str)test,String-2=(s)\"test\","
            "Int-1=(i)-5,Int-2=(gint)-5,Uint-1=(u)5,Uint-2=(guint)5,"
            "Float-1=(f)0.5,Float-2=(gfloat)0.5,Double-1=(d)0.7,"
            "Double-2=(gdouble)0.7,Boolean-1=(bool)true,"
            "Boolean-2=(b)true,Boolean-3=(gboolean)true,"
            "Fraction=(GstFraction)2/5,"
            "Structure=(GstStructure)\"name\\;\"")
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
        self.assertTrue(struct["Structure"].is_equivalent_to(
            SCHEMA.GstStructure("name")))
        struct = SCHEMA.GstStructure("properties")
        struct.set("prop", "s", "test test")
        self.assertEqual(struct["prop"], "test test")
        self.assertEqual(struct.get_type_name("prop"), "string")
        struct.set("prop", "str", "test test")
        self.assertEqual(struct["prop"], "test test")
        self.assertEqual(struct.get_type_name("prop"), "string")
        struct.set("prop", "i", -5)
        self.assertEqual(struct["prop"], -5)
        self.assertEqual(struct.get_type_name("prop"), "int")
        struct.set("prop", "gint", -5)
        self.assertEqual(struct["prop"], -5)
        self.assertEqual(struct.get_type_name("prop"), "int")
        struct.set("prop", "u", 5)
        self.assertEqual(struct["prop"], 5)
        self.assertEqual(struct.get_type_name("prop"), "uint")
        struct.set("prop", "guint", 5)
        self.assertEqual(struct["prop"], 5)
        self.assertEqual(struct.get_type_name("prop"), "uint")
        struct.set("prop", "f", 0.5)
        self.assertEqual(struct["prop"], 0.5)
        self.assertEqual(struct.get_type_name("prop"), "float")
        struct.set("prop", "gfloat", 0.5)
        self.assertEqual(struct["prop"], 0.5)
        self.assertEqual(struct.get_type_name("prop"), "float")
        struct.set("prop", "d", 0.7)
        self.assertEqual(struct["prop"], 0.7)
        self.assertEqual(struct.get_type_name("prop"), "double")
        struct.set("prop", "gdouble", 0.7)
        self.assertEqual(struct["prop"], 0.7)
        self.assertEqual(struct.get_type_name("prop"), "double")
        struct.set("prop", "b", True)
        self.assertEqual(struct["prop"], True)
        self.assertEqual(struct.get_type_name("prop"), "boolean")
        struct.set("prop", "bool", True)
        self.assertEqual(struct["prop"], True)
        self.assertEqual(struct.get_type_name("prop"), "boolean")
        struct.set("prop", "gboolean", True)
        self.assertEqual(struct["prop"], True)
        self.assertEqual(struct.get_type_name("prop"), "boolean")
        struct.set("prop", "GstFraction", Fraction("2/5"))
        self.assertEqual(struct["prop"], "2/5")
        self.assertEqual(struct.get_type_name("prop"), "fraction")
        struct.set("prop", "GstStructure", SCHEMA.GstStructure("name"))
        self.assertTrue(struct["prop"].is_equivalent_to(
            SCHEMA.GstStructure("name")))
        self.assertEqual(struct.get_type_name("prop"), "structure")

    def test_GstStructure_values_list(self):
        structs = [
            SCHEMA.GstStructure.new_from_str(
                "name, String1=(string)\"\", Int1=(int)0, "
                "Float1=(float)0.1, Int2=(i)5, Float2=(f)0.2, "
                "String2=(s)NULL, String3=(string)test"),
            SCHEMA.GstStructure("name", {
                "String1": ("string", ""), "Int1": ("int", 0),
                "Float1": ("float", 0.1), "Int2": ("i", 5),
                "Float2": ("f", 0.2), "String2": ("s", None),
                "String3": ("string", "test")})]

        # TODO: remove once python2 has ended
        # Python2 does not have assertCountEqual
        def assertCountEqual(x, y):
            if str is bytes:
                self.assertEqual(sorted(x), sorted(y))
            else:
                self.assertCountEqual(x, y)

        for struct in structs:
            assertCountEqual(
                struct.values(), ["", 0, 0.1, 5, 0.2, None, "test"])
            assertCountEqual(
                struct.values_of_type("string"), ["", None, "test"])
            assertCountEqual(
                struct.values_of_type("s"), ["", None, "test"])
            assertCountEqual(
                struct.values_of_type("int"), [0, 5])
            assertCountEqual(
                struct.values_of_type("i"), [0, 5])
            assertCountEqual(
                struct.values_of_type("float"), [0.1, 0.2])
            assertCountEqual(
                struct.values_of_type("f"), [0.1, 0.2])
            assertCountEqual(
                struct.values_of_type("double"), [])

    def test_GstStructure_getting(self):
        structs = [
            SCHEMA.GstStructure.new_from_str(
                "name, String=(string)test, Int=(int)5;"),
            SCHEMA.GstStructure("name", {
                "String": ("string", "test"), "Int": ("int", 5)})]
        for struct in structs:
            self.assertEqual(struct.get("Strin"), None)
            self.assertEqual(struct.get("Strin", "default"), "default")
            self.assertEqual(
                struct.get_typed("Strin", "string", "default"), "default")
            self.assertEqual(struct.get("String"), "test")
            self.assertEqual(struct.get_typed("String", "string"), "test")
            self.assertEqual(struct.get_typed("String", "s"), "test")
            self.assertEqual(struct.get("Int"), 5)
            self.assertEqual(struct.get_typed("Int", "int"), 5)
            self.assertEqual(struct.get_typed("Int", "i"), 5)
            # TODO: remove once python2 has ended
            # Python2 does not have assertWarns
            if str is bytes:
                continue
            with self.assertWarns(UserWarning):
                self.assertEqual(
                    struct.get_typed("String", "int", 23), 23)
            with self.assertWarns(UserWarning):
                self.assertEqual(
                    struct.get_typed("Int", "string", "def"), "def")

    def test_GstStructure_invalid_parse(self):
        # invalid names:
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str("0name, prop=(int)4;")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str(
                f"{UTF8_NAME}, prop=(int)4;")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure("0name", {"prop": ("int", 4)})
        # invalid fieldnames:
        struct = SCHEMA.GstStructure.new_from_str("name")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str("name, prop erty=(int)4;")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop erty", "int", 4)
        with self.assertRaises(otio.exceptions.OTIOError):
            # the following would cause problems with serializing
            # followed by de-serializing, since it would create two
            # different fields!
            struct.set("prop=(int)4, other=", "string", "test")
        # invalid type names
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str("name, prop=(my type)4;")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "int ", 4)
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", " int", 4)
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "my type", 4)
        # invalid serialized values
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str("name, prop=(int)4.5")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str("name, prop=(float)7.0s")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str('name, prop=(string);')
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str(
                "name, prop=(boolean)yesyes;")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str(
                "name, prop=(fraction)1/2.0;")
        with self.assertRaises(otio.exceptions.OTIOError):
            # no comma in list
            SCHEMA.GstStructure.new_from_str(
                "name, prop=(list){ 5, 6 7 };")
        with self.assertRaises(otio.exceptions.OTIOError):
            SCHEMA.GstStructure.new_from_str(
                "name, prop=(list){ 5, 6, 7;")
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
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "mytype", "test ")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "mytype", "&")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "mytype", "(int)4")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "mytype", "4, other_prop=(string)insert")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "mytype", "4;")  # would hide rest!
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "list", "{ 5, 6 7 }")  # no comma
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "list", "{ {5}, { 6 7} }")  # no comma

    def test_GstStructure_unknown_type(self):
        # TODO: remove once python2 has ended
        # Python2 does not have assertWarns
        if str is bytes:
            return
        struct = SCHEMA.GstStructure("properties")
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set(
                "prop", "MyType", "test, other_field=(string)insert")
            # would cause errors when trying to reserialize!
        with self.assertRaises(otio.exceptions.OTIOError):
            struct.set("prop", "MyType ", "test ")
            # don't want trailing whitespaces
        with self.assertWarns(UserWarning):
            struct.set("prop", "MyType", "test")
        self.assertEqual(struct["prop"], "test")
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure.new_from_str(
                "properties, prop= ( MyOtherType )  4-5  ;")
        self.assertEqual(struct["prop"], "4-5")
        self.assertEqual(
            str(struct), "properties, prop=(MyOtherType)4-5;")
        with self.assertWarns(UserWarning):
            SCHEMA.GstStructure("properties", struct.fields)
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure.new_from_str(
                'properties, prop=(string) {  "spa\\ ce"  ,  '
                '( string )  test }  ;')
        self.assertEqual(
            struct["prop"], '{ "spa\\ ce", (string)test }')
        self.assertEqual(
            str(struct), 'properties, prop=(string){ "spa\\ ce", '
            '(string)test };')
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure.new_from_str(
                "properties, prop=(int)<1,3,4,5>;")
        self.assertEqual(struct["prop"], "< 1, 3, 4, 5 >")
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure.new_from_str(
                "properties, prop=(int)[1,3];")
        self.assertEqual(struct["prop"], "[ 1, 3 ]")
        with self.assertWarns(UserWarning):
            struct = SCHEMA.GstStructure.new_from_str(
                "properties, prop=(MyType){(MyType){1,2},"
                "(MyType){3a3,4,5}};")
        self.assertEqual(
            struct["prop"],
            "{ (MyType){ 1, 2 }, (MyType){ 3a3, 4, 5 } }")

    def test_image_sequence_example(self):
        timeline = otio.adapters.read_from_file(IMAGE_SEQUENCE_EXAMPLE_PATH)

        ges_el = self._get_xges_from_otio_timeline(timeline)
        self.assertIsNotNone(ges_el)
        self.assertXgesNumLayers(ges_el, 1)
        self.assertXgesAsset(
            ges_el,
            "imagesequence:./sample_sequence/sample_sequence.%2504d.exr" +
            "?rate=24/1&start-index=86400&stop-index=86450",
            "GESUriClip")

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
        with open(XGES_EXAMPLE_PATH) as original_file:
            with open(tmp_path) as output_file:
                self.assertNotEqual(original_file.read(), output_file.read())


if __name__ == '__main__':
    unittest.main()
