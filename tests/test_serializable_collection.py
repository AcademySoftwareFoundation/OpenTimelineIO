# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class SerializableColTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    def setUp(self):
        self.maxDiff = None
        self.children = [
            otio.schema.Clip(name="testClip"),
            otio.schema.MissingReference()
        ]
        self.md = {'foo': 'bar'}
        self.sc = otio.schema.SerializableCollection(
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

        # test recursive iteration
        sc = otio.schema.SerializableCollection(
            name="parent",
            children=[self.sc]
        )

        self.assertEqual(len(list(sc.each_clip())), 1)

        # test deleting an item
        tmp = self.sc[0]
        del self.sc[0]
        self.assertEqual(len(self.sc), 1)
        self.sc[0] = tmp
        self.assertEqual(self.sc[0], tmp)

    def test_serialize(self):
        encoded = otio.adapters.otio_json.write_to_string(self.sc)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(self.sc, decoded)

    def test_str(self):
        self.assertMultiLineEqual(
            str(self.sc),
            "SerializableCollection(" +
            str(self.sc.name) + ", " +
            str(list(self.sc)) + ", " +
            str(self.sc.metadata) +
            ")"
        )

    def test_repr(self):
        self.assertMultiLineEqual(
            repr(self.sc),
            "otio.schema.SerializableCollection(" +
            "name=" + repr(self.sc.name) + ", " +
            "children=" + repr(list(self.sc)) + ", " +
            "metadata=" + repr(self.sc.metadata) +
            ")"
        )

    def test_children_if(self):
        cl = otio.schema.Clip()
        tr = otio.schema.Track()
        tr.append(cl)
        tl = otio.schema.Timeline()
        tl.tracks.append(tr)
        sc = otio.schema.SerializableCollection()
        sc.append(tl)
        result = sc.children_if(otio.schema.Clip)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl)

    def test_children_if_search_range(self):
        range = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0.0, 24.0),
            otio.opentime.RationalTime(24.0, 24.0))
        cl0 = otio.schema.Clip()
        cl0.source_range = range
        cl1 = otio.schema.Clip()
        cl1.source_range = range
        cl2 = otio.schema.Clip()
        cl2.source_range = range
        tr = otio.schema.Track()
        tr.append(cl0)
        tr.append(cl1)
        tr.append(cl2)
        tl = otio.schema.Timeline()
        tl.tracks.append(tr)
        sc = otio.schema.SerializableCollection()
        sc.append(tl)
        result = sc.children_if(otio.schema.Clip, range)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl0)

    def test_children_if_shallow_search(self):
        cl = otio.schema.Clip()
        tr = otio.schema.Track()
        tr.append(cl)
        tl = otio.schema.Timeline()
        tl.tracks.append(tr)
        sc = otio.schema.SerializableCollection()
        sc.append(tl)
        result = sc.children_if(otio.schema.Clip, shallow_search=True)
        self.assertEqual(len(result), 0)
        result = sc.children_if(otio.schema.Clip, shallow_search=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl)


if __name__ == '__main__':
    unittest.main()
