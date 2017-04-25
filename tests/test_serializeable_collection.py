#!/usr/bin/env python

import unittest

import opentimelineio as otio


class SerializeableCollectionTests(unittest.TestCase):
    def setUp(self):
        self.children = [
            otio.core.Item(name="testItem"),
            otio.media_reference.MissingReference()
        ]
        self.md = {'foo': 'bar'}
        self.sc = otio.schema.SerializeableCollection(
            name="test",
            children=self.children,
            metadata=self.md
        )

    def test_ctor(self):
        self.assertEqual(self.sc.name, "test")
        self.assertEqual(self.sc[:], self.children)
        self.assertEqual(self.sc.metadata, self.md)

    def test_iterable(self):
        self.assertEqual(self.sc[0], self.children[0])
        self.assertEqual([i for i in self.sc], self.children)
        self.assertEqual(len(self.sc), 2)

    def test_serialize(self):
        encoded = otio.adapters.otio_json.write_to_string(self.sc)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(self.sc, decoded)

    def test_str(self):
        self.assertMultiLineEqual(
            str(self.sc),
            "SerializeableCollection(" +
            str(self.sc.name) + ", " +
            str(self.sc._children) + ", " +
            str(self.sc.metadata) +
            ")"
        )

    def test_repr(self):
        self.assertMultiLineEqual(
            repr(self.sc),
            "otio.schema.SerializeableCollection(" +
            "name=" + repr(self.sc.name) + ", " +
            "children=" + repr(self.sc._children) + ", " +
            "metadata=" + repr(self.sc.metadata) +
            ")"
        )
