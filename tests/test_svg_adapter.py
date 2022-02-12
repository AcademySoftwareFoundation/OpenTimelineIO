# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the OTIO to SVG adapter"""

import os
import unittest
import tempfile
import xml.etree.ElementTree as ET

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SIMPLE_CUT_OTIO_PATH = os.path.join(SAMPLE_DATA_DIR, 'simple_cut.otio')
SIMPLE_CUT_SVG_PATH = os.path.join(SAMPLE_DATA_DIR, 'simple_cut.svg')
MULTIPLE_TRACK_OTIO_PATH = os.path.join(SAMPLE_DATA_DIR, 'multiple_track.otio')
MULTIPLE_TRACK_SVG_PATH = os.path.join(SAMPLE_DATA_DIR, 'multiple_track.svg')
TRANSITION_OTIO_PATH = os.path.join(SAMPLE_DATA_DIR, 'transition.otio')
TRANSITION_SVG_PATH = os.path.join(SAMPLE_DATA_DIR, 'transition.svg')


def _svg_equal(e1, e2):
    if e1.tag != e2.tag:
        return False
    if e1.text != e2.text:
        return False
    if e1.tail != e2.tail:
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False
    return all(_svg_equal(c1, c2) for c1, c2 in zip(e1, e2))


class SVGAdapterTest(unittest.TestCase):
    def test_simple_cut(self):
        self.maxDiff = None
        tmp_path = tempfile.mkstemp(suffix=".svg", text=True)[1]
        timeline = otio.core.deserialize_json_from_file(SIMPLE_CUT_OTIO_PATH)
        otio.adapters.write_to_file(input_otio=timeline, filepath=tmp_path)

        test_tree = ET.parse(SIMPLE_CUT_SVG_PATH)
        test_root = test_tree.getroot()

        reference_tree = ET.parse(tmp_path)
        reference_root = reference_tree.getroot()

        self.assertTrue(_svg_equal(test_root, reference_root))

    def test_multiple_tracks(self):
        self.maxDiff = None
        tmp_path = tempfile.mkstemp(suffix=".svg", text=True)[1]
        timeline = otio.core.deserialize_json_from_file(MULTIPLE_TRACK_OTIO_PATH)
        otio.adapters.write_to_file(input_otio=timeline, filepath=tmp_path)

        test_tree = ET.parse(MULTIPLE_TRACK_SVG_PATH)
        test_root = test_tree.getroot()

        reference_tree = ET.parse(tmp_path)
        reference_root = reference_tree.getroot()

        self.assertTrue(_svg_equal(test_root, reference_root))

    def test_transition(self):
        self.maxDiff = None
        tmp_path = tempfile.mkstemp(suffix=".svg", text=True)[1]
        timeline = otio.core.deserialize_json_from_file(TRANSITION_OTIO_PATH)
        otio.adapters.write_to_file(input_otio=timeline, filepath=tmp_path)

        test_tree = ET.parse(TRANSITION_SVG_PATH)
        test_root = test_tree.getroot()

        reference_tree = ET.parse(tmp_path)
        reference_root = reference_tree.getroot()

        self.assertTrue(_svg_equal(test_root, reference_root))
