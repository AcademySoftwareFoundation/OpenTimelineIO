# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test harness for Media References."""

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils
from opentimelineio.schema import StreamInfo

import unittest


class MediaReferenceTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(5, 24), otio.opentime.RationalTime(10, 24.0)
        )
        mr = otio.schema.MissingReference(
            available_range=tr, metadata={"show": "OTIOTheMovie"}
        )

        self.assertEqual(mr.available_range, tr)

        mr = otio.schema.MissingReference()
        self.assertIsNone(mr.available_range)
        self.assertEqual(mr.available_streams(), {})

    def test_str_missing(self):
        missing = otio.schema.MissingReference()
        self.assertMultiLineEqual(str(missing), "MissingReference('', None, None, {})")
        self.assertMultiLineEqual(
            repr(missing),
            "otio.schema.MissingReference("
            "name='', available_range=None, available_image_bounds=None, metadata={}"
            ")",
        )

        encoded = otio.adapters.otio_json.write_to_string(missing)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(missing, decoded)

    def test_filepath(self):
        filepath = otio.schema.ExternalReference("/var/tmp/foo.mov")
        self.assertMultiLineEqual(
            str(filepath), 'ExternalReference("/var/tmp/foo.mov")'
        )
        self.assertMultiLineEqual(
            repr(filepath),
            "otio.schema.ExternalReference(target_url='/var/tmp/foo.mov')",
        )

        # round trip serialize
        encoded = otio.adapters.otio_json.write_to_string(filepath)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(filepath, decoded)

    def test_equality(self):
        filepath = otio.schema.ExternalReference(target_url="/var/tmp/foo.mov")
        filepath2 = otio.schema.ExternalReference(target_url="/var/tmp/foo.mov")
        self.assertIsOTIOEquivalentTo(filepath, filepath2)

        bl = otio.schema.MissingReference()
        self.assertNotEqual(filepath, bl)

        filepath2 = otio.schema.ExternalReference(target_url="/var/tmp/foo2.mov")
        self.assertNotEqual(filepath, filepath2)
        self.assertEqual(filepath == filepath2, False)

    def test_is_missing(self):
        mr = otio.schema.ExternalReference(target_url="/var/tmp/foo.mov")
        self.assertFalse(mr.is_missing_reference)

        mr = otio.schema.MissingReference()
        self.assertTrue(mr.is_missing_reference)


class TestAvailableStreamsOnMediaReference(unittest.TestCase):
    def test_set_and_get_available_streams(self):
        ref = otio.schema.ExternalReference(target_url="/foo/bar.mov")
        video_info = StreamInfo(
            name="left eye 4K",
            address=otio.schema.IndexStreamAddress(index=0),
            kind=otio.schema.TrackKind.Video,
        )
        audio_left = StreamInfo(
            name="left channel",
            address=otio.schema.IndexStreamAddress(index=1),
            kind=otio.schema.TrackKind.Audio,
        )
        ref.set_available_streams(
            {
                StreamInfo.Identifier.left_eye: video_info,
                StreamInfo.Identifier.stereo_left: audio_left,
            }
        )
        streams = ref.available_streams()
        self.assertIn(StreamInfo.Identifier.left_eye, streams)
        self.assertIn(StreamInfo.Identifier.stereo_left, streams)
        self.assertIsInstance(streams[StreamInfo.Identifier.left_eye], StreamInfo)
        self.assertEqual(
            streams[StreamInfo.Identifier.left_eye].kind, otio.schema.TrackKind.Video
        )
        self.assertEqual(
            streams[StreamInfo.Identifier.stereo_left].kind, otio.schema.TrackKind.Audio
        )

    def test_round_trip_serialization(self):
        ref = otio.schema.ExternalReference(target_url="/show/shot.mov")
        ref.set_available_streams(
            {
                StreamInfo.Identifier.left_eye: StreamInfo(
                    name="v0_left",
                    address=otio.schema.IndexStreamAddress(index=0),
                    kind=otio.schema.TrackKind.Video,
                ),
                StreamInfo.Identifier.stereo_left: StreamInfo(
                    name="a1_left",
                    address=otio.schema.IndexStreamAddress(index=1),
                    kind=otio.schema.TrackKind.Audio,
                ),
            }
        )
        json_str = ref.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.ExternalReference)
        self.assertEqual(restored.target_url, "/show/shot.mov")
        streams = restored.available_streams()
        self.assertIn(StreamInfo.Identifier.left_eye, streams)
        self.assertIn(StreamInfo.Identifier.stereo_left, streams)
        self.assertEqual(
            streams[StreamInfo.Identifier.left_eye].kind, otio.schema.TrackKind.Video
        )
        self.assertEqual(
            streams[StreamInfo.Identifier.stereo_left].kind, otio.schema.TrackKind.Audio
        )
        self.assertIsInstance(
            streams[StreamInfo.Identifier.left_eye].address,
            otio.schema.IndexStreamAddress,
        )
        self.assertEqual(streams[StreamInfo.Identifier.left_eye].address.index, 0)


if __name__ == "__main__":
    unittest.main()
