# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest
import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
import opentimelineio_contrib.adapters.kdenlive as kdenlive_adapter
import os
from xml.etree import ElementTree as ET


def prepare_for_check(timeline):
    """Clear the given timeline of irrelevant data
    For example since Kdenlive only supports one timeline,
    we do not care about its name. Same applies to reference names."""
    timeline.name = ""
    for track in timeline.tracks:
        for clip in track.clip_if():
            if isinstance(clip.media_reference, list):
                for reference in clip.media_reference:
                    reference.name = ""
            else:
                clip.media_reference.name = ""


class AdaptersKdenliveTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_library_roundtrip(self):
        timeline = otio.adapters.read_from_file(
            os.path.join(os.path.dirname(__file__), "sample_data",
                         "kdenlive_example_v221170.kdenlive"))

        # check tracks
        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 5)

        self.assertEqual(len(timeline.video_tracks()), 2)
        self.assertEqual(len(timeline.audio_tracks()), 3)

        # check clips
        clip_urls = (('AUD0002.OGG',),
                     ('AUD0001.OGG', 'AUD0001.OGG'),
                     ('VID0001.MKV', 'VID0001.MKV'),
                     ('VID0001.MKV', 'VID0001.MKV'),
                     ('VID0002.MKV', 'VID0003.MKV'))

        for n, track in enumerate(timeline.tracks):
            self.assertTupleEqual(
                clip_urls[n],
                tuple(c.media_reference.target_url
                      for c in track
                      if isinstance(c, otio.schema.Clip) and
                      isinstance(
                          c.media_reference,
                          otio.schema.ExternalReference)))

        # check timeline markers
        self.assertEqual(len(timeline.tracks.markers), 2)

        markers_data = ((230, 'Purple Marker', otio.schema.MarkerColor.PURPLE),
                        (466, 'Green', otio.schema.MarkerColor.GREEN))

        for n, marker in enumerate(timeline.tracks.markers):
            self.assertEqual(0, marker.marked_range.duration.value)
            self.assertEqual(markers_data[n][0],
                             marker.marked_range.start_time.value)
            self.assertEqual(markers_data[n][1], marker.name)
            self.assertEqual(markers_data[n][2], marker.color)

        kdenlive_xml = otio.adapters.write_to_string(timeline, "kdenlive")
        self.assertIsNotNone(kdenlive_xml)

        new_timeline = otio.adapters.read_from_string(kdenlive_xml, "kdenlive")
        self.assertJsonEqual(timeline, new_timeline)

    def test_v19_11_80__file_roundtrip(self):
        timeline = otio.adapters.read_from_file(
            os.path.join(os.path.dirname(__file__), "sample_data",
                         "kdenlive_example_v191180.kdenlive"))

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 5)

        self.assertEqual(len(timeline.video_tracks()), 2)
        self.assertEqual(len(timeline.audio_tracks()), 3)

        clip_urls = (('AUD0002.OGG',),
                     ('AUD0001.OGG', 'AUD0001.OGG'),
                     ('VID0001.MKV', 'VID0001.MKV'),
                     ('VID0001.MKV', 'VID0001.MKV'),
                     ('VID0002.MKV', 'VID0003.MKV'))

        for n, track in enumerate(timeline.tracks):
            self.assertTupleEqual(
                clip_urls[n],
                tuple(c.media_reference.target_url
                      for c in track
                      if isinstance(c, otio.schema.Clip) and
                      isinstance(
                          c.media_reference,
                          otio.schema.ExternalReference)))

        kdenlive_xml = otio.adapters.write_to_string(timeline, "kdenlive")
        self.assertIsNotNone(kdenlive_xml)

        new_timeline = otio.adapters.read_from_string(kdenlive_xml, "kdenlive")
        self.assertJsonEqual(timeline, new_timeline)

    def test_from_fcp_example(self):
        timeline = otio.adapters.read_from_file(
            os.path.join(
                os.path.dirname(__file__),
                "sample_data",
                "kdenlive_example_from_fcp.xml",
            ),
        )

        kdenlive_xml = otio.adapters.write_to_string(timeline, "kdenlive")
        self.assertIsNotNone(kdenlive_xml)

        new_timeline = otio.adapters.read_from_string(kdenlive_xml, "kdenlive")
        troublesome_clip = new_timeline.video_tracks()[0][35]
        self.assertEqual(
            troublesome_clip.source_range.duration.value,
            807,
        )

    def test_read_mixes(self):
        # mixes are yet only supported to be read, not written
        timeline = otio.adapters.read_from_file(
            os.path.join(os.path.dirname(__file__), "sample_data",
                         "kdenlive_mixes_markers.kdenlive"))

        # check tracks
        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        video_tracks = timeline.video_tracks()
        audio_tracks = timeline.audio_tracks()
        self.assertEqual(len(video_tracks), 2)
        self.assertEqual(len(audio_tracks), 2)

        # check items
        video_track_normal = video_tracks[0]
        video_track_mix = video_tracks[1]

        audio_track_normal = audio_tracks[1]
        audio_track_mix = audio_tracks[0]

        self.assertEqual(len(video_track_normal), 10)
        self.assertEqual(len(audio_track_normal), 10)
        self.assertEqual(len(video_track_mix), 15)
        self.assertEqual(len(audio_track_mix), 15)

        clips_normal = list(video_track_normal.clip_if())
        self.assertEqual(len(clips_normal), 8)
        clips_mix = list(video_track_mix.clip_if())
        self.assertEqual(len(clips_mix), 8)

        normal_item_order = [
            otio.schema.Clip,
            otio.schema.Clip,
            otio.schema.Gap,
            otio.schema.Clip,
            otio.schema.Clip,
            otio.schema.Clip,
            otio.schema.Clip,
            otio.schema.Gap,
            otio.schema.Clip,
            otio.schema.Clip
        ]
        self.assertEqual(
            [type(item) for item in video_track_normal],
            normal_item_order
        )
        self.assertEqual(
            [type(item) for item in audio_track_normal],
            normal_item_order
        )

        mix_item_order = [
            otio.schema.Clip,
            otio.schema.Transition,
            otio.schema.Clip,
            otio.schema.Gap,
            otio.schema.Clip,
            otio.schema.Transition,
            otio.schema.Clip,
            otio.schema.Transition,
            otio.schema.Clip,
            otio.schema.Transition,
            otio.schema.Clip,
            otio.schema.Gap,
            otio.schema.Clip,
            otio.schema.Transition,
            otio.schema.Clip
        ]
        self.assertEqual(
            [type(item) for item in video_track_mix],
            mix_item_order
        )
        self.assertEqual(
            [type(item) for item in audio_track_mix],
            mix_item_order
        )

        def only_transitions(item):
            return isinstance(item, otio.schema.Transition)

        mix_times = ((13, 25),
                     (25, 25),
                     (0, 25),
                     (115, 214),
                     (44, 114))
        for x, mix in enumerate(filter(only_transitions, video_track_mix)):
            duration = mix.in_offset.value + mix.out_offset.value
            self.assertEqual(mix.in_offset.value, mix_times[x][0])
            self.assertEqual(duration, mix_times[x][1])

        mix_times = ((13, 25),
                     (13, 25),
                     (119, 131),
                     (13, 25),
                     (44, 114))
        for x, mix in enumerate(filter(only_transitions, audio_track_mix)):
            duration = mix.in_offset.value + mix.out_offset.value
            self.assertEqual(mix.in_offset.value, mix_times[x][0])
            self.assertEqual(duration, mix_times[x][1])

    def test_fun_read_mix(self):
        rate = 25
        mix = ET.Element(
            'transition',
            {"in": '00:00:11.000', "out": '00:00:13.000'},
        )
        mixcut = ET.SubElement(mix, 'property', {'name': 'kdenlive:mixcut'})
        mixcut.text = '16'
        reverese_prop = ET.SubElement(mix, 'property', {'name': 'reverse'})
        reverese_prop.text = '1'
        (mix_range, before_mix_cut,
         after_mix_cut, reverse) = kdenlive_adapter.read_mix(mix, rate)
        self.assertIsNotNone(mix_range)
        self.assertIsNotNone(before_mix_cut)
        self.assertIsNotNone(after_mix_cut)
        self.assertIsNotNone(reverse)
        self.assertEqual(mix_range, otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(11 * rate, rate),
            duration=otio.opentime.RationalTime(2 * rate, rate)
        ))
        self.assertEqual(before_mix_cut, otio.opentime.RationalTime(16, rate))
        self.assertEqual(after_mix_cut,
                         otio.opentime.RationalTime(2 * rate, rate)
                         - otio.opentime.RationalTime(16, rate))
        self.assertEqual(reverse, True)

    def test_read_clip_markers(self):
        # clip markers are yet only supported to be read, not written
        timeline = otio.adapters.read_from_file(
            os.path.join(os.path.dirname(__file__), "sample_data",
                         "kdenlive_mixes_markers.kdenlive"))

        # check tracks
        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        video_tracks = timeline.video_tracks()
        audio_tracks = timeline.audio_tracks()
        self.assertEqual(len(video_tracks), 2)
        self.assertEqual(len(audio_tracks), 2)

        def only_clips(item):
            return isinstance(item, otio.schema.Clip)

        for track in timeline.tracks:
            for clip in filter(only_clips, track):
                self.assertEqual(len(clip.markers), 2)

                markers_data = (
                    (1782, 'Lila', otio.schema.MarkerColor.PURPLE),
                    (2899, 'Orange', otio.schema.MarkerColor.ORANGE))

                for n, marker in enumerate(clip.markers):
                    self.assertEqual(0, marker.marked_range.duration.value)
                    self.assertEqual(markers_data[n][0],
                                     marker.marked_range.start_time.value)
                    self.assertEqual(markers_data[n][1], marker.name)
                    self.assertEqual(markers_data[n][2], marker.color)

    def test_smpte_bars(self):
        timeline = otio.adapters.read_from_file(
            os.path.join(
                os.path.dirname(__file__),
                "sample_data",
                "generator_reference_test.otio",
            ),
        )

        kdenlive_xml = otio.adapters.write_to_string(timeline, "kdenlive")
        self.assertIsNotNone(kdenlive_xml)

        new_timeline = otio.adapters.read_from_string(kdenlive_xml, "kdenlive")
        prepare_for_check(timeline)
        prepare_for_check(new_timeline)
        self.assertIsOTIOEquivalentTo(timeline, new_timeline)


if __name__ == '__main__':
    unittest.main()
