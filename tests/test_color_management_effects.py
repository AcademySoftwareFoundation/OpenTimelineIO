"""Color management effects class test harness."""

import unittest
import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

class VideoBrightnessTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        brightness = otio.schema.VideoBrightness(
            name="BrightIt",
            brightness=50,
            metadata={"foo": "bar"}
        )
        self.assertEqual(brightness.brightness, 50)
        self.assertEqual(brightness.name, "BrightIt")
        self.assertEqual(brightness.metadata, {"foo": "bar"})

    def test_eq(self):
        b1 = otio.schema.VideoBrightness(name="BrightIt", brightness=50, metadata={"foo": "bar"})
        b2 = otio.schema.VideoBrightness(name="BrightIt", brightness=50, metadata={"foo": "bar"})
        self.assertIsOTIOEquivalentTo(b1, b2)

    def test_serialize(self):
        brightness = otio.schema.VideoBrightness(name="BrightIt", brightness=50, metadata={"foo": "bar"})
        encoded = otio.adapters.otio_json.write_to_string(brightness)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(brightness, decoded)

    def test_setters(self):
        brightness = otio.schema.VideoBrightness(name="BrightIt", brightness=50, metadata={"foo": "bar"})
        self.assertEqual(brightness.brightness, 50)
        brightness.brightness = 100
        self.assertEqual(brightness.brightness, 100)

class VideoContrastTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        contrast = otio.schema.VideoContrast(
            name="ContrastIt",
            contrast=20,
            metadata={"foo": "bar"}
        )
        self.assertEqual(contrast.contrast, 20)
        self.assertEqual(contrast.name, "ContrastIt")
        self.assertEqual(contrast.metadata, {"foo": "bar"})

    def test_eq(self):
        c1 = otio.schema.VideoContrast(name="ContrastIt", contrast=20, metadata={"foo": "bar"})
        c2 = otio.schema.VideoContrast(name="ContrastIt", contrast=20, metadata={"foo": "bar"})
        self.assertIsOTIOEquivalentTo(c1, c2)

    def test_serialize(self):
        contrast = otio.schema.VideoContrast(name="ContrastIt", contrast=20, metadata={"foo": "bar"})
        encoded = otio.adapters.otio_json.write_to_string(contrast)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(contrast, decoded)

    def test_setters(self):
        contrast = otio.schema.VideoContrast(name="ContrastIt", contrast=20, metadata={"foo": "bar"})
        self.assertEqual(contrast.contrast, 20)
        contrast.contrast = 40
        self.assertEqual(contrast.contrast, 40)

class VideoSaturationTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        saturation = otio.schema.VideoSaturation(
            name="SaturateIt",
            saturation=70,
            metadata={"foo": "bar"}
        )
        self.assertEqual(saturation.saturation, 70)
        self.assertEqual(saturation.name, "SaturateIt")
        self.assertEqual(saturation.metadata, {"foo": "bar"})

    def test_eq(self):
        s1 = otio.schema.VideoSaturation(name="SaturateIt", saturation=70, metadata={"foo": "bar"})
        s2 = otio.schema.VideoSaturation(name="SaturateIt", saturation=70, metadata={"foo": "bar"})
        self.assertIsOTIOEquivalentTo(s1, s2)

    def test_serialize(self):
        saturation = otio.schema.VideoSaturation(name="SaturateIt", saturation=70, metadata={"foo": "bar"})
        encoded = otio.adapters.otio_json.write_to_string(saturation)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(saturation, decoded)

    def test_setters(self):
        saturation = otio.schema.VideoSaturation(name="SaturateIt", saturation=70, metadata={"foo": "bar"})
        self.assertEqual(saturation.saturation, 70)
        saturation.saturation = 100
        self.assertEqual(saturation.saturation, 100)

class VideoLightnessTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        lightness = otio.schema.VideoLightness(
            name="LightIt",
            lightness=10,
            metadata={"foo": "bar"}
        )
        self.assertEqual(lightness.lightness, 10)
        self.assertEqual(lightness.name, "LightIt")
        self.assertEqual(lightness.metadata, {"foo": "bar"})

    def test_eq(self):
        l1 = otio.schema.VideoLightness(name="LightIt", lightness=10, metadata={"foo": "bar"})
        l2 = otio.schema.VideoLightness(name="LightIt", lightness=10, metadata={"foo": "bar"})
        self.assertIsOTIOEquivalentTo(l1, l2)

    def test_serialize(self):
        lightness = otio.schema.VideoLightness(name="LightIt", lightness=10, metadata={"foo": "bar"})
        encoded = otio.adapters.otio_json.write_to_string(lightness)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(lightness, decoded)

    def test_setters(self):
        lightness = otio.schema.VideoLightness(name="LightIt", lightness=10, metadata={"foo": "bar"})
        self.assertEqual(lightness.lightness, 10)
        lightness.lightness = 20
        self.assertEqual(lightness.lightness, 20)

class VideoColorTemperatureTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        temp = otio.schema.VideoColorTemperature(
            name="TempIt",
            temperature=6500,
            metadata={"foo": "bar"}
        )
        self.assertEqual(temp.temperature, 6500)
        self.assertEqual(temp.name, "TempIt")
        self.assertEqual(temp.metadata, {"foo": "bar"})

    def test_eq(self):
        t1 = otio.schema.VideoColorTemperature(name="TempIt", temperature=6500, metadata={"foo": "bar"})
        t2 = otio.schema.VideoColorTemperature(name="TempIt", temperature=6500, metadata={"foo": "bar"})
        self.assertIsOTIOEquivalentTo(t1, t2)

    def test_serialize(self):
        temp = otio.schema.VideoColorTemperature(name="TempIt", temperature=6500, metadata={"foo": "bar"})
        encoded = otio.adapters.otio_json.write_to_string(temp)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(temp, decoded)

    def test_setters(self):
        temp = otio.schema.VideoColorTemperature(name="TempIt", temperature=6500, metadata={"foo": "bar"})
        self.assertEqual(temp.temperature, 6500)
        temp.temperature = 7000
        self.assertEqual(temp.temperature, 7000)
