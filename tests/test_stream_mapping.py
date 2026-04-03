# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Tests for stream mapping schemas."""

import unittest
import opentimelineio as otio
from opentimelineio.schema import StreamInfo


class TestIndexStreamAddress(unittest.TestCase):
    def test_create_default(self):
        addr = otio.schema.IndexStreamAddress()
        self.assertEqual(addr.index, 0)
        self.assertEqual(addr.schema_name(), "IndexStreamAddress")
        self.assertEqual(addr.schema_version(), 1)

    def test_create_with_index(self):
        addr = otio.schema.IndexStreamAddress(index=3)
        self.assertEqual(addr.index, 3)

    def test_set_index(self):
        addr = otio.schema.IndexStreamAddress()
        addr.index = 7
        self.assertEqual(addr.index, 7)

    def test_round_trip_serialization(self):
        addr = otio.schema.IndexStreamAddress(index=5)
        json_str = addr.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.IndexStreamAddress)
        self.assertEqual(restored.index, 5)


class TestStringStreamAddress(unittest.TestCase):
    def test_create_default(self):
        addr = otio.schema.StringStreamAddress()
        self.assertEqual(addr.address, "")
        self.assertEqual(addr.schema_name(), "StringStreamAddress")
        self.assertEqual(addr.schema_version(), 1)

    def test_create_with_address(self):
        addr = otio.schema.StringStreamAddress(address="/World/potatoSet/cam1")
        self.assertEqual(addr.address, "/World/potatoSet/cam1")

    def test_set_address(self):
        addr = otio.schema.StringStreamAddress()
        addr.address = "/World/potatoSet/cam1"
        self.assertEqual(addr.address, "/World/potatoSet/cam1")

    def test_round_trip_serialization(self):
        addr = otio.schema.StringStreamAddress(address="/World/potatoSet/cam1")
        json_str = addr.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.StringStreamAddress)
        self.assertEqual(restored.address, "/World/potatoSet/cam1")


class TestStreamInfo(unittest.TestCase):
    def test_create_default(self):
        info = otio.schema.StreamInfo()
        self.assertEqual(info.name, "")
        self.assertIsNone(info.address)
        self.assertEqual(info.kind, "")
        self.assertEqual(info.metadata, {})
        self.assertEqual(info.schema_name(), "StreamInfo")
        self.assertEqual(info.schema_version(), 1)

    def test_create_with_fields(self):
        addr = otio.schema.IndexStreamAddress(index=0)
        info = otio.schema.StreamInfo(
            name="main_video", address=addr, kind=otio.schema.TrackKind.Video
        )
        self.assertEqual(info.name, "main_video")
        self.assertIsInstance(info.address, otio.schema.IndexStreamAddress)
        self.assertEqual(info.address.index, 0)
        self.assertEqual(info.kind, otio.schema.TrackKind.Video)

    def test_round_trip_with_index_address(self):
        addr = otio.schema.IndexStreamAddress(index=2)
        info = otio.schema.StreamInfo(
            name="audio_left",
            address=addr,
            kind=otio.schema.TrackKind.Audio,
            metadata={"ITU-R_BS.2051": {"label": "L"}},
        )
        json_str = info.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.StreamInfo)
        self.assertEqual(restored.name, "audio_left")
        self.assertEqual(restored.kind, otio.schema.TrackKind.Audio)
        self.assertIsInstance(restored.address, otio.schema.IndexStreamAddress)
        self.assertEqual(restored.address.index, 2)
        self.assertEqual(restored.metadata["ITU-R_BS.2051"]["label"], "L")

    def test_round_trip_with_string_address(self):
        addr = otio.schema.StringStreamAddress(address="/World/potatoSet/cam1")
        info = otio.schema.StreamInfo(
            name="cam1", address=addr, kind=otio.schema.TrackKind.Video
        )
        json_str = info.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.StreamInfo)
        self.assertIsInstance(restored.address, otio.schema.StringStreamAddress)
        self.assertEqual(restored.address.address, "/World/potatoSet/cam1")


class TestStreamSelector(unittest.TestCase):
    def test_create_default(self):
        sel = otio.schema.StreamSelector()
        self.assertEqual(sel.name, "")
        self.assertEqual(sel.effect_name, "")
        self.assertEqual(sel.output_streams, [])

    def test_create_with_streams(self):
        sel = otio.schema.StreamSelector(
            name="stereo_select",
            effect_name="StreamSelector",
            output_streams=[
                StreamInfo.Identifier.stereo_left,
                StreamInfo.Identifier.stereo_right,
            ],
        )
        self.assertEqual(
            sel.output_streams,
            [
                StreamInfo.Identifier.stereo_left,
                StreamInfo.Identifier.stereo_right,
            ],
        )

    def test_set_output_streams(self):
        sel = otio.schema.StreamSelector()
        sel.output_streams = [
            StreamInfo.Identifier.surround_center_front,
            StreamInfo.Identifier.surround_low_frequency_effects,
        ]
        self.assertEqual(
            sel.output_streams,
            [
                StreamInfo.Identifier.surround_center_front,
                StreamInfo.Identifier.surround_low_frequency_effects,
            ],
        )

    def test_schema_name(self):
        sel = otio.schema.StreamSelector()
        self.assertEqual(sel.schema_name(), "StreamSelector")
        self.assertEqual(sel.schema_version(), 1)

    def test_round_trip_serialization(self):
        sel = otio.schema.StreamSelector(
            name="select_stereo",
            output_streams=[
                StreamInfo.Identifier.stereo_left,
                StreamInfo.Identifier.stereo_right,
            ],
        )
        json_str = sel.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.StreamSelector)
        self.assertEqual(restored.name, "select_stereo")
        self.assertEqual(
            restored.output_streams,
            [
                StreamInfo.Identifier.stereo_left,
                StreamInfo.Identifier.stereo_right,
            ],
        )

    def test_as_clip_effect(self):
        clip = otio.schema.Clip(name="my_clip")
        sel = otio.schema.StreamSelector(
            output_streams=[StreamInfo.Identifier.stereo_left]
        )
        clip.effects.append(sel)
        json_str = clip.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertEqual(len(restored.effects), 1)
        self.assertIsInstance(restored.effects[0], otio.schema.StreamSelector)
        self.assertEqual(
            restored.effects[0].output_streams, [StreamInfo.Identifier.stereo_left]
        )


class TestAudioMixMatrix(unittest.TestCase):
    def test_create_default(self):
        m = otio.schema.AudioMixMatrix()
        self.assertEqual(m.name, "")
        self.assertEqual(m.effect_name, "AudioMixMatrix")
        self.assertEqual(len(m.matrix), 0)

    def test_create_with_matrix(self):
        m = otio.schema.AudioMixMatrix(
            name="stereo_downmix",
            matrix={
                StreamInfo.Identifier.stereo_left: {
                    StreamInfo.Identifier.stereo_left: 1.0,
                    StreamInfo.Identifier.surround_center_front: 0.707,
                },
                StreamInfo.Identifier.stereo_right: {
                    StreamInfo.Identifier.stereo_right: 1.0,
                    StreamInfo.Identifier.surround_center_front: 0.707,
                },
            },
        )
        self.assertIn(StreamInfo.Identifier.stereo_left, m.matrix)
        self.assertIn(StreamInfo.Identifier.stereo_right, m.matrix)

    def test_schema_name(self):
        m = otio.schema.AudioMixMatrix()
        self.assertEqual(m.schema_name(), "AudioMixMatrix")
        self.assertEqual(m.schema_version(), 1)

    def test_round_trip_serialization(self):
        m = otio.schema.AudioMixMatrix(
            name="5_1_downmix",
            matrix={
                StreamInfo.Identifier.stereo_left: {
                    StreamInfo.Identifier.surround_left_front: 1.0,
                    StreamInfo.Identifier.surround_center_front: 0.707,
                    StreamInfo.Identifier.surround_left_rear: 0.707,
                },
                StreamInfo.Identifier.stereo_right: {
                    StreamInfo.Identifier.surround_right_front: 1.0,
                    StreamInfo.Identifier.surround_center_front: 0.707,
                    StreamInfo.Identifier.surround_right_rear: 0.707,
                },
            },
        )
        json_str = m.to_json_string()
        restored = otio.adapters.read_from_string(json_str, "otio_json")
        self.assertIsInstance(restored, otio.schema.AudioMixMatrix)
        self.assertEqual(restored.name, "5_1_downmix")
        self.assertIn(StreamInfo.Identifier.stereo_left, restored.matrix)
        self.assertIn(StreamInfo.Identifier.stereo_right, restored.matrix)


class TestStreamIdentifier(unittest.TestCase):
    def test_video_identifiers(self):
        self.assertEqual(StreamInfo.Identifier.left_eye, "left_eye")
        self.assertEqual(StreamInfo.Identifier.right_eye, "right_eye")
        self.assertEqual(StreamInfo.Identifier.monocular, "monocular")

    def test_audio_identifiers(self):
        self.assertEqual(StreamInfo.Identifier.monaural, "monaural")
        self.assertEqual(StreamInfo.Identifier.stereo_left, "stereo_left")
        self.assertEqual(StreamInfo.Identifier.stereo_right, "stereo_right")

    def test_surround_identifiers(self):
        self.assertEqual(
            StreamInfo.Identifier.surround_left_front, "surround_left_front"
        )
        self.assertEqual(
            StreamInfo.Identifier.surround_right_front, "surround_right_front"
        )
        self.assertEqual(
            StreamInfo.Identifier.surround_center_front, "surround_center_front"
        )
        self.assertEqual(StreamInfo.Identifier.surround_left_rear, "surround_left_rear")
        self.assertEqual(
            StreamInfo.Identifier.surround_right_rear, "surround_right_rear"
        )
        self.assertEqual(
            StreamInfo.Identifier.surround_low_frequency_effects,
            "surround_low_frequency_effects",
        )

    def test_module_alias(self):
        self.assertIs(otio.schema.StreamIdentifier, StreamInfo.Identifier)

    def test_use_in_available_streams(self):
        ref = otio.schema.ExternalReference(target_url="/foo/bar.mov")
        ref.set_available_streams(
            {
                StreamInfo.Identifier.left_eye: StreamInfo(
                    kind=otio.schema.TrackKind.Video,
                    address=otio.schema.IndexStreamAddress(0),
                ),
                StreamInfo.Identifier.stereo_left: StreamInfo(
                    kind=otio.schema.TrackKind.Audio,
                    address=otio.schema.IndexStreamAddress(1),
                ),
            }
        )
        streams = ref.available_streams()
        self.assertIn(StreamInfo.Identifier.left_eye, streams)
        self.assertIn(StreamInfo.Identifier.stereo_left, streams)


if __name__ == "__main__":
    unittest.main()
