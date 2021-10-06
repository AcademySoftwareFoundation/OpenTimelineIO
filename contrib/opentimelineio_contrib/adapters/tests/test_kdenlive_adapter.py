import unittest
import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
import os


class AdaptersKdenliveTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def __init__(self, *args, **kwargs):
        super(AdaptersKdenliveTest, self).__init__(*args, **kwargs)

    def test_library_roundtrip(self):
        timeline = otio.adapters.read_from_file(
            os.path.join(os.path.dirname(__file__), "sample_data",
                         "kdenlive_example.kdenlive"))

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


if __name__ == '__main__':
    unittest.main()
