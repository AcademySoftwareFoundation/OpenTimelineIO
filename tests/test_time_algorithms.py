#!/usr/bin/env python

import unittest

import opentimelineio as otio


class ExampleCase(unittest.TestCase):
    def setUp(self):
        # a simple timeline with one track, with one clip, but with a global
        # offset of 1 hour.
        self.tl = otio.schema.Timeline(name="test")
        self.tl.global_start_time = otio.opentime.RationalTime(86400, 24)

        self.tl.tracks.append(otio.schema.Track())
        self.tl.tracks[0].append(otio.schema.Clip())

        self.tr = self.tl.tracks[0]
        self.cl = self.tl.tracks[0][0]

        # media reference goes 100 frames.
        self.cl.media_reference = otio.schema.MissingReference(
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(100, 24),
            )
        )

    def test_single_timeline_object(self):
        some_frame = otio.opentime.RationalTime(86410, 24)

        # transform within the same object first, from global to internal
        result = otio.algorithms.transform_time(
            some_frame,
            self.tl.global_space(),
            self.tl.internal_space()
        )

        self.assertEqual(result.value, 10)

        # back into the global space
        result = otio.algorithms.transform_time(
            result,
            self.tl.internal_space(),
            self.tl.global_space(),
        )

        self.assertEqual(result, some_frame)
        )

        self.assertEqual(result, otio.opentime.RationalTime(10, 24))


if __name__ == '__main__':
    unittest.main()
