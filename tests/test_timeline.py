#
# Copyright Contributors to the OpenTimelineIO project
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

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


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
        self.assertEqual([cl, cl2, cl3], list(tl.each_clip()))

        rt_start = otio.opentime.RationalTime(0, 24)
        rt_end = otio.opentime.RationalTime(1, 24)
        search_range = otio.opentime.TimeRange(rt_start, rt_end)
        self.assertEqual([cl], list(tl.each_clip(search_range)))

        # check to see if full range works
        search_range = tl.tracks.trimmed_range()
        self.assertEqual([cl, cl2, cl3], list(tl.each_clip(search_range)))

        # just one clip
        search_range = cl2.range_in_parent()
        self.assertEqual([cl2], list(tl.each_clip(search_range)))

        # the last two clips
        search_range = otio.opentime.TimeRange(
            start_time=cl2.range_in_parent().start_time,
            duration=cl2.trimmed_range().duration + rt_end
        )
        self.assertEqual([cl2, cl3], list(tl.each_clip(search_range)))

        # no clips
        search_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(
                value=-10,
                rate=rt_start.rate
            ),
            duration=rt_end
        )
        self.assertEqual([], list(tl.each_clip(search_range)))

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


if __name__ == '__main__':
    unittest.main()
