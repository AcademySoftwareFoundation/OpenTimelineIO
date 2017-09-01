#
# Copyright 2017 Pixar Animation Studios
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
"""Unit tests for the rv session file adapter"""

import unittest

import opentimelineio as otio

MODULE = otio.adapters.from_name('ffmpeg_burnins').module()
SAMPLE_DATA = """{
    "OTIO_SCHEMA": "Timeline.1", 
    "metadata": {
        "ffmpeg_burnins": {
            "overwrite": true,
            "burnins": [
                {
                    "text": "Top Center",
                    "align": "TOP_CENTERED",
                    "font": "/System/Library/Fonts/Menlo.ttc",
                    "font_size": 48,
                    "function": "text"
                },
                {
                    "align": "TOP_LEFT",
                    "x_offset": 75,
                    "font": "/System/Library/Fonts/Menlo.ttc",
                    "frame_offset": 101,
                    "font_size": 48,
                    "function": "frame_number"
                }
            ]
        }
    }, 
    "name": "BUSH0005.MOV", 
    "tracks": {
        "OTIO_SCHEMA": "Stack.1", 
        "children": [
            {
                "OTIO_SCHEMA": "Sequence.1", 
                "children": [
                    {
                        "OTIO_SCHEMA": "Clip.1", 
                        "effects": [], 
                        "markers": [], 
                        "media_reference": {
                            "OTIO_SCHEMA": "ExternalReference.1", 
                            "available_range": {
                                "OTIO_SCHEMA": "TimeRange.1", 
                                "duration": {
                                    "OTIO_SCHEMA": "RationalTime.1", 
                                    "rate": 30.0, 
                                    "value": 600.0
                                }, 
                                "start_time": {
                                    "OTIO_SCHEMA": "RationalTime.1", 
                                    "rate": 30.0, 
                                    "value": 0.0
                                }
                            }, 
                            "metadata": {}, 
                            "name": null, 
                            "target_url": "file://BUSH0005.MOV"
                        }, 
                        "metadata": {}, 
                        "name": "BUSH0005.MOV", 
                        "source_range": null
                    }
                ], 
                "effects": [], 
                "kind": "Video", 
                "markers": [], 
                "metadata": {}, 
                "name": "BUSH0005.MOV", 
                "source_range": null
            }
        ], 
        "effects": [], 
        "markers": [], 
        "metadata": {}, 
        "name": "tracks", 
        "source_range": null
    }
}"""
COMMAND = ("ffmpeg -loglevel panic -i BUSH0005.MOV -vf "
           "\"drawbox=815:0:295:57:black@1.0:t=max,"
           "drawbox=75:0:92:48:black@1.0:t=max,drawtext="
           "text='Top Center':x=w/2-tw/2+2:y=5:fontcolor"
           "=white@1.0:fontsize=48:fontfile=/System/"
           "Library/Fonts/Menlo.ttc,drawtext=text="
           r"'%{eif\:n+101\:d}':x=77.5:y=5:fontcolor="
           "white@1.0:fontsize=48:fontfile=/System/"
           "Library/Fonts/Menlo.ttc\" BUSH0005.MOV")

class FFMPEGBurninsTest(unittest.TestCase):
    """Test Cases for FFMPEG Burnins"""

    def test_burnins(self):
        """
        Simple test case that just tests the resulting
        command string, no media output is being tested.
        """
        timeline = otio.adapters.read_from_string(SAMPLE_DATA, "otio_json")
        burnins = MODULE.build_burnins(timeline)
        self.assertEqual(len(burnins), 1)
        command = burnins[-1].command(burnins[-1].otio_media)
        self.assertEqual(command, COMMAND)


if __name__ == '__main__':
    unittest.main()
