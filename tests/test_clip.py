#!/usr/bin/env python

import unittest

import opentimelineio as otio


class ClipTests(unittest.TestCase):

    def test_cons(self):
        name = "test"
        rt = otio.opentime.RationalTime(5, 24)
        tr = otio.opentime.TimeRange(rt, rt)
        mr = otio.media_reference.External(
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
        self.assertEqual(cl.media_reference, mr)
        self.assertEqual(cl.source_range, tr)

        encoded = otio.adapters.otio_json.write_to_string(cl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(cl, decoded)

    def test_each_clip(self):
        cl = otio.schema.Clip(name="test_clip")
        self.assertEqual(list(cl.each_clip()), [cl])

    def test_str(self):
        cl = otio.schema.Clip(name="test_clip")

        self.assertMultiLineEqual(
            str(cl),
            'Clip("test_clip", MissingReference(), None)'
        )
        self.assertMultiLineEqual(
            repr(cl),
            'otio.schema.Clip('
            "name='test_clip', "
            'media_reference=otio.media_reference.MissingReference(), '
            'source_range=None'
            ')'
        )

    def test_str_with_filepath(self):
        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.media_reference.External(
                "/var/tmp/foo.mov"
            )
        )
        self.assertMultiLineEqual(
            str(cl),
            'Clip("test_clip", External("/var/tmp/foo.mov"), None)'
        )
        self.assertMultiLineEqual(
            repr(cl),
            'otio.schema.Clip('
            "name='test_clip', "
            "media_reference=otio.media_reference.External("
            "target_url='/var/tmp/foo.mov'"
            "), "
            'source_range=None'
            ')'
        )

    def test_computed_duration(self):
        tr = otio.opentime.TimeRange(
            # 1 hour in at 24 fps
            start_time=otio.opentime.RationalTime(86400, 24),
            duration=otio.opentime.RationalTime(200, 24)
        )

        cl = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.media_reference.External(
                "/var/tmp/foo.mov",
                available_range=tr
            )
        )
        self.assertEqual(cl.duration(), cl.computed_duration())
        self.assertEqual(cl.duration(), tr.duration)
        cl.source_range = otio.opentime.TimeRange(
            # 1 hour + 100 frames
            start_time=otio.opentime.RationalTime(86500, 24),
            duration=otio.opentime.RationalTime(50, 24)
        )
        self.assertNotEqual(cl.duration(), tr.duration)
        self.assertEqual(cl.duration(), cl.source_range.duration)

if __name__ == '__main__':
    unittest.main()
