import os
import unittest
import opentimelineio as otio

SAMPLE_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_example.fcpxml"
)


class AdaptersFcpXXmlTest(unittest.TestCase, otio.test_utils.OTIOAssertions):
    """
    The test class for the FCP X XML adapter
    """

    def __init__(self, *args, **kwargs):
        super(AdaptersFcpXXmlTest, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def test_roundtrip(self):
        timeline = otio.adapters.read_from_file(SAMPLE_XML)
        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 4)

        video_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Video
        ]
        audio_tracks = [
            t for t in timeline.tracks
            if t.kind == otio.schema.TrackKind.Audio
        ]

        self.assertEqual(len(video_tracks), 3)
        self.assertEqual(len(audio_tracks), 1)

        video_clip_names = (
            ('IMG_0023', None, 'IMG_0268'),
            (None, 'OpenTimelineIO_1 Clip'),
            (None, 'IMG_0715', None, 'IMG_0715')
        )

        for n, track in enumerate(video_tracks):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertTrue(fcpx_xml is not None)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(timeline, new_timeline)


if __name__ == '__main__':
    unittest.main()
