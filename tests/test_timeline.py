#!/usr/bin/env python

import unittest

import opentimelineio as otio


class TimelineTests(unittest.TestCase):

    def test_init(self):
        rt = otio.opentime.RationalTime(12, 24)
        tl = otio.schema.Timeline("test_timeline", global_start_time=rt)
        self.assertEqual(tl.name, "test_timeline")
        self.assertEqual(tl.global_start_time, rt)

    def test_metadata(self):
        rt = otio.opentime.RationalTime(12, 24)
        tl = otio.schema.Timeline("test_timeline", global_start_time=rt)
        tl.metadata['foo'] = "bar"
        self.assertEqual(tl.metadata['foo'], 'bar')

        encoded = otio.adapters.otio_json.write_to_string(tl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(tl, decoded)
        self.assertEqual(tl.metadata, decoded.metadata)

    def test_range(self):
        track = otio.schema.Sequence(name="test_track")
        tl = otio.schema.Timeline("test_timeline", tracks=[track])
        rt = otio.opentime.RationalTime(5, 24)
        mr = otio.media_reference.External(
            available_range=otio.opentime.range_from_start_end_time(
                otio.opentime.RationalTime(5, 24),
                otio.opentime.RationalTime(15, 24)
            ),
            target_url="/var/tmp/test.mov"
        )

        cl = otio.schema.Clip(
            name="test clip1",
            media_reference=mr,
            source_range=otio.opentime.TimeRange(duration=rt),
        )
        cl2 = otio.schema.Clip(
            name="test clip2",
            media_reference=mr,
            source_range=otio.opentime.TimeRange(duration=rt),
        )
        cl3 = otio.schema.Clip(
            name="test clip3",
            media_reference=mr,
            source_range=otio.opentime.TimeRange(duration=rt),
        )
        tl.tracks[0].append(cl)
        tl.tracks[0].extend([cl2, cl3])

        self.assertEqual(tl.duration(), rt + rt + rt)

        self.assertEqual(
            tl.range_of_child(cl),
            tl.tracks[0].range_of_child_at_index(0)
        )

    def test_iterators(self):
        track = otio.schema.Sequence(name="test_track")
        tl = otio.schema.Timeline("test_timeline", tracks=[track])
        rt = otio.opentime.RationalTime(5, 24)
        mr = otio.media_reference.External(
            available_range=otio.opentime.range_from_start_end_time(
                otio.opentime.RationalTime(5, 24),
                otio.opentime.RationalTime(15, 24)
            ),
            target_url="/var/tmp/test.mov"
        )

        cl = otio.schema.Clip(
            name="test clip1",
            media_reference=mr,
            source_range=otio.opentime.TimeRange(
                mr.available_range.start_time,
                rt
            ),
        )
        cl2 = otio.schema.Clip(
            name="test clip2",
            media_reference=mr,
            source_range=otio.opentime.TimeRange(
                mr.available_range.start_time,
                rt
            ),
        )
        cl3 = otio.schema.Clip(
            name="test clip3",
            media_reference=mr,
            source_range=otio.opentime.TimeRange(
                mr.available_range.start_time,
                rt
            ),
        )
        tl.tracks[0].append(cl)
        tl.tracks[0].extend([cl2, cl3])
        self.assertEqual([cl, cl2, cl3], list(tl.each_clip()))

        rt_start = otio.opentime.RationalTime(0, 24)
        rt_end = otio.opentime.RationalTime(1, 24)
        search_range = otio.opentime.TimeRange(rt_start, rt_end)
        self.assertEqual([cl], list(tl.each_clip(search_range)))

    def test_str(self):
        self.maxDiff = None
        clip = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.media_reference.MissingReference()
        )
        track = otio.schema.Sequence(name="test_track", children=[clip])
        tl = otio.schema.Timeline(name="test_timeline", tracks=[track])
        self.assertMultiLineEqual(
            str(tl),
            'Timeline(' +
            '"' + str(tl.name) + '", ' +
            str(tl.tracks) +
            ')'
        )
        self.assertMultiLineEqual(
            repr(tl),
            'otio.schema.Timeline(' +
            "name='" + tl.name + "', " +
            "tracks=" + repr(tl.tracks) +
            ')'
        )

    def test_serialize_timeline(self):
        clip = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.media_reference.MissingReference()
        )
        tl = otio.schema.timeline_from_clips([clip])
        encoded = otio.adapters.otio_json.write_to_string(tl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(tl, decoded)

        string2 = otio.adapters.otio_json.write_to_string(decoded)
        self.assertEqual(encoded, string2)

    def test_serialization_of_subclasses(self):
        clip1 = otio.schema.Clip()
        clip1.name = "Test Clip"
        clip1.media_reference = otio.media_reference.External(
            "/tmp/foo.mov"
        )
        tl1 = otio.schema.timeline_from_clips([clip1])
        tl1.name = "Testing Serialization"
        self.assertIsNotNone(tl1)
        otio_module = otio.adapters.from_name("otio_json")
        serialized = otio_module.write_to_string(tl1)
        self.assertIsNotNone(serialized)
        tl2 = otio_module.read_from_string(serialized)
        self.assertIsNotNone(tl2)
        self.assertEqual(type(tl1), type(tl2))
        self.assertEqual(tl1.name, tl2.name)
        self.assertEqual(len(tl1.tracks), 1)
        self.assertEqual(len(tl2.tracks), 1)
        track1 = tl1.tracks[0]
        track2 = tl2.tracks[0]
        self.assertEqual(type(track1), type(track2))
        self.assertEqual(len(track1), 1)
        self.assertEqual(len(track2), 1)
        clip2 = tl2.tracks[0][0]
        self.assertEqual(clip1.name, clip2.name)
        self.assertEqual(type(clip1), type(clip2))
        self.assertEqual(
            type(clip1.media_reference),
            type(clip2.media_reference)
        )
        self.assertEqual(
            clip1.media_reference.target_url,
            clip2.media_reference.target_url
        )

if __name__ == '__main__':
    unittest.main()
