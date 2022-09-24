# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test harness for Image Sequence References."""
import unittest
import sys

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


IS_PYTHON_2 = (sys.version_info < (3, 0))


class ImageSequenceReferenceTests(
    unittest.TestCase, otio_test_utils.OTIOAssertions
):
    def test_create(self):
        frame_policy = otio.schema.ImageSequenceReference.MissingFramePolicy.hold
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            frame_step=3,
            missing_frame_policy=frame_policy,
            rate=30,
            metadata={"custom": {"foo": "bar"}},
        )

        # Check Values
        self.assertEqual(ref.target_url_base, "file:///show/seq/shot/rndr/")
        self.assertEqual(ref.name_prefix, "show_shot.")
        self.assertEqual(ref.name_suffix, ".exr")
        self.assertEqual(ref.frame_zero_padding, 5)
        self.assertEqual(
            ref.available_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            )
        )
        self.assertEqual(ref.frame_step, 3)
        self.assertEqual(ref.rate, 30)
        self.assertEqual(ref.metadata, {"custom": {"foo": "bar"}})
        self.assertEqual(
            ref.missing_frame_policy,
            otio.schema.ImageSequenceReference.MissingFramePolicy.hold,
        )

    def test_str(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            start_frame=1,
            frame_step=3,
            rate=30,
            frame_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            metadata={"custom": {"foo": "bar"}},
            available_image_bounds=otio.schema.Box2d(
                otio.schema.V2d(0.0, 0.0),
                otio.schema.V2d(16.0, 9.0)
            ),
        )
        self.assertEqual(
            str(ref),
            'ImageSequenceReference('
            '"file:///show/seq/shot/rndr/", '
            '"show_shot.", '
            '".exr", '
            '1, '
            '3, '
            '30.0, '
            '5, '
            'MissingFramePolicy.error, '
            'TimeRange(RationalTime(0, 30), RationalTime(60, 30)), '
            'Box2d(V2d(0.0, 0.0), V2d(16.0, 9.0)), '
            "{'custom': {'foo': 'bar'}}"
            ')'
        )

    def test_repr(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            start_frame=1,
            frame_step=3,
            rate=30,
            frame_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            available_image_bounds=otio.schema.Box2d(
                otio.schema.V2d(0.0, 0.0),
                otio.schema.V2d(16.0, 9.0)
            ),
            metadata={"custom": {"foo": "bar"}},
        )
        ref_value = (
            'ImageSequenceReference('
            "target_url_base='file:///show/seq/shot/rndr/', "
            "name_prefix='show_shot.', "
            "name_suffix='.exr', "
            'start_frame=1, '
            'frame_step=3, '
            'rate=30.0, '
            'frame_zero_padding=5, '
            'missing_frame_policy=<MissingFramePolicy.error: 0>, '
            'available_range={}, '
            'available_image_bounds=otio.schema.Box2d('
            'min=otio.schema.V2d(x=0.0, y=0.0), '
            'max=otio.schema.V2d(x=16.0, y=9.0)), '
            "metadata={{'custom': {{'foo': 'bar'}}}}"
            ')'.format(repr(ref.available_range))
        )
        self.assertEqual(repr(ref), ref_value)

    def test_serialize_roundtrip(self):
        frame_policy = otio.schema.ImageSequenceReference.MissingFramePolicy.hold
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=5,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            frame_step=3,
            rate=30,
            missing_frame_policy=frame_policy,
            metadata={"custom": {"foo": "bar"}},
        )

        encoded = otio.adapters.otio_json.write_to_string(ref)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(ref, decoded)

        encoded2 = otio.adapters.otio_json.write_to_string(decoded)
        self.assertEqual(encoded, encoded2)

        # Check Values
        self.assertEqual(
            decoded.target_url_base, "file:///show/seq/shot/rndr/"
        )
        self.assertEqual(decoded.name_prefix, "show_shot.")
        self.assertEqual(decoded.name_suffix, ".exr")
        self.assertEqual(decoded.frame_zero_padding, 5)
        self.assertEqual(
            decoded.available_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 30),
                otio.opentime.RationalTime(60, 30),
            )
        )
        self.assertEqual(decoded.frame_step, 3)
        self.assertEqual(decoded.rate, 30)
        self.assertEqual(
            decoded.missing_frame_policy,
            otio.schema.ImageSequenceReference.MissingFramePolicy.hold
        )
        self.assertEqual(decoded.metadata, {"custom": {"foo": "bar"}})

    def test_deserialize_invalid_enum_value(self):
        encoded = """{
            "OTIO_SCHEMA": "ImageSequenceReference.1",
            "metadata": {
                "custom": {
                    "foo": "bar"
                }
            },
            "name": "",
            "available_range": {
                "OTIO_SCHEMA": "TimeRange.1",
                "duration": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 30.0,
                    "value": 60.0
                },
                "start_time": {
                    "OTIO_SCHEMA": "RationalTime.1",
                    "rate": 30.0,
                    "value": 0.0
                }
            },
            "target_url_base": "file:///show/seq/shot/rndr/",
            "name_prefix": "show_shot.",
            "name_suffix": ".exr",
            "start_frame": 1,
            "frame_step": 3,
            "rate": 30.0,
            "frame_zero_padding": 5,
            "missing_frame_policy": "BOGUS"
        }"""
        with self.assertRaises(ValueError):
            otio.adapters.otio_json.read_from_string(encoded)

    def test_number_of_images_in_sequence(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            rate=24,
        )

        self.assertEqual(ref.number_of_images_in_sequence(), 48)

    def test_number_of_images_in_sequence_with_skip(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            frame_step=2,
            rate=24,
        )

        self.assertEqual(ref.number_of_images_in_sequence(), 24)

        ref.frame_step = 3
        self.assertEqual(ref.number_of_images_in_sequence(), 16)

    def test_target_url_for_image_number(self):
        all_images_urls = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(1, 49)
        ]
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        generated_urls = [
            ref.target_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls, generated_urls)

    def test_target_url_for_image_number_steps(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=2,
            rate=24,
        )

        all_images_urls = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(1, 49, 2)
        ]
        generated_urls = [
            ref.target_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls, generated_urls)

        ref.frame_step = 3
        all_images_urls_threes = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(1, 49, 3)
        ]
        generated_urls_threes = [
            ref.target_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls_threes, generated_urls_threes)

        ref.frame_step = 2
        ref.start_frame = 0
        all_images_urls_zero_first = [
            "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i)
            for i in range(0, 48, 2)
        ]
        generated_urls_zero_first = [
            ref.target_url_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]
        self.assertEqual(all_images_urls_zero_first, generated_urls_zero_first)

    def test_target_url_for_image_number_with_missing_slash(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        self.assertEqual(
            ref.target_url_for_image_number(0),
            "file:///show/seq/shot/rndr/show_shot.0001.exr"
        )

    def test_abstract_target_url(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        self.assertEqual(
            ref.abstract_target_url("@@@@"),
            "file:///show/seq/shot/rndr/show_shot.@@@@.exr"
        )

    def test_abstract_target_url_with_missing_slash(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        self.assertEqual(
            ref.abstract_target_url("@@@@"),
            "file:///show/seq/shot/rndr/show_shot.@@@@.exr"
        )

    def test_presentation_time_for_image_number(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=2,
            rate=24,
        )

        reference_values = [
            otio.opentime.RationalTime(i * 2, 24) for i in range(24)
        ]

        generated_values = [
            ref.presentation_time_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]

        self.assertEqual(generated_values, reference_values)

    def test_presentation_time_for_image_number_with_offset(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=2,
            rate=24,
        )

        first_frame_time = otio.opentime.RationalTime(12, 24)
        reference_values = [
            first_frame_time + otio.opentime.RationalTime(i * 2, 24)
            for i in range(24)
        ]

        generated_values = [
            ref.presentation_time_for_image_number(i)
            for i in range(ref.number_of_images_in_sequence())
        ]

        self.assertEqual(generated_values, reference_values)

    def test_end_frame(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        self.assertEqual(ref.end_frame(), 48)

        # Frame step should not affect this
        ref.frame_step = 2
        self.assertEqual(ref.end_frame(), 48)

    def test_end_frame_with_offset(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=101,
            frame_step=1,
            rate=24,
        )

        self.assertEqual(ref.end_frame(), 148)

        # Frame step should not affect this
        ref.frame_step = 2
        self.assertEqual(ref.end_frame(), 148)

    def test_frame_for_time(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        # The start time should be frame 1
        self.assertEqual(
            ref.frame_for_time(ref.available_range.start_time), 1
        )

        # Test a sample in the middle
        self.assertEqual(
            ref.frame_for_time(otio.opentime.RationalTime(15, 24)), 4
        )

        # The end time (inclusive) should map to the last frame number
        self.assertEqual(
            ref.frame_for_time(ref.available_range.end_time_inclusive()), 48
        )

        # make sure frame step and RationalTime rate have no effect
        ref.frame_step = 2
        self.assertEqual(
            ref.frame_for_time(otio.opentime.RationalTime(118, 48)), 48
        )

    def test_frame_for_time_out_of_range(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 30),
                otio.opentime.RationalTime(60, 30),
            ),
            start_frame=1,
            frame_step=1,
            rate=30,
        )
        with self.assertRaises(ValueError):
            ref.frame_for_time(otio.opentime.RationalTime(73, 30))

    def test_frame_range_for_time_range(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(60, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )
        time_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(24, 24),
            otio.opentime.RationalTime(17, 24),
        )

        self.assertEqual(ref.frame_range_for_time_range(time_range), (13, 29))

    def test_frame_range_for_time_range_out_of_available_image_bounds(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(60, 24),
            ),
            start_frame=1,
            frame_step=1,
            rate=24,
        )
        time_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(24, 24),
            otio.opentime.RationalTime(60, 24),
        )

        with self.assertRaises(ValueError):
            ref.frame_range_for_time_range(time_range)

    def test_negative_frame_numbers(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(12, 24),
                otio.opentime.RationalTime(48, 24),
            ),
            start_frame=-1,
            frame_step=2,
            rate=24,
        )

        self.assertEqual(ref.number_of_images_in_sequence(), 24)
        self.assertEqual(
            ref.presentation_time_for_image_number(0),
            otio.opentime.RationalTime(12, 24),
        )
        self.assertEqual(
            ref.presentation_time_for_image_number(1),
            otio.opentime.RationalTime(14, 24),
        )
        self.assertEqual(
            ref.presentation_time_for_image_number(2),
            otio.opentime.RationalTime(16, 24),
        )
        self.assertEqual(
            ref.presentation_time_for_image_number(23),
            otio.opentime.RationalTime(58, 24),
        )

        self.assertEqual(
            ref.target_url_for_image_number(0),
            "file:///show/seq/shot/rndr/show_shot.-0001.exr",
        )

        self.assertEqual(
            ref.target_url_for_image_number(1),
            "file:///show/seq/shot/rndr/show_shot.0001.exr",
        )
        self.assertEqual(
            ref.target_url_for_image_number(2),
            "file:///show/seq/shot/rndr/show_shot.0003.exr",
        )
        self.assertEqual(
            ref.target_url_for_image_number(17),
            "file:///show/seq/shot/rndr/show_shot.0033.exr",
        )
        self.assertEqual(
            ref.target_url_for_image_number(23),
            "file:///show/seq/shot/rndr/show_shot.0045.exr",
        )

        # Check values by ones
        ref.frame_step = 1
        for i in range(1, ref.number_of_images_in_sequence()):
            self.assertEqual(
                ref.target_url_for_image_number(i),
                "file:///show/seq/shot/rndr/show_shot.{:04}.exr".format(i - 1),
            )

    def test_target_url_for_image_number_with_missing_timing_info(self):
        ref = otio.schema.ImageSequenceReference(
            "file:///show/seq/shot/rndr/",
            "show_shot.",
            ".exr",
            frame_zero_padding=4,
            start_frame=1,
            frame_step=1,
            rate=24,
        )

        # Make sure the right error and a useful message raised when
        # source_range is either un-set or zero duration.
        with self.assertRaises(IndexError) as exception_manager:
            ref.target_url_for_image_number(0)

        self.assertEqual(
            str(exception_manager.exception),
            "Zero duration sequences has no frames.",
        )

        ref.available_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(12, 24),
            otio.opentime.RationalTime(0, 1),
        )

        with self.assertRaises(IndexError) as exception_manager:
            ref.target_url_for_image_number(0)

        self.assertEqual(
            str(exception_manager.exception),
            "Zero duration sequences has no frames.",
        )

        # Set the duration and make sure a similarly useful message comes
        # when rate is un-set.
        ref.available_range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(12, 24),
            otio.opentime.RationalTime(48, 24),
        )
        ref.rate = 0

        with self.assertRaises(IndexError) as exception_manager:
            ref.target_url_for_image_number(0)

        self.assertEqual(
            str(exception_manager.exception),
            "Zero rate sequence has no frames.",
        )

    def test_clone(self):
        """ ensure that deeopcopy/clone function """
        isr = otio.schema.ImageSequenceReference()

        try:
            import copy
            cln = copy.deepcopy(isr)
            cln = isr.clone()
        except ValueError as exc:
            self.fail("Cloning raised an exception: {}".format(exc))

        self.assertJsonEqual(isr, cln)

    def test_target_url_for_image_number_with_blank_target_url_base(self):
        ref = otio.schema.ImageSequenceReference(
            name_prefix="myfilename.",
            name_suffix=".exr",
            start_frame=101,
            rate=24,
            frame_zero_padding=4,
            available_range=otio.opentime.TimeRange(
                otio.opentime.from_timecode("01:25:30:04", rate=24),
                duration=otio.opentime.from_frames(48, 24)
            ),
        )

        self.assertEqual(
            ref.target_url_for_image_number(0), "myfilename.0101.exr"
        )


if __name__ == "__main__":
    unittest.main()
