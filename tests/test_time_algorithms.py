#!/usr/bin/env python

import unittest

import opentimelineio as otio


class TestClipSpaces(unittest.TestCase):
    def setUp(self):
        # No effects, just a trim
        self.cl = otio.schema.Clip(
            source_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(450, 24),
                otio.opentime.RationalTime(30, 24),
            )
        )
        self.cl.media_reference = otio.schema.ExternalReference(
            # go 100 frames starting at frame 400
            available_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(400, 24),
                otio.opentime.RationalTime(100, 24),
            )
        )

    def test_spaces_from_bottom_to_top(self):
        media_space = self.cl.media_space()
        self.assertIsNotNone(media_space)

        internal_space = self.cl.internal_space()
        self.assertIsNotNone(internal_space)

        # media references don't directly participate in the coordinate 
        # hierarchy, rather their space is accessible via the media_space()
        # accessor on the clip.
        self.assertEqual(internal_space, media_space)

        trimmed_space = self.cl.trimmed_space()
        self.assertIsNotNone(trimmed_space)

        # the external space represents the space after all the transformations
        external_space = self.cl.external_space()
        self.assertIsNotNone(external_space)

        # the hidden method to transform within scopes in an object.
        result = self.cl._transform_time(
            # time to transform
            otio.opentime.RationalTime(460, 24),
            internal_space,
            internal_space
        )
        self.assertEqual(result.value, 460)

        # the hidden method to transform within scopes in an object.
        result = self.cl._transform_time(
            # time to transform
            otio.opentime.RationalTime(460, 24),
            internal_space,
            external_space
        )

        self.assertEqual(result.value, 10)

    def test_spaces_from_bottom_to_top_with_effects(self):
        internal_space = self.cl.internal_space()
        self.assertIsNotNone(internal_space)

        trimmed_space = self.cl.trimmed_space()
        self.assertIsNotNone(trimmed_space)

        effects_space = self.cl.effects_space()
        self.assertIsNotNone(effects_space)

        external_space = self.cl.external_space()
        self.assertIsNotNone(external_space)

        # the hidden method to transform within scopes in an object.
        result = self.cl._transform_time(
            # time to transform
            otio.opentime.RationalTime(460, 24),
            internal_space,
            internal_space
        )
        self.assertEqual(result.value, 460)

        result = self.cl._transform_time(
            # time to transform
            otio.opentime.RationalTime(460, 24),
            internal_space,
            effects_space
        )

        self.cl.effects.append(
            otio.schema.LinearTimeWarp(
                time_scalar=2
            )
        )

        # the hidden method to transform within scopes in an object.
        result = self.cl._transform_time(
            # time to transform
            otio.opentime.RationalTime(460, 24),
            internal_space,
            external_space
        )

        self.assertEqual(result.value, 5)


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

    def SKIP_test_multi_object(self):
        some_frame = otio.opentime.RationalTime(86410, 24)

        # @TODO: eventually, this would be cool
        #
        # clip_that_is_playing = self.tl.tracks.top_clip_at_time(
        #     search_time=some_frame,
        #     from_space=self.tl.global_space()
        # )
        # self.assertIsNotNone(clip_that_is_playing)

        result = otio.algorithms.transform_time(
            some_frame,
            self.tl.global_space(),
            self.cl.media_space()
        )

        self.assertEqual(result, otio.opentime.RationalTime(10, 24))


if __name__ == '__main__':
    unittest.main()
