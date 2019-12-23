# -*- coding: utf-8 -*-
#
# Copyright 2019 Pixar Animation Studios
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


import opentimelineio as otio


import unittest


class VLCTests(unittest.TestCase):
    def setUp(self):
        test_otio = otio.schema.Timeline()
        test_otio.tracks.append(otio.schema.Track())
        self.cl = otio.schema.Clip("foo")
        self.cl.media_reference = otio.schema.ExternalReference(target_url="foobar")
        test_otio.tracks[0].append(self.cl)
        self.test_otio = test_otio

    def test_basic(self):
        result = otio.adapters.write_to_string(self.test_otio, "vlc")
        self.assertIn("File1=foobar", result)

    def test_only_timeline_constraint(self):
        # test crash cases
        with self.assertRaises(otio.exceptions.NotSupportedError):
            otio.adapters.write_to_string(self.cl, "vlc")

    def test_only_external_reference_constraint(self):
        self.cl.media_reference = otio.schema.GeneratorReference()
        with self.assertRaises(otio.exceptions.NotSupportedError):
            otio.adapters.write_to_string(self.test_otio, "vlc")

    def test_single_track_constraint(self):
        # single track constraint
        self.test_otio.tracks.append(otio.schema.Track())
        with self.assertRaises(otio.exceptions.NotSupportedError):
            otio.adapters.write_to_string(self.test_otio, "vlc")


if __name__ == '__main__':
    unittest.main()
