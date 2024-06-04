#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class TrackTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_find_children(self):
        cl = otio.schema.Clip()
        tr = otio.schema.Track()
        tr.append(cl)
        result = tr.find_children(otio.schema.Clip)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl)

    def test_find_children_search_range(self):
        range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0.0, 24.0),
            otio.opentime.RationalTime(24.0, 24.0))
        cl0 = otio.schema.Clip()
        cl0.source_range = range
        cl1 = otio.schema.Clip()
        cl1.source_range = range
        cl2 = otio.schema.Clip()
        cl2.source_range = range
        tr = otio.schema.Track()
        tr.append(cl0)
        tr.append(cl1)
        tr.append(cl2)
        result = tr.find_children(otio.schema.Clip, range)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl0)

    def test_find_children_shallow_search(self):
        cl0 = otio.schema.Clip()
        cl1 = otio.schema.Clip()
        st = otio.schema.Stack()
        st.append(cl1)
        tr = otio.schema.Track()
        tr.append(cl0)
        tr.append(st)
        result = tr.find_children(otio.schema.Clip, shallow_search=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl0)
        result = tr.find_children(otio.schema.Clip, shallow_search=False)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], cl0)
        self.assertEqual(result[1], cl1)

    def test_find_children_stack(self):
        video_clip = otio.schema.Clip();
        video_clip.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0.0, 30.0),
            otio.opentime.RationalTime(700.0, 30.0))
        audio_clip = otio.schema.Clip();
        audio_clip.source_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0.0, 30.0),
            otio.opentime.RationalTime(704.0, 30.0))
        video_track = otio.schema.Track()
        audio_track = otio.schema.Track()
        stack = otio.schema.Stack()
        video_track.append(video_clip)
        audio_track.append(audio_clip)
        stack.append(video_track)
        stack.append(audio_track)

        time = otio.opentime.RationalTime(703.0, 30.0)
        one_frame = otio.opentime.RationalTime(1.0, 30.0)
        range = otio.opentime.TimeRange(time, one_frame)
        items = stack.find_children(search_range=range)
        self.assertEqual(len(items), 2)
        self.assertTrue(audio_clip in items)
        self.assertTrue(audio_track in items)

if __name__ == '__main__':
    unittest.main()
