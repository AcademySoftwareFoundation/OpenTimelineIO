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

"""Unit tests for the OTIO to SVG adapter"""

import os
import unittest
import tempfile

import opentimelineio as otio

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
SIMPLE_CUT_OTIO_PATH = os.path.join(SAMPLE_DATA_DIR, 'simple_cut.otio')
SIMPLE_CUT_SVG_PATH = os.path.join(SAMPLE_DATA_DIR, 'simple_cut.svg')
MULTIPLE_TRACK_OTIO_PATH = os.path.join(SAMPLE_DATA_DIR, 'multiple_track.otio')
MULTIPLE_TRACK_SVG_PATH = os.path.join(SAMPLE_DATA_DIR, 'multiple_track.svg')
TRANSITION_OTIO_PATH = os.path.join(SAMPLE_DATA_DIR, 'transition.otio')
TRANSITION_SVG_PATH = os.path.join(SAMPLE_DATA_DIR, 'transition.svg')


class SVGAdapterTest(unittest.TestCase):
    def test_simple_cut(self):
        self.maxDiff = None
        tmp_path = tempfile.mkstemp(suffix=".svg", text=True)[1]
        otio.adapters.write_to_file(SIMPLE_CUT_OTIO_PATH, tmp_path)

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(SIMPLE_CUT_SVG_PATH) as svg_file:
            reference_svg_string = svg_file.read()

        self.assertMultiLineEqual(reference_svg_string, test_data)

    def test_multiple_tracks(self):
        self.maxDiff = None
        tmp_path = tempfile.mkstemp(suffix=".svg", text=True)[1]
        otio.adapters.write_to_file(MULTIPLE_TRACK_OTIO_PATH, tmp_path)

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(MULTIPLE_TRACK_SVG_PATH) as svg_file:
            reference_svg_string = svg_file.read()

        self.assertMultiLineEqual(reference_svg_string, test_data)

    def test_transition(self):
        self.maxDiff = None
        tmp_path = tempfile.mkstemp(suffix=".svg", text=True)[1]
        otio.adapters.write_to_file(TRANSITION_OTIO_PATH, tmp_path)

        with open(tmp_path) as fo:
            test_data = fo.read()

        with open(TRANSITION_SVG_PATH) as svg_file:
            reference_svg_string = svg_file.read()

        self.assertMultiLineEqual(reference_svg_string, test_data)
