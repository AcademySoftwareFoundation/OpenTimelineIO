import os
import unittest
import opentimelineio as otio

SAMPLE_XML = os.path.join(
    os.path.dirname(__file__),
    "sample_data",
    "fcpx_example.fcpxml"
)


class AdaptersFcpXXmlTest(unittest.TestCase, otio.test_utils.OTIOAssertions):
    def __init__(self, *args, **kwargs):
        super(AdaptersFcpXXmlTest, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def test_read(self):
        timeline = otio.adapters.read_from_file(SAMPLE_XML)
        self.assertTrue(timeline is not None)
        self.assertEqual(len(timeline.tracks), 4)

        xml = otio.adapters.write_to_string(timeline, "fcpx_xml")
        self.assertTrue(xml is not None)


if __name__ == '__main__':
    unittest.main()
