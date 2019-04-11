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
        container = otio.adapters.read_from_file(SAMPLE_XML)
        timeline = next(
            container.each_child(descended_from_type=otio.schema.Timeline)
        )

        self.assertIsNotNone(timeline)
        self.assertEqual(len(timeline.tracks), 4)

        self.assertEqual(len(timeline.video_tracks()), 3)
        self.assertEqual(len(timeline.audio_tracks()), 1)

        video_clip_names = (
            (
                'IMG_0715',
                "",
                'compound_clip_1',
                'IMG_0233',
                'IMG_0687',
                'IMG_0268',
                'compound_clip_1'
            ),
            ("", 'IMG_0513', "", 'IMG_0268', 'IMG_0740'),
            ("", 'IMG_0857')
        )

        for n, track in enumerate(timeline.video_tracks()):
            self.assertTupleEqual(
                tuple(c.name for c in track),
                video_clip_names[n]
            )

        fcpx_xml = otio.adapters.write_to_string(container, "fcpx_xml")
        self.assertIsNotNone(fcpx_xml)

        new_timeline = otio.adapters.read_from_string(fcpx_xml, "fcpx_xml")
        self.assertJsonEqual(container, new_timeline)


if __name__ == '__main__':
    unittest.main()
