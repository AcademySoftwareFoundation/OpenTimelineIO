#
# Copyright 2018 Pixar Animation Studios
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

"""Test the Media File adapter."""

# python
import os
import unittest

import opentimelineio as otio

SAMPLE_DATA_DIR = otio.test_utils.SAMPLE_DATA_DIR
EXAMPLE_PATH0 = os.path.join(SAMPLE_DATA_DIR, "frame_debugger_0h.mov")
EXAMPLE_PATH1 = os.path.join(SAMPLE_DATA_DIR, "frame_debugger_1h.mov")


# try:
# TODO: Try to detect the presence of ffprobe, so we can skip this test
#     could_find_ffprobe = True
# except (ImportError):
#     could_find_ffprobe = False
#
# @unittest.skipIf(
#     not could_find_ffprobe,
#     "ffprobe command line tool not found."
# )
class MediaFileAdapterTest(unittest.TestCase):

    def test_mov_read(self):
        mov_path = EXAMPLE_PATH0
        timeline = otio.adapters.read_from_file(mov_path)
        self.assertEqual(timeline.name, "frame_debugger_0h")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        self.assertEqual(
            otio.opentime.from_timecode("00:00:05:00", fps),
            timeline.duration()
        )

        self.assertEqual(len(timeline.tracks), 1)

        self.assertEqual(len(timeline.video_tracks()), 1)
        video_track = timeline.video_tracks()[0]
        self.assertEqual(len(video_track), 1)

        clip = video_track[0]

        self.assertEqual("frame_debugger_0h.mov", clip.name)
        self.assertEqual(
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("00:00:00:00", fps),
                otio.opentime.from_timecode("00:00:05:00", fps)
            ),
            clip.trimmed_range()
        )

    def test_mov_timecode_read(self):
        mov_path = EXAMPLE_PATH1
        timeline = otio.adapters.read_from_file(mov_path)
        self.assertEqual(timeline.name, "frame_debugger_1h")
        fps = timeline.duration().rate
        self.assertEqual(fps, 24.0)
        self.assertEqual(
            otio.opentime.from_timecode("00:00:05:00", fps),
            timeline.duration()
        )

        self.assertEqual(len(timeline.tracks), 1)

        self.assertEqual(len(timeline.video_tracks()), 1)
        video_track = timeline.video_tracks()[0]
        self.assertEqual(len(video_track), 1)

        clip = video_track[0]

        self.assertEqual("frame_debugger_1h.mov", clip.name)
        self.assertEqual(
            otio.opentime.TimeRange(
                otio.opentime.from_timecode("01:00:00:00", fps),
                otio.opentime.from_timecode("00:00:05:00", fps)
            ),
            clip.trimmed_range()
        )


if __name__ == '__main__':
    unittest.main()
