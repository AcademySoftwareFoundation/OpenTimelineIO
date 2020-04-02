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
"""Unit tests for the rv session file adapter"""

import unittest

import opentimelineio as otio

MODULE = otio.adapters.from_name('burnins').module()
SAMPLE_DATA = """{
    "OTIO_SCHEMA": "Timeline.1",
    "metadata": {
        "burnins": {
            "overwrite": true,
            "burnins": [
                {
                    "text": "Top Center",
                    "align": "top_centered",
                    "font": "/System/Library/Fonts/Menlo.ttc",
                    "font_size": 48,
                    "function": "text"
                },
                {
                    "align": "top_left",
                    "x_offset": 75,
                    "font": "/System/Library/Fonts/Menlo.ttc",
                    "frame_offset": 101,
                    "font_size": 48,
                    "function": "frame_number"
                }
            ],
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1",
                    "start_time": "0.000000",
                    "duration": "20.000000"
                }
            ]
        }
    },
    "name": "TEST.MOV",
    "tracks": {
        "OTIO_SCHEMA": "Stack.1",
        "children": [
            {
                "OTIO_SCHEMA": "Track.1",
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
                            "target_url": "file://TEST.MOV"
                        },
                        "metadata": {},
                        "name": "TEST.MOV",
                        "source_range": null
                    }
                ],
                "effects": [],
                "kind": "Video",
                "markers": [],
                "metadata": {},
                "name": "TEST.MOV",
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
WITH_BG = ('ffmpeg -loglevel panic -i TEST.MOV -vf "drawtext=text='
           '\'Top Center\':x=w/2-tw/2:y=0:fontcolor=white@1.0:fontsize'
           '=48:fontfile=\'/System/Library/Fonts/Menlo.ttc\':box=1:boxbord'
           'erw=5:boxcolor=black@1.0,drawtext=text=\''
           r'%{eif\:n+101\:d}'
           '\':x=75:y=0:fontcolor=white@1.0:fontsize=48:fontfile=\'/Syst'
           'em/Library/Fonts/Menlo.ttc\':box=1:boxborderw=5:boxcolor=bla'
           'ck@1.0" TEST.MOV')

WITHOUT_BG = ('ffmpeg -loglevel panic -i TEST.MOV -vf "drawtext=text='
              '\'Top Center\':x=w/2-tw/2:y=0:fontcolor=white@1.0:fontsize'
              '=48:fontfile=\'/System/Library/Fonts/Menlo.ttc\','
              'drawtext=text=\''
              r'%{eif\:n+101\:d}'
              '\':x=75:y=0:fontcolor=white@1.0:fontsize=48:fontfile=\'/System'
              '/Library/Fonts/Menlo.ttc\'" TEST.MOV')
TIMECODE = ('ffmpeg -loglevel panic -i TEST.MOV -vf "drawtext=timecode='
            '\'Top Center\':timecode_rate=24.00:x=w/2-tw/2:y=0:fontcolor='
            'white@1.0:fontsize=48:fontfile=\'/System/Library/Fonts/Menlo.'
            'ttc\':box=1:boxborderw=5:boxcolor=black@1.0,drawtext=timecode='
            r"'00\:00\:00\:00':timecode_rate=24.00:x=75:y=0:fontcolor="
            'white@1.0:fontsize=48:fontfile=\'/System/Library/Fonts/Menlo.'
            'ttc\':box=1:boxborderw=5:boxcolor=black@1.0" TEST.MOV')


try:
    import PIL # noqa
    from PIL.Image import core as imaging # noqa
    could_import_pillow = True
except (ImportError, SyntaxError):
    could_import_pillow = False


@unittest.skipIf(
    not could_import_pillow,
    "Pillow Required for burnin unit tests. see:"
    " https://python-pillow.org/"
)
class FFMPEGBurninsTest(unittest.TestCase):
    """Test Cases for FFMPEG Burnins"""

    def test_burnins_with_background(self):
        """
        Tests creating burnins with a background (box)
        """
        timeline = otio.adapters.read_from_string(SAMPLE_DATA, "otio_json")
        burnins = MODULE.build_burnins(timeline)
        self.assertEqual(len(burnins), 1)
        command = burnins[-1].command(burnins[-1].otio_media)
        self.assertEqual(command, WITH_BG)

    def test_burnins_without_background(self):
        """
        Tests creating burnins without a background (box)
        """
        timeline = otio.adapters.read_from_string(SAMPLE_DATA, "otio_json")
        for each in timeline.metadata['burnins']['burnins']:
            each['bg_color'] = None
        burnins = MODULE.build_burnins(timeline)
        self.assertEqual(len(burnins), 1)
        command = burnins[-1].command(burnins[-1].otio_media)
        self.assertEqual(command, WITHOUT_BG)

    def test_burnins_with_timecode(self):
        """
        Tests creating burnins with an animated timecode
        """
        timeline = otio.adapters.read_from_string(SAMPLE_DATA, "otio_json")
        for each in timeline.metadata['burnins']['burnins']:
            each['function'] = 'timecode'
            each['frame_offset'] = 0
            each['fps'] = 24
        burnins = MODULE.build_burnins(timeline)
        self.assertEqual(len(burnins), 1)
        command = burnins[-1].command(burnins[-1].otio_media)
        self.assertEqual(command, TIMECODE)


if __name__ == '__main__':
    unittest.main()
