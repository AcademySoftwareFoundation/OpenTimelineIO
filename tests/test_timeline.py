#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import math
import os
import sys
import unittest

import tempfile

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
BIG_INT_TEST = os.path.join(SAMPLE_DATA_DIR, "big_int.otio")


class TimelineTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

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
        self.assertIsOTIOEquivalentTo(tl, decoded)
        self.assertEqual(tl.metadata, decoded.metadata)

    def test_big_integers(self):
        result = otio.adapters.read_from_file(BIG_INT_TEST)

        md = result.tracks[0][0].metadata["int_test"]

        # test the deserialized values from the file

        # positive integers
        self.assertEqual(md["maxint32"], 2147483647)
        self.assertEqual(md["smallest_int64"], 2147483648)
        self.assertEqual(md["verybig"], 3450100000)

        # negative
        self.assertEqual(md["minint32"], -2147483647)
        self.assertEqual(md["neg_smallest_int64"], -2147483648)
        self.assertEqual(md["negverybig"], -3450100000)

        # from memory
        supported_integers = [
            # name       value to enter
            ('minint32', -int(2**31 - 1)),
            ('maxint32', int(2**31 - 1)),
            ('maxuint32', int(2**32 - 1)),
            ('minint64', -int(2**63 - 1)),
            ('maxint64', int(2**63 - 1)),
        ]

        for (name, value) in supported_integers:
            md[name] = value
            self.assertEqual(
                md[name],
                value,
                "{} didn't match expected value: got {} expected {}".format(
                    name,
                    md[name],
                    value
                )
            )
            self.assertEqual(
                type(md[name]),
                int,
                "{} didn't match expected type: got {} expected {}".format(
                    name,
                    type(md[name]),
                    int
                )
            )

            # test that roundtripping through json functions
            serialized = otio.adapters.write_to_string(
                result,
                "otio_json"
            )
            deserialized = otio.adapters.read_from_string(
                serialized,
                "otio_json"
            )

            value_deserialized = (
                deserialized.tracks[0][0].metadata["int_test"][name]
            )
            self.assertEqual(
                value,
                value_deserialized,
                "{} did not round trip correctly.  expected: {} got: {}".format(
                    name,
                    value,
                    value_deserialized
                )
            )
            self.assertEqual(
                type(value),
                type(value_deserialized),
                "the type of {} did not round trip correctly.  expected: "
                "{} got: {}".format(
                    name,
                    type(value),
                    type(value_deserialized)
                )
            )

        supported_doubles = [
            # name       value to enter
            ('minint32', -float(2**31 - 1)),
            ('maxint32', float(2**31 - 1)),
            ('maxuint32', float(2**32 - 1)),
            ('minint64', -float(2**63 - 1)),
            ('maxint64', float(2**63 - 1)),
            ('maxdouble', sys.float_info.max),
            ('infinity', float('inf')),
            ('infinity_because_too_big', float(2 * sys.float_info.max)),
            ('nan', float('nan')),
            ('neg_infinity', float('-inf')),
        ]

        for (name, value) in supported_doubles:
            md[name] = value

            # float('nan') != float('nan'), so need ot test isnan(value) instead
            if not math.isnan(value):
                self.assertEqual(
                    md[name],
                    value,
                    "{} didn't match expected value: got '{}' ('{}') expected "
                    "'{}' ('{}')".format(
                        name,
                        md[name],
                        type(md[name]),
                        value,
                        type(value)
                    )
                )
            else:
                self.assertTrue(
                    math.isnan(md[name]),
                    f"Expected {name} to be a nan, got {md[name]}"
                )

            self.assertEqual(
                type(md[name]),
                float,
                "{} didn't match expected type: got {} expected {}".format(
                    name,
                    type(md[name]),
                    float
                )
            )

            # test that roundtripping through json functions
            try:
                serialized = otio.adapters.write_to_string(
                    result,
                    "otio_json"
                )
            except Exception as e:
                self.fail(
                    "A problem occured when attempting to serialize {} "
                    "with value: {}.  Error message was: {}".format(
                        name,
                        value,
                        e
                    )
                )

            try:
                deserialized = otio.adapters.read_from_string(
                    serialized,
                    "otio_json"
                )
            except Exception as e:
                self.fail(
                    "A problem occured when attempting to serialize {} "
                    "with value: {}.  Error message was: {}".format(
                        name,
                        value,
                        e
                    )
                )

            value_deserialized = (
                deserialized.tracks[0][0].metadata["int_test"][name]
            )

            if not math.isnan(value):
                self.assertEqual(
                    value,
                    value_deserialized,
                    "{} did not round trip correctly.  expected: {}, of type {} "
                    "got: {}, of type {}".format(
                        name,
                        value,
                        type(value),
                        value_deserialized,
                        type(value_deserialized),
                    )
                )
            else:
                self.assertTrue(
                    math.isnan(value_deserialized),
                    "Expected {} to be a nan, got {}".format(
                        name,
                        value_deserialized
                    )
                )

        unsupported_values = [
            # numbers -- supported python type but don't fit into the C++ types
            #            (ie int but doesn't fit into int64_t)
            ('minuint64_not_int64', int(2**63), ValueError),
            ('maxuint64', int(2**64 - 1), ValueError),
            ('minint128', int(2**64), ValueError),

            # other kinds of python things
            ('object', object(), TypeError),
            ('set', set(), TypeError),
        ]

        for (name, value, exc) in unsupported_values:
            with self.assertRaises(
                    exc,
                    msg=f"Expected {name} to raise an exception."
            ):
                md[name] = value

    def test_unicode(self):
        result = otio.adapters.read_from_file(BIG_INT_TEST)

        md = result.tracks[0][0].metadata['unicode']

        utf8_test_str = "Viel glück und hab spaß!"

        self.assertEqual(md['utf8'], utf8_test_str)

        tl = otio.schema.Timeline()

        tl.metadata['utf8'] = utf8_test_str
        self.assertEqual(tl.metadata['utf8'], utf8_test_str)

        encoded = otio.adapters.otio_json.write_to_string(tl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(tl, decoded)
        self.assertEqual(tl.metadata, decoded.metadata)

    def test_unicode_file_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:

            tl = otio.schema.Timeline("大平原")
            filename = os.path.join(temp_dir, "大平原.otio")
            otio.adapters.write_to_file(tl, filename)

            result = otio.adapters.read_from_file(filename)
            self.assertEqual(result.name, "大平原")

    def test_range(self):
        track = otio.schema.Track(name="test_track")
        tl = otio.schema.Timeline("test_timeline", tracks=[track])
        rt = otio.opentime.RationalTime(5, 24)
        mr = otio.schema.ExternalReference(
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

    def test_available_image_bounds(self):
        track = otio.schema.Track(name="test_track")
        tl = otio.schema.Timeline("test_timeline", tracks=[track])

        # three clips, each successive clip partially overlaps the previous
        cl = otio.schema.Clip(
            name="test clip1",
            media_reference=otio.schema.ExternalReference(
                available_image_bounds=otio.schema.Box2d(
                    otio.schema.V2d(0.0, 0.0),
                    otio.schema.V2d(1.0, 1.0)
                ),
                target_url="/var/tmp/test.mov"
            )
        )
        cl2 = otio.schema.Clip(
            name="test clip2",
            media_reference=otio.schema.ExternalReference(
                available_image_bounds=otio.schema.Box2d(
                    otio.schema.V2d(1.0, 1.0),
                    otio.schema.V2d(2.0, 2.0)
                ),
                target_url="/var/tmp/test.mov"
            )
        )
        cl3 = otio.schema.Clip(
            name="test clip3",
            media_reference=otio.schema.ExternalReference(
                available_image_bounds=otio.schema.Box2d(
                    otio.schema.V2d(2.0, 2.0),
                    otio.schema.V2d(3.0, 3.0)
                ),
                target_url="/var/tmp/test.mov"
            )
        )
        gap = otio.schema.Gap(name="gap")

        tl.tracks[0].append(cl)
        tl.tracks[0].extend([cl2, cl3, gap])

        union = otio.schema.Box2d(
            otio.schema.V2d(0.0, 0.0),
            otio.schema.V2d(3.0, 3.0)
        )

        # union should be overlapping area, gap should be ignored
        self.assertEqual(tl.tracks[0].available_image_bounds, union)

    def test_iterators(self):
        self.maxDiff = None
        track = otio.schema.Track(name="test_track")
        tl = otio.schema.Timeline("test_timeline", tracks=[track])
        rt = otio.opentime.RationalTime(5, 24)
        mr = otio.schema.ExternalReference(
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
        self.assertEqual([cl, cl2, cl3], list(tl.clip_if()))

        rt_start = otio.opentime.RationalTime(0, 24)
        rt_end = otio.opentime.RationalTime(1, 24)
        search_range = otio.opentime.TimeRange(rt_start, rt_end)
        self.assertEqual([cl], list(tl.clip_if(search_range)))

        # check to see if full range works
        search_range = tl.tracks.trimmed_range()
        self.assertEqual([cl, cl2, cl3], list(tl.clip_if(search_range)))

        # just one clip
        search_range = cl2.range_in_parent()
        self.assertEqual([cl2], list(tl.clip_if(search_range)))

        # the last two clips
        search_range = otio.opentime.TimeRange(
            start_time=cl2.range_in_parent().start_time,
            duration=cl2.trimmed_range().duration + rt_end
        )
        self.assertEqual([cl2, cl3], list(tl.clip_if(search_range)))

        # no clips
        search_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(
                value=-10,
                rate=rt_start.rate
            ),
            duration=rt_end
        )
        self.assertEqual([], list(tl.clip_if(search_range)))

    def test_str(self):
        self.maxDiff = None
        clip = otio.schema.Clip(
            name="test_clip",
            media_reference=otio.schema.MissingReference()
        )
        track = otio.schema.Track(name="test_track", children=[clip])
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
            media_reference=otio.schema.MissingReference()
        )
        tl = otio.schema.timeline_from_clips([clip])
        encoded = otio.adapters.otio_json.write_to_string(tl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(tl, decoded)

        string2 = otio.adapters.otio_json.write_to_string(decoded)
        self.assertEqual(encoded, string2)

    def test_serialization_of_subclasses(self):
        clip1 = otio.schema.Clip()
        clip1.name = "Test Clip"
        clip1.media_reference = otio.schema.ExternalReference(
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

    def test_tracks(self):
        tl = otio.schema.Timeline(tracks=[
            otio.schema.Track(
                name="V1",
                kind=otio.schema.TrackKind.Video
            ),
            otio.schema.Track(
                name="V2",
                kind=otio.schema.TrackKind.Video
            ),
            otio.schema.Track(
                name="A1",
                kind=otio.schema.TrackKind.Audio
            ),
            otio.schema.Track(
                name="A2",
                kind=otio.schema.TrackKind.Audio
            ),
        ])
        self.assertListEqual(
            ["V1", "V2"],
            [t.name for t in tl.video_tracks()]
        )
        self.assertListEqual(
            ["A1", "A2"],
            [t.name for t in tl.audio_tracks()]
        )

    def test_tracks_set_null_tracks(self):
        tl = otio.schema.Timeline(tracks=[
            otio.schema.Track(
                name="V1",
                kind=otio.schema.TrackKind.Video
            ),
            otio.schema.Track(
                name="V2",
                kind=otio.schema.TrackKind.Video
            )])

        self.assertEqual(len(tl.tracks), 2)
        self.assertTrue(isinstance(tl.tracks, otio.schema.Stack))
        tl.tracks = None
        self.assertEqual(len(tl.audio_tracks()), 0)
        self.assertEqual(len(tl.video_tracks()), 0)
        self.assertTrue(isinstance(tl.tracks, otio.schema.Stack))

    def test_children_if(self):
        cl = otio.schema.Clip()
        tr = otio.schema.Track()
        tr.append(cl)
        tl = otio.schema.Timeline()
        tl.tracks.append(tr)
        result = tl.children_if(otio.schema.Clip)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl)

    def test_children_if_search_range(self):
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
        tl = otio.schema.Timeline()
        tl.tracks.append(tr)
        result = tl.children_if(otio.schema.Clip, range)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl0)

    def test_children_if_shallow_search(self):
        cl = otio.schema.Clip()
        tr = otio.schema.Track()
        tr.append(cl)
        tl = otio.schema.Timeline()
        tl.tracks.append(tr)
        result = tl.children_if(otio.schema.Clip, shallow_search=True)
        self.assertEqual(len(result), 0)
        result = tl.children_if(otio.schema.Clip, shallow_search=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl)


if __name__ == '__main__':
    unittest.main()
