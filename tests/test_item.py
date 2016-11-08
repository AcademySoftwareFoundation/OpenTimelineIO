#!/usr/bin/env python

""" Test harness for Item. """

import unittest

import opentimelineio as otio


class FillerTester(unittest.TestCase):

    def test_str_filler(self):
        fl = otio.schema.Filler()
        self.assertMultiLineEqual(
            str(fl),
            "Filler(" +
            str(fl.name) + ", " +
            str(fl.source_range) + ", " +
            str(fl.effects) + ", " +
            str(fl.markers) + ", " +
            str(fl.metadata) +
            ")"
        )
        self.assertMultiLineEqual(
            repr(fl),
            "otio.schema.Filler("
            "name={}, "
            "source_range={}, "
            "effects={}, "
            "markers={}, "
            "metadata={}"
            ")".format(
                repr(fl.name),
                repr(fl.source_range),
                repr(fl.effects),
                repr(fl.markers),
                repr(fl.metadata),
            )
        )

        encoded = otio.adapters.otio_json.write_to_string(fl)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(fl, decoded)


class ItemTests(unittest.TestCase):

    def test_constructor(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(name="foo", source_range=tr)
        self.assertEqual(it.source_range, tr)
        self.assertEqual(it.name, "foo")

        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(it, decoded)

    def test_is_parent_of(self):
        it = otio.core.Item()
        it_2 = otio.core.Item()

        self.assertFalse(it.is_parent_of(it_2))
        it_2._set_parent(it)
        self.assertTrue(it.is_parent_of(it_2))

    def test_set_parent(self):
        it = otio.core.Item()
        it_2 = otio.core.Item()

        # set it from none
        it_2._set_parent(it)
        self.assertEqual(it, it_2._parent)

        # change it
        it_3 = otio.core.Item()
        it_2._set_parent(it_3)
        self.assertEqual(it_3, it_2._parent)

    def test_duration(self):
        it = otio.core.Item()
        with self.assertRaises(NotImplementedError):
            it.computed_duration()

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)

        self.assertEqual(it.duration(), tr.duration)

    def test_duration_and_source_range(self):
        it = otio.core.Item()
        with self.assertRaises(NotImplementedError):
            it.computed_duration()
        with self.assertRaises(NotImplementedError):
            it.duration()
        self.assertEqual(None, it.source_range)

        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(1, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it2 = otio.core.Item(source_range=tr)
        with self.assertRaises(NotImplementedError):
            it2.computed_duration()
        self.assertEqual(tr, it2.source_range)
        self.assertEqual(tr.duration, it2.duration())

    def test_trimmed_range(self):
        it = otio.core.Item()
        with self.assertRaises(NotImplementedError):
            it.trimmed_range()
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(1, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it2 = otio.core.Item(source_range=tr)
        self.assertEqual(it2.trimmed_range(), tr)

    def test_serialize(self):
        tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 1),
            otio.opentime.RationalTime(10, 1)
        )
        it = otio.core.Item(source_range=tr)
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(it, decoded)

    def test_stringify(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr)
        self.assertMultiLineEqual(
            str(it),
            "Item("
            "{}, "
            "{}, "
            "{}, "
            "{}, "
            "{}"
            ")".format(
                str(it.name),
                str(it.source_range),
                str(it.effects),
                str(it.markers),
                str(it.metadata),
            )
        )

        self.assertMultiLineEqual(
            repr(it),
            "otio.core.Item("
            "name={}, "
            "source_range={}, "
            "effects={}, "
            "markers={}, "
            "metadata={}"
            ")".format(
                repr(it.name),
                repr(it.source_range),
                repr(it.effects),
                repr(it.markers),
                repr(it.metadata),
            )
        )

    def test_metadata(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr)
        it.metadata["foo"] = "bar"
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(it, decoded)
        self.assertEqual(decoded.metadata["foo"], it.metadata["foo"])

    def test_add_effect(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr)
        it.effects.append(
            otio.schema.Effect(
                effect_name="blur",
                metadata={
                    'amount': '100'
                }
            )
        )
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(it, decoded)
        self.assertEqual(it.effects, decoded.effects)

    def test_add_marker(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr)
        it.markers.append(
            otio.schema.Marker(
                name="test_marker",
                range=tr,
                metadata={
                    'some stuff to mark': '100'
                }
            )
        )
        encoded = otio.adapters.otio_json.write_to_string(it)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(it, decoded)
        self.assertEqual(it.markers, decoded.markers)

    def test_copy(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr, metadata={"foo": "bar"})
        it.markers.append(
            otio.schema.Marker(
                name="test_marker",
                range=tr,
                metadata={
                    'some stuff to mark': '100'
                }
            )
        )
        it.effects.append(
            otio.schema.Effect(
                effect_name="blur",
                metadata={
                    'amount': '100'
                }
            )
        )

        it_copy = it.copy()
        self.assertEqual(it, it_copy)
        it.metadata["foo"] = "bar2"
        # shallow copy, should change both dictionaries
        self.assertEqual(it_copy.metadata["foo"], "bar2")

        # name should be different
        it.name = "foo"
        self.assertNotEqual(it_copy.name, it.name)

        # deep copy should have different dictionaries
        it_dcopy = it.deepcopy()
        it_dcopy.metadata["foo"] = "not bar"
        self.assertNotEqual(it.metadata, it_dcopy.metadata)

    def test_copy_library(self):
        tr = otio.opentime.TimeRange(
            duration=otio.opentime.RationalTime(10, 1))
        it = otio.core.Item(source_range=tr, metadata={"foo": "bar"})
        it.markers.append(
            otio.schema.Marker(
                name="test_marker",
                range=tr,
                metadata={
                    'some stuff to mark': '100'
                }
            )
        )
        it.effects.append(
            otio.schema.Effect(
                effect_name="blur",
                metadata={
                    'amount': '100'
                }
            )
        )

        # shallow test
        import copy
        it_copy = copy.copy(it)
        self.assertEqual(it, it_copy)
        it.metadata["foo"] = "bar2"
        # shallow copy, should change both dictionaries
        self.assertEqual(it_copy.metadata["foo"], "bar2")

        # name should be different
        it.name = "foo"
        self.assertNotEqual(it_copy.name, it.name)

        # deep copy should have different dictionaries
        it_dcopy = copy.deepcopy(it)
        it_dcopy.metadata["foo"] = "not bar"
        self.assertNotEqual(it.metadata, it_dcopy.metadata)


if __name__ == '__main__':
    unittest.main()
