"""Volume effects class test harness."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

class AudioVolumeTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        scale = otio.schema.AudioVolume(
            name="volume",
            gain=2.5,
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(scale.gain, 2.5)
        self.assertEqual(scale.name, "volume")
        self.assertEqual(scale.metadata, {"foo": "bar"})

    def test_eq(self):
        scale1 = otio.schema.AudioVolume(
            name="volume",
            gain=2.5,
            metadata={
                "foo": "bar"
            }
        )
        scale2 = otio.schema.AudioVolume(
            name="volume",
            gain=2.5,
            metadata={
                "foo": "bar"
            }
        )
        self.assertIsOTIOEquivalentTo(scale1, scale2)

    def test_serialize(self):
        scale = otio.schema.AudioVolume(
            name="volume",
            gain=0.6,
            metadata={
                "foo": "bar"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(scale)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(scale, decoded)

    def test_setters(self):
        scale = otio.schema.AudioVolume(
            name="volume",
            gain=0.8,
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(scale.gain, 0.8)
        scale.gain = 0.25
        self.assertEqual(scale.gain, 0.25)

class AudioFadeTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        fade = otio.schema.AudioFade(
            name="fade",
            fade_in=True,
            start_time=12.0,
            duration=8.0,
            metadata={"baz": "qux"}
        )
        self.assertEqual(fade.name, "fade")
        self.assertEqual(fade.fade_in, True)
        self.assertEqual(fade.start_time, 12.0)
        self.assertEqual(fade.duration, 8.0)
        self.assertEqual(fade.metadata, {"baz": "qux"})

    def test_eq(self):
        fade1 = otio.schema.AudioFade(
            name="fade",
            fade_in=False,
            start_time=5.0,
            duration=3.0,
            metadata={"baz": "qux"}
        )
        fade2 = otio.schema.AudioFade(
            name="fade",
            fade_in=False,
            start_time=5.0,
            duration=3.0,
            metadata={"baz": "qux"}
        )
        self.assertIsOTIOEquivalentTo(fade1, fade2)

    def test_serialize(self):
        fade = otio.schema.AudioFade(
            name="fade",
            fade_in=True,
            start_time=2.5,
            duration=1.5,
            metadata={"baz": "qux"}
        )
        encoded = otio.adapters.otio_json.write_to_string(fade)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(fade, decoded)

    def test_setters(self):
        fade = otio.schema.AudioFade(
            name="fade",
            fade_in=False,
            start_time=4.0,
            duration=2.0,
            metadata={"baz": "qux"}
        )
        self.assertEqual(fade.fade_in, False)
        self.assertEqual(fade.start_time, 4.0)
        self.assertEqual(fade.duration, 2.0)
        fade.fade_in = True
        fade.start_time = 7.5
        fade.duration = 3.5
        self.assertEqual(fade.fade_in, True)
        self.assertEqual(fade.start_time, 7.5)
        self.assertEqual(fade.duration, 3.5)
