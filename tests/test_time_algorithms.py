#!/usr/bin/env python

import unittest

import opentimelineio as otio

class ExampleCase(unittest.TestCase):
    def setUp(self):
        # a simple timeline with one track, with one clip, but with a global
        # offset of 1 hour.
        self.tl = otio.schema.Timeline(name="test")
        self.tl.global_offset = otio.opentime.RationalTime(86400, 24)

        self.tl.tracks.append(otio.schema.Track())
        self.tl.tracks[0].append(otio.schema.Clip())

        self.tr = self.tl.tracks[0]
        self.cl = self.tl.tracks[0][0]

        # media reference goes 100 frames.
        self.cl.media_reference = otio.schema.MissingReference(
            available_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(100, 24),
            )
        )

    def test_frame_to_global(self):
        some_frame = otio.opentime.RationalTime(86410, 24)
        clip_that_is_playing = self.tl.tracks.top_clip_at_time(some_frame)

        result = otio.algorithms.transform_time(
            some_frame,
            self.tl.global_space(),
            clip_that_is_playing.media_reference.media_space()
        )

        self.assertEqual(result, otio.opentime.RationalTime(10, 24))

if __name__ == '__main__':
    unittest.main()
