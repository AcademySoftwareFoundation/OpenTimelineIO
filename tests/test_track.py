#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class TrackTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_children_if(self):
        cl = otio.schema.Clip()
        tr = otio.schema.Track()
        tr.append(cl)
        result = tr.children_if(otio.schema.Clip)
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
        result = tr.children_if(otio.schema.Clip, range)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl0)

    def test_children_if_shallow_search(self):
        cl0 = otio.schema.Clip()
        cl1 = otio.schema.Clip()
        st = otio.schema.Stack()
        st.append(cl1)
        tr = otio.schema.Track()
        tr.append(cl0)
        tr.append(st)
        result = tr.children_if(otio.schema.Clip, shallow_search=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], cl0)
        result = tr.children_if(otio.schema.Clip, shallow_search=False)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], cl0)
        self.assertEqual(result[1], cl1)


if __name__ == '__main__':
    unittest.main()
