#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test file for the edit algorithms bindings.

The algorithms are tested in C++ (test_editAlgorithm.cpp), these tests check
that each one can be called from Python.
"""

import unittest

import opentimelineio as otio


def _clip(name, duration, start=0):
    return otio.schema.Clip(
        name=name,
        source_range=otio.opentime.TimeRange(
            otio.opentime.RationalTime(start, 24),
            otio.opentime.RationalTime(duration, 24)
        )
    )


def _track(*durations):
    return otio.schema.Track(
        children=[_clip("ABC"[i], d) for i, d in enumerate(durations)]
    )


def _rt(value):
    return otio.opentime.RationalTime(value, 24)


def _ranges(track):
    return [
        (c.name or c.schema_name(),
         c.source_range.start_time.value,
         c.source_range.duration.value)
        for c in track
    ]


class EditAlgoTests(unittest.TestCase):

    def test_overwrite(self):
        track = _track(10, 10)
        otio.algorithms.edit.overwrite(
            _clip("C", 4),
            track,
            otio.opentime.TimeRange(_rt(3), _rt(4))
        )
        self.assertEqual(
            _ranges(track),
            [("A", 0, 3), ("C", 0, 4), ("A", 7, 3), ("B", 0, 10)]
        )

    def test_insert(self):
        track = _track(10, 10)
        otio.algorithms.edit.insert(_clip("C", 4), track, _rt(5))
        self.assertEqual(
            [(c.name, c.source_range.duration.value) for c in track],
            [("A", 5), ("C", 4), ("A", 5), ("B", 10)]
        )

    def test_trim(self):
        track = _track(10, 10)
        otio.algorithms.edit.trim(track[0], _rt(0), _rt(-3))
        self.assertEqual(
            _ranges(track),
            [("A", 0, 7), ("Gap", 0, 3), ("B", 0, 10)]
        )

    def test_slice(self):
        track = _track(10, 10)
        otio.algorithms.edit.slice(track, _rt(5))
        self.assertEqual(
            _ranges(track),
            [("A", 0, 5), ("A", 5, 5), ("B", 0, 10)]
        )

    def test_slip(self):
        track = _track(10, 10)
        otio.algorithms.edit.slip(track[0], _rt(3))
        self.assertEqual(_ranges(track), [("A", 3, 10), ("B", 0, 10)])

    def test_slide(self):
        track = _track(10, 10, 10)
        otio.algorithms.edit.slide(track[1], _rt(2))
        self.assertEqual(
            _ranges(track),
            [("A", 0, 12), ("B", 0, 10), ("C", 0, 10)]
        )

    def test_ripple(self):
        track = _track(10, 10)
        otio.algorithms.edit.ripple(track[0], _rt(0), _rt(-3))
        self.assertEqual(_ranges(track), [("A", 0, 7), ("B", 0, 10)])

    def test_roll(self):
        track = otio.schema.Track(children=[_clip("A", 10), _clip("B", 10, 5)])
        otio.algorithms.edit.roll(track[1], _rt(-3), _rt(0))
        self.assertEqual(_ranges(track), [("A", 0, 7), ("B", 2, 13)])

    def test_fill(self):
        track = _track(10, 10, 10)
        track[1] = otio.schema.Gap(duration=_rt(10))
        otio.algorithms.edit.fill(_clip("C", 4), track, _rt(12))
        self.assertEqual(
            _ranges(track),
            [("A", 0, 10), ("Gap", 0, 2), ("C", 0, 4), ("Gap", 6, 4),
             ("C", 0, 10)]
        )

        track = _track(10, 10, 10)
        track[1] = otio.schema.Gap(duration=_rt(10))
        otio.algorithms.edit.fill(
            _clip("C", 20),
            track,
            _rt(10),
            otio.algorithms.edit.ReferencePoint.Sequence
        )
        self.assertEqual(
            _ranges(track),
            [("A", 0, 10), ("C", 0, 10), ("C", 0, 10)]
        )

        with self.assertRaises(ValueError):
            otio.algorithms.edit.fill(_clip("C", 4), _track(10, 10), _rt(5))

    def test_remove(self):
        track = _track(10, 10, 10)
        otio.algorithms.edit.remove(track, _rt(15))
        self.assertEqual(
            _ranges(track),
            [("A", 0, 10), ("Gap", 0, 10), ("C", 0, 10)]
        )

        track = _track(10, 10, 10)
        otio.algorithms.edit.remove(track, _rt(15), fill=False)
        self.assertEqual(_ranges(track), [("A", 0, 10), ("C", 0, 10)])

    def test_error(self):
        with self.assertRaises(otio.exceptions.NotAChildError):
            otio.algorithms.edit.roll(_clip("C", 4), _rt(1), _rt(0))


if __name__ == '__main__':
    unittest.main()
