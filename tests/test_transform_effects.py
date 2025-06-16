"""Transform effects class test harness."""

import unittest
from fractions import Fraction

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

class VideoScaleTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        scale = otio.schema.VideoScale(
            name="ScaleIt",
            width=100,
            height=120,
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(scale.width, 100)
        self.assertEqual(scale.height, 120)
        self.assertEqual(scale.name, "ScaleIt")
        self.assertEqual(scale.metadata, {"foo": "bar"})

    def test_eq(self):
        scale1 = otio.schema.VideoScale(
            name="ScaleIt",
            width=120,
            height=130,
            metadata={
                "foo": "bar"
            }
        )
        scale2 = otio.schema.VideoScale(
            name="ScaleIt",
            width=120,
            height=130,
            metadata={
                "foo": "bar"
            }
        )
        self.assertIsOTIOEquivalentTo(scale1, scale2)

    def test_serialize(self):
        scale = otio.schema.VideoScale(
            name="ScaleIt",
            width=130,
            height=140,
            metadata={
                "foo": "bar"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(scale)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(scale, decoded)

    def test_setters(self):
        scale = otio.schema.VideoScale(
            name="ScaleIt",
            width=140,
            height=150,
            metadata={
                "foo": "bar"
            }
        )
        self.assertEqual(scale.width, 140)
        scale.width = 100
        self.assertEqual(scale.width,100)
        self.assertEqual(scale.height, 150)
        scale.height = 100
        self.assertEqual(scale.height,100)

class VideoCropTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_cons(self):
        crop = otio.schema.VideoCrop(
            name="CropIt",
            left=2,
            right=3,
            top=4,
            bottom=5,
            metadata={
                "baz": "qux"
            }
        )
        self.assertEqual(crop.left, 2)
        self.assertEqual(crop.right, 3)
        self.assertEqual(crop.top, 4)
        self.assertEqual(crop.bottom, 5)
        self.assertEqual(crop.name, "CropIt")
        self.assertEqual(crop.metadata, {"baz": "qux"})

    def test_eq(self):
        crop1 = otio.schema.VideoCrop(
            name="CropIt",
            left=2,
            right=3,
            top=4,
            bottom=5,
            metadata={
                "baz": "qux"
            }
        )
        crop2 = otio.schema.VideoCrop(
            name="CropIt",
            left=2,
            right=3,
            top=4,
            bottom=5,
            metadata={
                "baz": "qux"
            }
        )
        self.assertIsOTIOEquivalentTo(crop1, crop2)

    def test_serialize(self):
        crop = otio.schema.VideoCrop(
            name="CropIt",
            left=2,
            right=3,
            top=4,
            bottom=5,
            metadata={
                "baz": "qux"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(crop)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(crop, decoded)

    def test_setters(self):
        crop = otio.schema.VideoCrop(
            name="CropIt",
            left=2,
            right=3,
            top=4,
            bottom=5,
            metadata={
                "baz": "qux"
            }
        )
        self.assertEqual(crop.left, 2)
        crop.left = 1
        self.assertEqual(crop.left, 1)
        crop.right = 3
        self.assertEqual(crop.right, 3)
        crop.top = 4
        self.assertEqual(crop.top, 4)
        crop.bottom = 7
        self.assertEqual(crop.bottom, 7)

class VideoPositionTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        position = otio.schema.VideoPosition(
            name="PositionIt",
            x=11,
            y=12,
            metadata={
                "alpha": "beta"
            }
        )
        self.assertEqual(position.x, 11)
        self.assertEqual(position.y, 12)
        self.assertEqual(position.name, "PositionIt")
        self.assertEqual(position.metadata, {"alpha": "beta"})

    def test_eq(self):
        pos1 = otio.schema.VideoPosition(
            name="PositionIt",
            x=11,
            y=12,
            metadata={
                "alpha": "beta"
            }
        )
        pos2 = otio.schema.VideoPosition(
            name="PositionIt",
            x=11,
            y=12,
            metadata={
                "alpha": "beta"
            }
        )
        self.assertIsOTIOEquivalentTo(pos1, pos2)

    def test_serialize(self):
        position = otio.schema.VideoPosition(
            name="PositionIt",
            x=11,
            y=12,
            metadata={
                "alpha": "beta"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(position)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(position, decoded)

    def test_setters(self):
        position = otio.schema.VideoPosition(
            name="PositionIt",
            x=11,
            y=12,
            metadata={
                "alpha": "beta"
            }
        )
        self.assertEqual(position.x, 11)
        position.x = 1
        self.assertEqual(position.x, 1)
        self.assertEqual(position.y, 12)
        position.y = 2
        self.assertEqual(position.y, 2)

class VideoRotateTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def test_constructor(self):
        rotate = otio.schema.VideoRotate(
            name="RotateIt",
            angle=45.25,
            metadata={
                "rot": "val"
            }
        )
        self.assertEqual(rotate.angle,45.25)
        self.assertEqual(rotate.name, "RotateIt")
        self.assertEqual(rotate.metadata, {"rot": "val"})

    def test_eq(self):
        rot1 = otio.schema.VideoRotate(
            name="RotateIt",
            angle=45.25,
            metadata={
                "rot": "val"
            }
        )
        rot2 = otio.schema.VideoRotate(
            name="RotateIt",
            angle=45.25,
            metadata={
                "rot": "val"
            }
        )
        self.assertIsOTIOEquivalentTo(rot1, rot2)

    def test_serialize(self):
        rotate = otio.schema.VideoRotate(
            name="RotateIt",
            angle=45.25,
            metadata={
                "rot": "val"
            }
        )
        encoded = otio.adapters.otio_json.write_to_string(rotate)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(rotate, decoded)

    def test_setters(self):
        rotate = otio.schema.VideoRotate(
            name="RotateIt",
            angle=45.25,
            metadata={
                "rot": "val"
            }
        )
        self.assertEqual(rotate.angle, 45.25)
        rotate.angle = 90.0
        self.assertEqual(rotate.angle, 90.0)
