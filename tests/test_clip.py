# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class ClipTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        name = "test"
        rt = otio.opentime.RationalTime(5, 24)
        tr = otio.opentime.TimeRange(rt, rt)
        mr = otio.schema.ExternalReference(
            available_range=otio.opentime.TimeRange(
                rt,
                otio.opentime.RationalTime(10, 24)
            ),
            target_url="/var/tmp/test.mov"
        )

        cl = otio.schema.Clip(
            name=name,
            media_reference=mr,
            source_range=tr,
            # transition_in
            # transition_out
        )
        self.assertEqual(cl.name, name)
        self.assertEqual(cl.source_range, tr)
        self.assertIsOTIOEquivalentTo(cl.media_reference, mr)

        encoded = otio.adapters.otio_json.write_to_string(cl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(cl, decoded)

    def test_clip_if(self):
        cl = otio.schema.Clip(name="test_clip")
        self.assertEqual(list(cl.clip_if()), [cl])

    def test_str(self):
        cl = otio.schema.Clip(name="test_clip")

        self.assertMultiLineEqual(
            str(cl),
            'Clip("test_clip", MissingReference(\'\', None, None, {}), None, {})'
        )
        self.assertMultiLineEqual(
            repr(cl),
            'otio.schema.Clip('
            "name='test_clip', "
            'media_reference={}, '
            'source_range=None, '
            'metadata={{}}'
            ')'.format(
                repr(cl.media_reference)
            )
        )

    def test_str_with_filepath(self):
        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.schema.ExternalReference(
                "/var/tmp/foo.mov"
            )
        )
        self.assertMultiLineEqual(
            str(cl),
            'Clip('
            '"test_clip", ExternalReference("/var/tmp/foo.mov"), None, {}'
            ')'
        )
        self.assertMultiLineEqual(
            repr(cl),
            'otio.schema.Clip('
            "name='test_clip', "
            "media_reference=otio.schema.ExternalReference("
            "target_url='/var/tmp/foo.mov'"
            "), "
            'source_range=None, '
            'metadata={}'
            ')'
        )

    def test_ranges(self):
        tr = otio.opentime.TimeRange(
            # 1 hour in at 24 fps
            start_time=otio.opentime.RationalTime(86400, 24),
            duration=otio.opentime.RationalTime(200, 24)
        )

        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.schema.ExternalReference(
                "/var/tmp/foo.mov",
                available_range=tr
            )
        )
        self.assertEqual(cl.duration(), cl.trimmed_range().duration)
        self.assertEqual(cl.duration(), tr.duration)
        self.assertEqual(cl.trimmed_range(), tr)
        self.assertEqual(cl.available_range(), tr)
        self.assertIsNot(cl.trimmed_range(), tr)
        self.assertIsNot(cl.available_range(), tr)

        cl.source_range = otio.opentime.TimeRange(
            # 1 hour + 100 frames
            start_time=otio.opentime.RationalTime(86500, 24),
            duration=otio.opentime.RationalTime(50, 24)
        )
        self.assertNotEqual(cl.duration(), tr.duration)
        self.assertNotEqual(cl.trimmed_range(), tr)
        self.assertEqual(cl.duration(), cl.source_range.duration)
        self.assertIsNot(cl.duration(), cl.source_range.duration)

        self.assertEqual(cl.trimmed_range(), cl.source_range)
        self.assertIsNot(cl.trimmed_range(), cl.source_range)

    def test_available_image_bounds(self):
        available_image_bounds = otio.schema.Box2d(
            otio.schema.V2d(0.0, 0.0),
            otio.schema.V2d(16.0, 9.0)
        )

        media_reference = otio.schema.ExternalReference(
            "/var/tmp/foo.mov",
            available_image_bounds=available_image_bounds
        )

        cl = otio.schema.Clip(
            name="test_available_image_bounds",
            media_reference=media_reference
        )

        self.assertEqual(available_image_bounds, cl.available_image_bounds)
        self.assertEqual(
            cl.available_image_bounds,
            media_reference.available_image_bounds
        )

        self.assertEqual(0.0, cl.available_image_bounds.min.x)
        self.assertEqual(0.0, cl.available_image_bounds.min.y)
        self.assertEqual(16.0, cl.available_image_bounds.max.x)
        self.assertEqual(9.0, cl.available_image_bounds.max.y)

        # test range exceptions
        cl.media_reference.available_image_bounds = None
        with self.assertRaises(otio.exceptions.CannotComputeAvailableRangeError):
            cl.available_range()

    def test_ref_default(self):
        cl = otio.schema.Clip()
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.MissingReference()
        )

        cl.media_reference = None
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.MissingReference()
        )

        cl.media_reference = otio.schema.ExternalReference()
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.ExternalReference()
        )

    def test_multi_ref(self):
        cl = otio.schema.Clip()

        self.assertEqual(
            otio.schema.Clip.DEFAULT_MEDIA_KEY,
            cl.active_media_reference_key
        )
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.MissingReference()
        )

        mrs = cl.media_references()
        self.assertIsOTIOEquivalentTo(
            mrs[otio.schema.Clip.DEFAULT_MEDIA_KEY],
            otio.schema.MissingReference()
        )

        cl.set_media_references(
            {
                otio.schema.Clip.DEFAULT_MEDIA_KEY: otio.schema.ExternalReference(),
                "high_quality": otio.schema.GeneratorReference(),
                "proxy_quality": otio.schema.ImageSequenceReference(),
            },
            otio.schema.Clip.DEFAULT_MEDIA_KEY)

        mrs = cl.media_references()
        self.assertIsOTIOEquivalentTo(
            mrs[otio.schema.Clip.DEFAULT_MEDIA_KEY],
            otio.schema.ExternalReference()
        )
        self.assertIsOTIOEquivalentTo(
            mrs["high_quality"],
            otio.schema.GeneratorReference()
        )
        self.assertIsOTIOEquivalentTo(
            mrs["proxy_quality"],
            otio.schema.ImageSequenceReference()
        )

        cl.active_media_reference_key = "high_quality"
        self.assertIsOTIOEquivalentTo(
            cl.media_reference,
            otio.schema.GeneratorReference()
        )
        self.assertEqual(
            cl.active_media_reference_key,
            "high_quality"
        )

        # we should get an exception if we try to use a key that is
        # not in the media_references
        with self.assertRaises(ValueError):
            cl.active_media_reference_key = "cloud"

        self.assertEqual(
            cl.active_media_reference_key,
            "high_quality"
        )

        # we should also get an exception if we set the references without
        # the active key
        with self.assertRaises(ValueError):
            cl.set_media_references(
                {
                    "cloud": otio.schema.ExternalReference()
                },
                "high_quality"
            )
        self.assertEqual(
            cl.active_media_reference_key,
            "high_quality"
        )

        # we should also get an exception if we set the references with
        # an empty key
        with self.assertRaises(ValueError):
            cl.set_media_references(
                {
                    "": otio.schema.ExternalReference()
                },
                ""
            )
        self.assertEqual(
            cl.active_media_reference_key,
            "high_quality"
        )

        # setting the references and the active key should resolve the problem
        cl.set_media_references(
            {
                "cloud": otio.schema.ExternalReference()
            },
            "cloud"
        )
        self.assertEqual(cl.active_media_reference_key, "cloud")
        self.assertIsOTIOEquivalentTo(
            cl.media_reference, otio.schema.ExternalReference())


if __name__ == '__main__':
    unittest.main()
