#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import unittest
import os
import copy

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
TRANSITION_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "transition_test.otio")


class CompositionTests(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        it = otio.core.Item()
        co = otio.core.Composition(name="test", children=[it])
        self.assertEqual(co.name, "test")
        self.assertEqual(list(co), [it])
        self.assertEqual(co.composition_kind, "Composition")

    def test_iterable(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertIs(co[0], it)
        self.assertEqual([i for i in co], [it])
        self.assertEqual(len(co), 1)

        self.assertEqual(list(co.children_if()), [it])
        self.assertEqual(
            list(co.children_if(descended_from_type=otio.schema.Clip)),
            []
        )

    def test_equality(self):
        co0 = otio.core.Composition()
        co00 = otio.core.Composition()
        self.assertIsOTIOEquivalentTo(co0, co00)

        a = otio.core.Item(name="A")
        b = otio.core.Item(name="B")
        c = otio.core.Item(name="C")
        co1 = otio.core.Composition(children=[a, b, c])

        x = otio.core.Item(name="X")
        y = otio.core.Item(name="Y")
        z = otio.core.Item(name="Z")
        co2 = otio.core.Composition(children=[x, y, z])

        a2 = otio.core.Item(name="A")
        b2 = otio.core.Item(name="B")
        c2 = otio.core.Item(name="C")
        co3 = otio.core.Composition(children=[a2, b2, c2])

        self.assertTrue(co1 is not co2)
        self.assertNotEqual(co1, co2)

        self.assertTrue(co1 is not co3)
        self.assertIsOTIOEquivalentTo(co1, co3)

    def test_truthiness(self):
        # An empty Composition is False (since it behaves like a list)
        o = otio.core.Composition()
        self.assertFalse(o)

        # A Composition with anything in it is True
        o.append(otio.core.Composition())
        self.assertTrue(o)

    def test_replacing_children(self):
        a = otio.core.Item(name="A")
        b = otio.core.Item(name="B")
        c = otio.core.Item(name="C")
        co = otio.core.Composition(children=[a, b])
        self.assertEqual(2, len(co))
        self.assertIs(co[0], a)
        self.assertIs(co[1], b)
        del co[1]
        self.assertEqual(1, len(co))
        self.assertIs(co[0], a)
        co[0] = c
        self.assertEqual(1, len(co))
        self.assertIs(co[0], c)
        co[:] = [a, b]
        self.assertEqual(2, len(co))
        self.assertIs(co[0], a)
        self.assertIs(co[1], b)
        co[0:2] = [c]
        self.assertEqual(1, len(co))
        self.assertIs(co[0], c)
        co[:] = [c, b, a]
        self.assertEqual(3, len(co))
        self.assertIs(co[0], c)
        self.assertIs(co[1], b)
        self.assertIs(co[2], a)

    def test_is_parent_of(self):
        co = otio.core.Composition()
        co_2 = otio.core.Composition()

        self.assertFalse(co.is_parent_of(co_2))
        co.append(co_2)
        self.assertTrue(co.is_parent_of(co_2))

    def test_parent_manip(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertIs(it.parent(), co)

    def test_move_child(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertIs(it.parent(), co)

        co2 = otio.core.Composition()
        with self.assertRaises(ValueError):
            co2.append(it)

        del co[0]
        co2.append(it)
        self.assertIs(it.parent(), co2)

    def test_children_if_recursion(self):
        tl = otio.schema.Timeline(name="TL")

        tr1 = otio.schema.Track(name="tr1")
        tl.tracks.append(tr1)
        c1 = otio.schema.Clip(name="c1")
        tr1.append(c1)
        c2 = otio.schema.Clip(name="c2")
        tr1.append(c2)
        c3 = otio.schema.Clip(name="c3")
        tr1.append(c3)

        tr2 = otio.schema.Track(name="tr2")
        tl.tracks.append(tr2)
        c4 = otio.schema.Clip(name="c4")
        tr2.append(c4)
        c5 = otio.schema.Clip(name="c5")
        tr2.append(c5)

        st = otio.schema.Stack(name="st")
        tr2.append(st)
        c6 = otio.schema.Clip(name="c6")
        st.append(c6)
        tr3 = otio.schema.Track(name="tr3")
        c7 = otio.schema.Clip(name="c7")
        tr3.append(c7)
        c8 = otio.schema.Clip(name="c8")
        tr3.append(c8)
        st.append(tr3)

        self.assertEqual(2, len(tl.tracks))
        self.assertEqual(3, len(tr1))
        self.assertEqual(3, len(tr2))
        self.assertEqual(2, len(st))
        self.assertEqual(2, len(tr3))

        clips = list(tl.clip_if())
        self.assertListEqual(
            [c1, c2, c3, c4, c5, c6, c7, c8],
            clips
        )

        all_tracks = list(tl.children_if(
            descended_from_type=otio.schema.Track
        ))
        self.assertListEqual(
            [tr1, tr2, tr3],
            all_tracks
        )

        all_stacks = list(tl.children_if(
            descended_from_type=otio.schema.Stack
        ))
        self.assertListEqual(
            [st],
            all_stacks
        )

        all_children = list(tl.children_if())
        self.assertListEqual(
            [tr1, c1, c2, c3, tr2, c4, c5, st, c6, tr3, c7, c8],
            all_children
        )

    def test_children_if_options(self):
        tl = otio.schema.Timeline(name="tl")
        tr = otio.schema.Track(name="tr")
        tl.tracks.append(tr)
        c1 = otio.schema.Clip(
            name="c1",
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=0, rate=24),
                duration=otio.opentime.RationalTime(value=50, rate=24)
            )
        )
        tr.append(c1)
        c2 = otio.schema.Clip(
            name="c2",
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=0, rate=24),
                duration=otio.opentime.RationalTime(value=50, rate=24)
            )
        )
        tr.append(c2)
        st = otio.schema.Stack(
            name="st",
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=0, rate=24),
                duration=otio.opentime.RationalTime(value=50, rate=24)
            )
        )
        tr.append(st)
        c3 = otio.schema.Clip(
            name="c3",
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=0, rate=24),
                duration=otio.opentime.RationalTime(value=50, rate=24)
            )
        )
        st.append(c3)

        # Test the search range
        self.assertListEqual(
            [c1],
            list(
                tr.children_if(
                    search_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(value=0, rate=24),
                        duration=otio.opentime.RationalTime(value=50, rate=24)
                    )
                )
            )
        )
        self.assertListEqual(
            [c2],
            list(
                tr.children_if(
                    search_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(value=50, rate=24),
                        duration=otio.opentime.RationalTime(value=50, rate=24)
                    )
                )
            )
        )
        self.assertListEqual(
            [c1, c2],
            list(
                tr.children_if(
                    search_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(value=0, rate=24),
                        duration=otio.opentime.RationalTime(value=100, rate=24)
                    )
                )
            )
        )
        self.assertListEqual(
            [c1, c2, st, c3],
            list(
                tr.children_if(
                    search_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(value=25, rate=24),
                        duration=otio.opentime.RationalTime(value=100, rate=24)
                    )
                )
            )
        )

        # Test descended from type
        self.assertListEqual(
            [c1, c2, c3],
            list(tl.children_if(descended_from_type=otio.schema.Clip))
        )
        self.assertListEqual(
            [st],
            list(tl.children_if(descended_from_type=otio.schema.Stack))
        )

        # Test shallow search
        self.assertListEqual(
            [c1, c2],
            list(
                tr.children_if(
                    descended_from_type=otio.schema.Clip,
                    shallow_search=True
                )
            )
        )

    def test_remove_actually_removes(self):
        """Test that removed item is no longer 'in' composition."""
        tr = otio.schema.Track()
        cl = otio.schema.Clip()

        # test inclusion
        tr.append(cl)
        self.assertIn(cl, tr)

        # delete by index
        del tr[0]
        self.assertNotIn(cl, tr)

        # delete by slice
        tr = otio.schema.Track()
        tr.append(cl)
        del tr[:]
        self.assertNotIn(cl, tr)

        # delete by setting over item
        tr = otio.schema.Track()
        tr.append(cl)
        cl2 = otio.schema.Clip()
        tr[0] = cl2
        self.assertNotIn(cl, tr)

        # delete by pop
        tr = otio.schema.Track()
        tr.insert(0, cl)
        tr.pop()
        self.assertNotIn(cl, tr)

    def test_insert_slice(self):
        """Test that inserting by slice actually correctly inserts"""

        st = otio.schema.Stack()
        cl = otio.schema.Clip()

        st[:] = [cl]

        self.assertEqual(cl, st[0])

        del st[0]

        self.assertEqual(len(st), 0)

        # again, this time deleting with a slice as well.
        st[:] = [cl]

        self.assertEqual(cl, st[0])

        del st[:]

        self.assertEqual(len(st), 0)

        st = otio.schema.Stack()
        cl = otio.schema.Clip()
        cl2 = otio.schema.Clip()

        st[:] = [cl]
        st[:] = [cl2]

        self.assertNotIn(cl, st)
        self.assertIn(cl2, st)

    def test_has_clip(self):
        st = otio.schema.Stack(name="ST")

        tr1 = otio.schema.Track(name="tr1")
        st.append(tr1)

        self.assertFalse(st.has_clips())
        self.assertFalse(tr1.has_clips())

        c1 = otio.schema.Clip(name="c1")
        tr1.append(c1)

        self.assertTrue(st.has_clips())
        self.assertTrue(tr1.has_clips())

        tr2 = otio.schema.Track(name="tr2")
        st.append(tr2)

        self.assertTrue(st.has_clips())
        self.assertTrue(tr1.has_clips())
        self.assertFalse(tr2.has_clips())

        g1 = otio.schema.Gap(name="g1")
        tr2.append(g1)

        self.assertTrue(st.has_clips())
        self.assertTrue(tr1.has_clips())
        self.assertFalse(tr2.has_clips())

        c2 = otio.schema.Clip(name="c2")
        tr2.append(c2)

        self.assertTrue(st.has_clips())
        self.assertTrue(tr1.has_clips())
        self.assertTrue(tr2.has_clips())


class StackTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_cons(self):
        st = otio.schema.Stack(name="test")
        self.assertEqual(st.name, "test")

    def test_serialize(self):
        st = otio.schema.Stack(
            name="test",
            children=[otio.schema.Clip(name="testClip")]
        )

        encoded = otio.adapters.otio_json.write_to_string(st)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(st, decoded)

        self.assertIsNotNone(decoded[0].parent())

    def test_str(self):
        st = otio.schema.Stack(name="foo", children=[])
        self.assertMultiLineEqual(
            str(st),
            "Stack(" +
            str(st.name) + ", " +
            str(list(st)) + ", " +
            str(st.source_range) + ", " +
            str(st.metadata) +
            ")"
        )

    def test_repr(self):
        st = otio.schema.Stack(name="foo", children=[])
        self.assertMultiLineEqual(
            repr(st),
            "otio.schema.Stack(" +
            "name=" + repr(st.name) + ", " +
            "children=" + repr(list(st)) + ", " +
            "source_range=" + repr(st.source_range) + ", " +
            "metadata=" + repr(st.metadata) +
            ")"
        )

    def test_trim_child_range(self):
        for st in [
            otio.schema.Track(name="foo"),
            otio.schema.Stack(name="foo")
        ]:
            st.source_range = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=100, rate=24),
                duration=otio.opentime.RationalTime(value=50, rate=24)
            )
            r = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=110, rate=24),
                duration=otio.opentime.RationalTime(value=30, rate=24)
            )
            self.assertEqual(st.trim_child_range(r), r)
            r = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=0, rate=24),
                duration=otio.opentime.RationalTime(value=30, rate=24)
            )
            self.assertEqual(st.trim_child_range(r), None)
            r = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=1000, rate=24),
                duration=otio.opentime.RationalTime(value=30, rate=24)
            )
            self.assertEqual(st.trim_child_range(r), None)
            r = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=90, rate=24),
                duration=otio.opentime.RationalTime(value=30, rate=24)
            )
            self.assertEqual(
                st.trim_child_range(r),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(value=100, rate=24),
                    duration=otio.opentime.RationalTime(value=20, rate=24)
                )
            )
            r = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=110, rate=24),
                duration=otio.opentime.RationalTime(value=50, rate=24)
            )
            self.assertEqual(
                st.trim_child_range(r),
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(value=110, rate=24),
                    duration=otio.opentime.RationalTime(value=40, rate=24)
                )
            )
            r = otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(value=90, rate=24),
                duration=otio.opentime.RationalTime(value=1000, rate=24)
            )
            self.assertEqual(
                st.trim_child_range(r),
                st.source_range
            )

    def test_range_of_child(self):
        st = otio.schema.Stack(name="foo", children=[
            otio.schema.Clip(
                name="clip1",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(value=100, rate=24),
                    duration=otio.opentime.RationalTime(value=50, rate=24)
                )
            ),
            otio.schema.Clip(
                name="clip2",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(value=101, rate=24),
                    duration=otio.opentime.RationalTime(value=50, rate=24)
                )
            ),
            otio.schema.Clip(
                name="clip3",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(value=102, rate=24),
                    duration=otio.opentime.RationalTime(value=50, rate=24)
                )
            )
        ])

        # The Stack should be as long as the longest child
        self.assertEqual(
            st.duration(),
            otio.opentime.RationalTime(value=50, rate=24)
        )

        # Stacked items should all start at time zero
        self.assertEqual(
            st.range_of_child_at_index(0).start_time,
            otio.opentime.RationalTime()
        )
        self.assertEqual(
            st.range_of_child_at_index(1).start_time,
            otio.opentime.RationalTime()
        )
        self.assertEqual(
            st.range_of_child_at_index(2).start_time,
            otio.opentime.RationalTime()
        )

        self.assertEqual(
            st.range_of_child_at_index(0).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEqual(
            st.range_of_child_at_index(1).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEqual(
            st.range_of_child_at_index(2).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )

        self.assertEqual(
            st.range_of_child_at_index(2),
            st.range_of_child(st[2])
        )

    def test_range_of_child_with_duration(self):

        st_sourcerange = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(5, 24),
            duration=otio.opentime.RationalTime(5, 24),
        )
        st = otio.schema.Stack(
            name="foo",
            children=[
                otio.schema.Clip(
                    name="clip1",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip2",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=101,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip3",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=102,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                )
            ],
            source_range=st_sourcerange
        )

        # range always returns the pre-trimmed range.  To get the post-trim
        # range, call .trimmed_range()
        self.assertEqual(
            # get the pre-trimmed range in the reference space of the parent
            st.range_of_child(st[0], reference_space=st),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(50, 24)
            )
        )

        self.assertEqual(
            st.transformed_time(otio.opentime.RationalTime(25, 24), st[0]),
            otio.opentime.RationalTime(125, 24)
        )
        self.assertEqual(
            (st[0]).transformed_time(otio.opentime.RationalTime(125, 24), st),
            otio.opentime.RationalTime(25, 24)
        )

        # # in the space of the child
        # self.assertEqual(
        #     # get the pre-trimmed range in the reference space of the parent
        #     st.range_of_child(st[0], reference_space=st[0]),
        #     otio.opentime.TimeRange(
        #         start_time=otio.opentime.RationalTime(105,24),
        #         duration=otio.opentime.RationalTime(5,24)
        #     )
        # )

        # trimmed_ functions take into account the source_range
        self.assertEqual(
            st.trimmed_range_of_child_at_index(0),
            st.source_range
        )

        self.assertEqual(
            st.trimmed_range_of_child(st[0], reference_space=st),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(5, 24),
                duration=otio.opentime.RationalTime(5, 24)
            )
        )

        # get the trimmed range in the parent
        self.assertEqual(
            st[0].trimmed_range_in_parent(),
            st.trimmed_range_of_child(st[0], reference_space=st),
        )

        # same test but via iteration
        for i, c in enumerate(st):
            self.assertEqual(
                st[i].trimmed_range_in_parent(),
                st.trimmed_range_of_child(st[i], reference_space=st),
            )

        with self.assertRaises(otio.exceptions.NotAChildError):
            otio.schema.Clip().trimmed_range_in_parent()

    def test_transformed_time(self):
        st = otio.schema.Stack(
            name="foo",
            children=[
                otio.schema.Clip(
                    name="clip1",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip2",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=101,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip3",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=102,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                )
            ],
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(5, 24),
                duration=otio.opentime.RationalTime(5, 24),
            )
        )

        clip1 = st[0]
        clip2 = st[1]
        clip3 = st[2]
        self.assertEqual(clip1.name, "clip1")
        self.assertEqual(clip2.name, "clip2")
        self.assertEqual(clip3.name, "clip3")

        test_time = otio.opentime.RationalTime(0, 24)
        self.assertEqual(
            st.transformed_time(test_time, clip1),
            otio.opentime.RationalTime(100, 24)
        )

        # ensure that transformed_time does not edit in place
        self.assertEqual(test_time, otio.opentime.RationalTime(0, 24))

        self.assertEqual(
            st.transformed_time(otio.opentime.RationalTime(0, 24), clip2),
            otio.opentime.RationalTime(101, 24)
        )
        self.assertEqual(
            st.transformed_time(otio.opentime.RationalTime(0, 24), clip3),
            otio.opentime.RationalTime(102, 24)
        )

        self.assertEqual(
            st.transformed_time(otio.opentime.RationalTime(50, 24), clip1),
            otio.opentime.RationalTime(150, 24)
        )
        self.assertEqual(
            st.transformed_time(otio.opentime.RationalTime(50, 24), clip2),
            otio.opentime.RationalTime(151, 24)
        )
        self.assertEqual(
            st.transformed_time(otio.opentime.RationalTime(50, 24), clip3),
            otio.opentime.RationalTime(152, 24)
        )

        self.assertEqual(
            clip1.transformed_time(otio.opentime.RationalTime(100, 24), st),
            otio.opentime.RationalTime(0, 24)
        )
        self.assertEqual(
            clip2.transformed_time(otio.opentime.RationalTime(101, 24), st),
            otio.opentime.RationalTime(0, 24)
        )
        self.assertEqual(
            clip3.transformed_time(otio.opentime.RationalTime(102, 24), st),
            otio.opentime.RationalTime(0, 24)
        )

        self.assertEqual(
            clip1.transformed_time(otio.opentime.RationalTime(150, 24), st),
            otio.opentime.RationalTime(50, 24)
        )
        self.assertEqual(
            clip2.transformed_time(otio.opentime.RationalTime(151, 24), st),
            otio.opentime.RationalTime(50, 24)
        )
        self.assertEqual(
            clip3.transformed_time(otio.opentime.RationalTime(152, 24), st),
            otio.opentime.RationalTime(50, 24)
        )

    def test_available_image_bounds_single_clip(self):
        st = otio.schema.Stack(name="foo", children=[
            otio.schema.Gap(name="GAP1")
        ])

        # There's noting valid, we should have no available_image_bounds
        self.assertEqual(st.available_image_bounds, None)

        clip = otio.schema.Clip(
            media_reference=otio.schema.ExternalReference(
                available_image_bounds=otio.schema.Box2d(
                    otio.schema.V2d(1, 1),
                    otio.schema.V2d(2, 2)
                ),
                target_url="/var/tmp/test.mov"
            ),
            name="clip1"
        )

        # The Stack available_image_bounds should be equal to
        # the single clip that's in it
        st.append(clip)
        self.assertEqual(st.available_image_bounds, clip.available_image_bounds)

    def test_available_image_bounds_multi_clip(self):
        st = otio.schema.Stack(name="foo", children=[
            otio.schema.Gap(name="GAP1"),
            otio.schema.Clip(
                media_reference=otio.schema.ExternalReference(
                    available_image_bounds=otio.schema.Box2d(
                        otio.schema.V2d(1, 1),
                        otio.schema.V2d(2, 2)
                    ),
                    target_url="/var/tmp/test.mov"
                ),
                name="clip1"
            ),
            otio.schema.Gap(name="GAP2"),
            otio.schema.Clip(
                media_reference=otio.schema.ExternalReference(
                    available_image_bounds=otio.schema.Box2d(
                        otio.schema.V2d(2, 2),
                        otio.schema.V2d(3, 3)
                    ),
                    target_url="/var/tmp/test.mov"
                ),
                name="clip2"
            ),
            otio.schema.Gap(name="GAP3"),
            otio.schema.Clip(
                media_reference=otio.schema.ExternalReference(
                    available_image_bounds=otio.schema.Box2d(
                        otio.schema.V2d(3, 3),
                        otio.schema.V2d(4, 4)
                    ),
                    target_url="/var/tmp/test.mov"
                ),
                name="clip3"
            ),
            otio.schema.Gap(name="GAP4")
        ])

        # The Stack available_image_bounds should cover the overlapping boxes,
        # the gaps should be ignored
        self.assertEqual(st.available_image_bounds,
                         otio.schema.Box2d(
                             otio.schema.V2d(1, 1),
                             otio.schema.V2d(4, 4)
                         )
                         )

    def test_available_image_bounds_multi_layer(self):
        tr1 = otio.schema.Track(name="tr1", children=[
            otio.schema.Gap(name="GAP1")
        ])
        st = otio.schema.Stack(name="foo", children=[tr1])

        self.assertEqual(st.available_image_bounds, tr1.available_image_bounds)
        self.assertEqual(st.available_image_bounds, None)

        cl1 = otio.schema.Clip(
            media_reference=otio.schema.ExternalReference(
                available_image_bounds=otio.schema.Box2d(
                    otio.schema.V2d(0, 0),
                    otio.schema.V2d(2, 2)
                ),
                target_url="/var/tmp/test.mov"
            ),
            name="clip1"
        )
        tr1.append(cl1)

        self.assertEqual(st.available_image_bounds, cl1.available_image_bounds)
        self.assertEqual(st.available_image_bounds, tr1.available_image_bounds)

        tr2 = otio.schema.Track(name="tr2", children=[
            otio.schema.Gap(name="GAP2")
        ])
        st.append(tr2)

        self.assertEqual(st.available_image_bounds, cl1.available_image_bounds)
        self.assertEqual(st.available_image_bounds, tr1.available_image_bounds)

        cl2 = otio.schema.Clip(
            media_reference=otio.schema.ExternalReference(
                available_image_bounds=otio.schema.Box2d(
                    otio.schema.V2d(1, 1),
                    otio.schema.V2d(3, 3)
                ),
                target_url="/var/tmp/test.mov"
            ),
            name="clip2"
        )
        tr2.append(cl2)

        # Each track should have available_image_bounds equal to its single clip,
        # but the stack available_image_bounds should use both tracks
        self.assertEqual(tr1.available_image_bounds, cl1.available_image_bounds)
        self.assertEqual(tr2.available_image_bounds, cl2.available_image_bounds)

        union = st.available_image_bounds
        self.assertEqual(union,
                         otio.schema.Box2d(
                             otio.schema.V2d(0, 0),
                             otio.schema.V2d(3, 3)
                         )
                         )

        # Appending a track with no available_image_bounds should do nothing
        st.append(otio.schema.Track())
        union2 = st.available_image_bounds
        self.assertEqual(union, union2)


class TrackTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_serialize(self):
        sq = otio.schema.Track(name="foo", children=[])

        encoded = otio.adapters.otio_json.write_to_string(sq)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertIsOTIOEquivalentTo(sq, decoded)

    def test_str(self):
        sq = otio.schema.Track(name="foo", children=[])
        self.assertMultiLineEqual(
            str(sq),
            "Track(" +
            str(sq.name) + ", " +
            str(list(sq)) + ", " +
            str(sq.source_range) + ", " +
            str(sq.metadata) +
            ")"
        )

    def test_repr(self):
        sq = otio.schema.Track(name="foo", children=[])
        self.assertMultiLineEqual(
            repr(sq),
            "otio.schema.Track(" +
            "name=" + repr(sq.name) + ", " +
            "children=" + repr(list(sq)) + ", " +
            "source_range=" + repr(sq.source_range) + ", " +
            "metadata=" + repr(sq.metadata) +
            ")"
        )

    def test_instancing(self):
        length = otio.opentime.RationalTime(5, 1)
        tr = otio.opentime.TimeRange(otio.opentime.RationalTime(), length)
        it = otio.core.Item(source_range=tr)
        sq = otio.schema.Track(children=[it])
        self.assertEqual(sq.range_of_child_at_index(0), tr)

        # Can't put item on a composition if it's already in one
        with self.assertRaises(ValueError):
            otio.schema.Track(children=[it])

        # Instancing is not allowed
        with self.assertRaises(ValueError):
            otio.schema.Track(children=[it, it, it])

        # inserting duplicates should raise and have no
        # side effects
        self.assertEqual(len(sq), 1)
        with self.assertRaises(ValueError):
            sq.append(it)
        self.assertEqual(len(sq), 1)

        self.assertEqual(len(sq), 1)
        with self.assertRaises(ValueError):
            sq[:] = [it, it]
        self.assertEqual(len(sq), 1)

        self.assertEqual(len(sq), 1)
        with self.assertRaises(ValueError):
            sq.insert(1, it)
        self.assertEqual(len(sq), 1)

        sq[0] = it
        self.assertEqual(len(sq), 1)

        sq[:] = [it]
        self.assertEqual(len(sq), 1)

        sq.append(copy.deepcopy(it))
        self.assertEqual(len(sq), 2)
        with self.assertRaises(ValueError):
            sq[1:] = [it, copy.deepcopy(it)]
        self.assertEqual(len(sq), 2)

    def test_delete_parent_container(self):
        # deleting the parent container should null out the parent pointer
        it = otio.core.Item()
        sq = otio.schema.Track(children=[it])
        del sq
        self.assertIsNone(it.parent())

    def test_transactional(self):
        item = otio.core.Item()
        trackA = otio.core.Track()
        trackB = otio.core.Track()

        trackA.extend([item.clone(), item.clone(), item.clone()])
        self.assertEqual(len(trackA), 3)

        trackB.extend([item.clone(), item.clone(), item.clone()])
        self.assertEqual(len(trackB), 3)

        cached_contents = list(trackA)

        with self.assertRaises(ValueError):
            trackA[1:] = [
                item.clone(),
                item.clone(),
                item.clone(),
                item.clone(),
                trackB[0]
            ]
        self.assertEqual(len(trackA), 3)

        with self.assertRaises(ValueError):
            trackA[-1:] = [item.clone(), item.clone(), trackB[0]]
        self.assertEqual(len(trackA), 3)
        self.assertEqual(cached_contents, list(trackA))

    def test_range(self):
        length = otio.opentime.RationalTime(5, 1)
        tr = otio.opentime.TimeRange(otio.opentime.RationalTime(), length)
        it = otio.core.Item(source_range=tr)
        sq = otio.schema.Track(children=[it])
        self.assertEqual(sq.range_of_child_at_index(0), tr)

        # It is an error to add an item to composition if it is already in
        # another composition.  This clears out the old test composition
        # (and also clears out its parent pointers).
        del sq[0]
        sq = otio.schema.Track(
            children=[it, it.clone(), it.clone(), it.clone()],
        )
        self.assertEqual(
            sq.range_of_child_at_index(index=1),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(5, 1),
                otio.opentime.RationalTime(5, 1)
            )
        )
        self.assertEqual(
            sq.range_of_child_at_index(index=0),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 1),
                otio.opentime.RationalTime(5, 1)
            )
        )
        self.assertEqual(
            sq.range_of_child_at_index(index=-1),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(15, 1),
                otio.opentime.RationalTime(5, 1)
            )
        )
        with self.assertRaises(IndexError):
            sq.range_of_child_at_index(index=11)
        self.assertEqual(sq.duration(), length + length + length + length)

        # add a transition to either side
        in_offset = otio.opentime.RationalTime(10, 24)
        out_offset = otio.opentime.RationalTime(12, 24)
        range_of_item = sq.range_of_child_at_index(index=3)
        trx = otio.schema.Transition()
        trx.in_offset = in_offset
        trx.out_offset = out_offset
        sq.insert(0, copy.deepcopy(trx))
        sq.insert(3, copy.deepcopy(trx))
        sq.append(copy.deepcopy(trx))

        # range of Transition
        self.assertEqual(
            sq.range_of_child_at_index(index=3),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(230, 24),
                otio.opentime.RationalTime(22, 24)
            )
        )
        self.assertEqual(
            sq.range_of_child_at_index(index=-1),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(470, 24),
                otio.opentime.RationalTime(22, 24)
            )
        )

        # range of Item is not altered by insertion of transitions
        self.assertEqual(
            sq.range_of_child_at_index(index=5),
            range_of_item
        )

        # in_offset and out_offset for the beginning and ending
        self.assertEqual(
            sq.duration(),
            in_offset + length + length + length + length + out_offset
        )

    def test_range_of_child(self):
        sq = otio.schema.Track(
            name="foo",
            children=[
                otio.schema.Clip(
                    name="clip1",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip2",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=101,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip3",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=102,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                )
            ]
        )

        # The Track should be as long as the children summed up
        self.assertEqual(
            sq.duration(),
            otio.opentime.RationalTime(value=150, rate=24)
        )

        # @TODO: should include time transforms

        # Sequenced items should all land end-to-end
        self.assertEqual(
            sq.range_of_child_at_index(0).start_time,
            otio.opentime.RationalTime()
        )
        self.assertEqual(
            sq.range_of_child_at_index(1).start_time,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEqual(
            sq.range_of_child_at_index(2).start_time,
            otio.opentime.RationalTime(value=100, rate=24)
        )
        self.assertEqual(
            sq.range_of_child(sq[2]),
            sq.range_of_child_at_index(2)
        )

        self.assertEqual(
            sq.range_of_child_at_index(0).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEqual(
            sq.range_of_child_at_index(1).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEqual(
            sq.range_of_child_at_index(2).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )

        # should trim 5 frames off the front, and 5 frames off the back
        sq_sourcerange = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(5, 24),
            duration=otio.opentime.RationalTime(140, 24),
        )
        sq.source_range = sq_sourcerange
        self.assertEqual(
            sq.trimmed_range_of_child_at_index(0),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(5, 24),
                otio.opentime.RationalTime(45, 24)
            )
        )
        self.assertEqual(
            sq.trimmed_range_of_child_at_index(1),
            sq.range_of_child_at_index(1)
        )
        self.assertEqual(
            sq.trimmed_range_of_child_at_index(2),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(100, 24),
                otio.opentime.RationalTime(45, 24),
            )
        )

        # get the trimmed range in the parent
        self.assertEqual(
            sq[0].trimmed_range_in_parent(),
            sq.trimmed_range_of_child(sq[0], reference_space=sq),
        )

        # same tesq but via iteration
        for i, c in enumerate(sq):
            self.assertEqual(
                c.trimmed_range_in_parent(),
                sq.trimmed_range_of_child_at_index(i)
            )

        with self.assertRaises(otio.exceptions.NotAChildError):
            otio.schema.Clip().trimmed_range_in_parent()

    def test_range_trimmed_out(self):
        track = otio.schema.Track(
            name="top_track",
            children=[
                otio.schema.Clip(
                    name="clip1",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip2",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=101,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
            ],
            # should trim out clip 1
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(60, 24),
                duration=otio.opentime.RationalTime(10, 24)
            )
        )

        # should be trimmed out, at the moment, the sentinel for that is None
        with self.assertRaises(ValueError):
            track.trimmed_range_of_child_at_index(0)

        not_nothing = track.trimmed_range_of_child_at_index(1)
        self.assertEqual(not_nothing, track.source_range)

        # should trim out second clip
        track.source_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(0, 24),
            duration=otio.opentime.RationalTime(10, 24)
        )

        with self.assertRaises(ValueError):
            track.trimmed_range_of_child_at_index(1)

        with self.assertRaises(ValueError):
            track[1].trimmed_range_in_parent()

        not_nothing = track.trimmed_range_of_child_at_index(0)
        self.assertEqual(not_nothing, track.source_range)

    def test_range_nested(self):
        track = otio.schema.Track(
            name="inner",
            children=[
                otio.schema.Clip(
                    name="clip1",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip2",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=101,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip3",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=102,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                )
            ]
        )

        self.assertEqual(len(track), 3)
        self.assertEqual(len(track.deepcopy()), 3)

        # make a nested track with 3 sub-tracks, each with 3 clips
        outer_track = otio.schema.Track(name="outer", children=[
            track.deepcopy(),
            track.deepcopy(),
            track.deepcopy()
        ])

        # make one long track with 9 clips
        long_track = otio.schema.Track(name="long", children=(
            track.deepcopy()[:] + track.deepcopy()[:] + track.deepcopy()[:]
        ))

        # the original track's children should have been copied
        with self.assertRaises(otio.exceptions.NotAChildError):
            outer_track.range_of_child(track[1])

        with self.assertRaises(otio.exceptions.NotAChildError):
            long_track.range_of_child(track[1])

        # the nested and long tracks should be the same length
        self.assertEqual(
            outer_track.duration(),
            long_track.duration()
        )

        # the 9 clips within both compositions should have the same
        # overall timing, even though the nesting is different.
        self.assertListEqual(
            [
                outer_track.range_of_child(clip)
                for clip in outer_track.clip_if()
            ],
            [
                long_track.range_of_child(clip)
                for clip in long_track.clip_if()
            ]
        )

    def test_setitem(self):
        seq = otio.schema.Track()
        it = otio.schema.Clip()
        it_2 = otio.schema.Clip()

        seq.append(it)
        self.assertEqual(len(seq), 1)

        seq[0] = it_2
        self.assertEqual(len(seq), 1)

    def test_transformed_time(self):
        sq = otio.schema.Track(
            name="foo",
            children=[
                otio.schema.Clip(
                    name="clip1",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip2",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=101,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                ),
                otio.schema.Clip(
                    name="clip3",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=102,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=50,
                            rate=24
                        )
                    )
                )
            ]
        )
        fl = otio.schema.Gap(
            name="GAP",
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(
                    value=0,
                    rate=24
                ),
                duration=otio.opentime.RationalTime(
                    value=50,
                    rate=24
                )
            )
        )
        self.assertFalse(fl.visible())
        clip1 = sq[0]
        clip2 = sq[1]
        clip3 = sq[2]
        self.assertEqual(clip1.name, "clip1")
        self.assertEqual(clip2.name, "clip2")
        self.assertEqual(clip3.name, "clip3")

        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(-1, 24)
                    )
                )
            ),
            []
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(0, 24)
                    )
                )
            ),
            [clip1]
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(49, 24)
                    )
                )
            ),
            [clip1]
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(50, 24)
                    )
                )
            ),
            [clip2]
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(99, 24)
                    )
                )
            ),
            [clip2]
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(100, 24)
                    )
                )
            ),
            [clip3]
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(149, 24)
                    )
                )
            ),
            [clip3]
        )
        self.assertEqual(
            list(
                sq.clip_if(
                    otio.opentime.TimeRange(
                        otio.opentime.RationalTime(150, 24)
                    )
                )
            ),
            []
        )

        self.assertEqual(
            sq.transformed_time(otio.opentime.RationalTime(0, 24), clip1),
            otio.opentime.RationalTime(100, 24)
        )
        self.assertEqual(
            sq.transformed_time(otio.opentime.RationalTime(0, 24), clip2),
            otio.opentime.RationalTime(51, 24)
        )
        self.assertEqual(
            sq.transformed_time(otio.opentime.RationalTime(0, 24), clip3),
            otio.opentime.RationalTime(2, 24)
        )

        self.assertEqual(
            sq.transformed_time(otio.opentime.RationalTime(50, 24), clip1),
            otio.opentime.RationalTime(150, 24)
        )
        self.assertEqual(
            sq.transformed_time(otio.opentime.RationalTime(50, 24), clip2),
            otio.opentime.RationalTime(101, 24)
        )
        self.assertEqual(
            sq.transformed_time(otio.opentime.RationalTime(50, 24), clip3),
            otio.opentime.RationalTime(52, 24)
        )

        self.assertEqual(
            clip1.transformed_time(otio.opentime.RationalTime(100, 24), sq),
            otio.opentime.RationalTime(0, 24)
        )
        self.assertEqual(
            clip2.transformed_time(otio.opentime.RationalTime(101, 24), sq),
            otio.opentime.RationalTime(50, 24)
        )
        self.assertEqual(
            clip3.transformed_time(otio.opentime.RationalTime(102, 24), sq),
            otio.opentime.RationalTime(100, 24)
        )

        self.assertEqual(
            clip1.transformed_time(otio.opentime.RationalTime(150, 24), sq),
            otio.opentime.RationalTime(50, 24)
        )
        self.assertEqual(
            clip2.transformed_time(otio.opentime.RationalTime(151, 24), sq),
            otio.opentime.RationalTime(100, 24)
        )
        self.assertEqual(
            clip3.transformed_time(otio.opentime.RationalTime(152, 24), sq),
            otio.opentime.RationalTime(150, 24)
        )

    def test_neighbors_of_simple(self):
        seq = otio.schema.Track()
        trans = otio.schema.Transition(
            in_offset=otio.opentime.RationalTime(10, 24),
            out_offset=otio.opentime.RationalTime(10, 24)
        )
        seq.append(trans)

        # neighbors of first transition
        neighbors = seq.neighbors_of(
            seq[0],
            otio.schema.NeighborGapPolicy.never
        )
        self.assertEqual(neighbors, (None, None))

        # test with the neighbor filling policy on
        neighbors = seq.neighbors_of(
            seq[0],
            otio.schema.NeighborGapPolicy.around_transitions
        )
        fill = otio.schema.Gap(
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, trans.in_offset.rate),
                duration=trans.in_offset
            )
        )
        self.assertJsonEqual(neighbors, (fill, fill.clone()))

    def test_neighbors_of_no_expand(self):
        seq = otio.schema.Track()
        seq.append(otio.schema.Clip())
        n = seq.neighbors_of(seq[0])
        self.assertEqual(n, (None, None))
        self.assertIs(n[0], (None))
        self.assertIs(n[1], (None))

    def test_neighbors_of_from_data(self):
        self.maxDiff = None

        edl_path = TRANSITION_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)

        # track is [t, clip, t, clip, clip, t]
        seq = timeline.tracks[0]

        # neighbors of first transition
        neighbors = seq.neighbors_of(
            seq[0],
            otio.schema.NeighborGapPolicy.never
        )
        self.assertEqual(neighbors, (None, seq[1]))

        fill = otio.schema.Gap(
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, seq[0].in_offset.rate),
                duration=seq[0].in_offset
            )
        )

        neighbors = seq.neighbors_of(
            seq[0],
            otio.schema.NeighborGapPolicy.around_transitions
        )
        self.assertJsonEqual(neighbors, (fill, seq[1]))

        # neighbor around second transition
        neighbors = seq.neighbors_of(
            seq[2],
            otio.schema.NeighborGapPolicy.never
        )
        self.assertEqual(neighbors, (seq[1], seq[3]))

        # no change w/ different policy
        neighbors = seq.neighbors_of(
            seq[2],
            otio.schema.NeighborGapPolicy.around_transitions
        )
        self.assertEqual(neighbors, (seq[1], seq[3]))

        # neighbor around third transition
        neighbors = seq.neighbors_of(
            seq[5],
            otio.schema.NeighborGapPolicy.never
        )
        self.assertEqual(neighbors, (seq[4], None))

        fill = otio.schema.Gap(
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, seq[5].out_offset.rate),
                duration=seq[5].out_offset
            )
        )

        neighbors = seq.neighbors_of(
            seq[5],
            otio.schema.NeighborGapPolicy.around_transitions
        )
        self.assertJsonEqual(neighbors, (seq[4], fill))

    def test_track_range_of_all_children(self):
        edl_path = TRANSITION_EXAMPLE_PATH
        timeline = otio.adapters.read_from_file(edl_path)
        tr = timeline.tracks[0]
        mp = tr.range_of_all_children()

        # fetch all the valid children that should be in the map
        vc = list(tr.clip_if())

        self.assertEqual(mp[vc[0]].start_time.value, 0)
        self.assertEqual(mp[vc[1]].start_time, mp[vc[0]].duration)

        for track in timeline.tracks:
            for child in track:
                self.assertEqual(child.range_in_parent(), mp[child])

        track = otio.schema.Track()
        self.assertEqual(track.range_of_all_children(), {})


class EdgeCases(unittest.TestCase):

    def test_empty_compositions(self):
        timeline = otio.schema.Timeline()

        self.assertEqual(len(timeline.tracks), 0)
        self.assertEqual(
            timeline.tracks.duration(),
            otio.opentime.RationalTime(0, 24)
        )

    def test_iterating_over_dupes(self):
        timeline = otio.schema.Timeline()
        track = otio.schema.Track()
        timeline.tracks.append(track)
        clip = otio.schema.Clip(
            name="Dupe",
            source_range=otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(10, 30),
                duration=otio.opentime.RationalTime(15, 30)
            )
        )

        # make several identical copies
        for i in range(10):
            dupe = copy.deepcopy(clip)
            track.append(dupe)
        self.assertEqual(len(track), 10)
        self.assertEqual(
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 30),
                duration=otio.opentime.RationalTime(150, 30)
            ),
            track.trimmed_range()
        )

        # test normal iteration
        previous = None
        for item in track:
            self.assertEqual(
                track.range_of_child(item),
                item.range_in_parent()
            )
            self.assertNotEqual(
                item.range_in_parent(),
                previous
            )
            previous = item.range_in_parent()

        # test recursive iteration
        previous = None
        for item in track.clip_if():
            self.assertEqual(
                track.range_of_child(item),
                item.range_in_parent()
            )
            self.assertNotEqual(
                item.range_in_parent(),
                previous
            )
            previous = item.range_in_parent()

        # compare to iteration by index
        previous = None
        for i, item in enumerate(track):
            self.assertEqual(
                track.range_of_child(item),
                track.range_of_child_at_index(i)
            )
            self.assertEqual(
                track.range_of_child(item),
                item.range_in_parent()
            )
            self.assertNotEqual(
                item.range_in_parent(),
                previous
            )
            previous = item.range_in_parent()

        # compare recursive to iteration by index
        previous = None
        for i, item in enumerate(track.clip_if()):
            self.assertEqual(
                track.range_of_child(item),
                track.range_of_child_at_index(i)
            )
            self.assertEqual(
                track.range_of_child(item),
                item.range_in_parent()
            )
            self.assertNotEqual(
                item.range_in_parent(),
                previous
            )
            previous = item.range_in_parent()


class NestingTest(unittest.TestCase):

    def test_deeply_nested(self):
        # Take a single clip of media (frames 100-200) and nest it into a bunch
        # of layers
        # Nesting it should not shift the media at all.
        # At one level:
        # Timeline:
        #  Stack: [0-99]
        #   Track: [0-99]
        #    Clip: [100-199]
        #     Media Reference: [100-199]

        # here are some times in the top-level coordinate system
        zero = otio.opentime.RationalTime(0, 24)
        one = otio.opentime.RationalTime(1, 24)
        fifty = otio.opentime.RationalTime(50, 24)
        ninetynine = otio.opentime.RationalTime(99, 24)
        onehundred = otio.opentime.RationalTime(100, 24)
        top_level_range = otio.opentime.TimeRange(
            start_time=zero, duration=onehundred)

        # here are some times in the media-level coordinate system
        first_frame = otio.opentime.RationalTime(100, 24)
        middle = otio.opentime.RationalTime(150, 24)
        last = otio.opentime.RationalTime(199, 24)
        media_range = otio.opentime.TimeRange(
            start_time=first_frame, duration=onehundred)

        timeline = otio.schema.Timeline()
        stack = timeline.tracks
        track = otio.schema.Track()
        clip = otio.schema.Clip()
        media = otio.schema.MissingReference()
        media.available_range = media_range
        clip.media_reference = media
        track.append(clip)
        stack.append(track)

        self.assertIs(track, clip.parent())
        self.assertIs(stack, track.parent())

        # the clip and track should auto-size to fit the media, since we
        # haven't trimmed anything
        self.assertEqual(clip.duration(), onehundred)
        self.assertEqual(track.duration(), onehundred)
        self.assertEqual(stack.duration(), onehundred)

        # the ranges should match our expectations...
        self.assertEqual(clip.trimmed_range(), media_range)
        self.assertEqual(track.trimmed_range(), top_level_range)
        self.assertEqual(stack.trimmed_range(), top_level_range)

        # verify that the media is where we expect
        self.assertEqual(stack.transformed_time(zero, clip), first_frame)
        self.assertEqual(stack.transformed_time(fifty, clip), middle)
        self.assertEqual(stack.transformed_time(ninetynine, clip), last)

        def _nest(self, item):

            self.assertIsNotNone(item)
            self.assertIsNotNone(item.parent())

            parent = item.parent()
            index = parent.index(item)
            wrapper = otio.schema.Stack()

            self.assertIs(parent[index], item)

            # swap out the item for the wrapper
            parent[index] = wrapper

            self.assertIs(parent[index], wrapper)
            self.assertIsNot(parent[index], item)

            self.assertIs(wrapper.parent(), parent)

            # now put the item inside the wrapper
            wrapper.append(item)

            self.assertIs(item.parent(), wrapper)

            return wrapper

        # now nest it many layers deeper
        wrappers = []
        num_wrappers = 10
        for i in range(num_wrappers):
            # print "Nesting", (i+1), "levels deep"
            wrapper = _nest(self, clip)
            wrappers.append(wrapper)

        # nothing should have shifted at all

        # print otio.adapters.otio_json.write_to_string(timeline)

        # the clip and track should auto-size to fit the media, since we
        # haven't trimmed anything
        self.assertEqual(clip.duration(), onehundred)
        self.assertEqual(track.duration(), onehundred)
        self.assertEqual(stack.duration(), onehundred)

        # the ranges should match our expectations...
        self.assertEqual(clip.trimmed_range(), media_range)
        self.assertEqual(track.trimmed_range(), top_level_range)
        self.assertEqual(stack.trimmed_range(), top_level_range)

        # verify that the media is where we expect
        self.assertEqual(stack.transformed_time(zero, clip), first_frame)
        self.assertEqual(stack.transformed_time(fifty, clip), middle)
        self.assertEqual(stack.transformed_time(ninetynine, clip), last)

        # now trim them all by one frame at each end
        self.assertEqual(ninetynine, ninetynine)
        self.assertEqual(ninetynine + one, onehundred)
        trim = otio.opentime.TimeRange(
            start_time=one,
            duration=(ninetynine - one)
        )
        self.assertEqual(trim.duration, otio.opentime.RationalTime(98, 24))
        for wrapper in wrappers:
            wrapper.source_range = trim

        # print otio.adapters.otio_json.write_to_string(timeline)

        # the clip should be the same
        self.assertEqual(clip.duration(), onehundred)

        # the parents should have shrunk by only 2 frames
        self.assertEqual(track.duration(), otio.opentime.RationalTime(98, 24))
        self.assertEqual(stack.duration(), otio.opentime.RationalTime(98, 24))

        # but the media should have shifted over by 1 one frame for each level
        # of nesting
        ten = otio.opentime.RationalTime(num_wrappers, 24)
        self.assertEqual(
            stack.transformed_time(zero, clip),
            first_frame + ten
        )
        self.assertEqual(stack.transformed_time(fifty, clip), middle + ten)
        self.assertEqual(stack.transformed_time(ninetynine, clip), last + ten)

    def test_child_at_time_with_children(self):
        sq = otio.schema.Track(
            name="foo",
            children=[
                otio.schema.Clip(
                    name="leader",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=100,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=10,
                            rate=24
                        )
                    )
                ),
                otio.schema.Track(
                    name="body",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=9,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=12,
                            rate=24
                        )
                    ),
                    children=[
                        otio.schema.Clip(
                            name="clip1",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=100,
                                    rate=24
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=10,
                                    rate=24
                                )
                            )
                        ),
                        otio.schema.Clip(
                            name="clip2",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=101,
                                    rate=24
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=10,
                                    rate=24
                                )
                            )
                        ),
                        otio.schema.Clip(
                            name="clip3",
                            source_range=otio.opentime.TimeRange(
                                start_time=otio.opentime.RationalTime(
                                    value=102,
                                    rate=24
                                ),
                                duration=otio.opentime.RationalTime(
                                    value=10,
                                    rate=24
                                )
                            )
                        )
                    ]
                ),
                otio.schema.Clip(
                    name="credits",
                    source_range=otio.opentime.TimeRange(
                        start_time=otio.opentime.RationalTime(
                            value=102,
                            rate=24
                        ),
                        duration=otio.opentime.RationalTime(
                            value=10,
                            rate=24
                        )
                    )
                )
            ]
        )

        """
        Looks like this:
        [ leader ][ body ][ credits ]
        10 f       12f     10f

        body: (source range starts: 9f duration: 12f)
        [ clip1 ][ clip2 ][ clip 3]
        1f       11f
        """

        leader = sq[0]
        body = sq[1]
        credits = sq[2]
        clip1 = body[0]
        clip2 = body[1]
        clip3 = body[2]
        self.assertEqual(leader.name, "leader")
        self.assertEqual(body.name, "body")
        self.assertEqual(credits.name, "credits")
        self.assertEqual(clip1.name, "clip1")
        self.assertEqual(clip2.name, "clip2")
        self.assertEqual(clip3.name, "clip3")

        expected = [
            ('leader', 100),
            ('leader', 101),
            ('leader', 102),
            ('leader', 103),
            ('leader', 104),
            ('leader', 105),
            ('leader', 106),
            ('leader', 107),
            ('leader', 108),
            ('leader', 109),
            ('clip1', 109),
            ('clip2', 101),
            ('clip2', 102),
            ('clip2', 103),
            ('clip2', 104),
            ('clip2', 105),
            ('clip2', 106),
            ('clip2', 107),
            ('clip2', 108),
            ('clip2', 109),
            ('clip2', 110),
            ('clip3', 102),
            ('credits', 102),
            ('credits', 103),
            ('credits', 104),
            ('credits', 105),
            ('credits', 106),
            ('credits', 107),
            ('credits', 108),
            ('credits', 109),
            ('credits', 110),
            ('credits', 111)
        ]

        for frame, expected_val in enumerate(expected):
            # first test child_at_time
            playhead = otio.opentime.RationalTime(frame, 24)
            item = sq.child_at_time(playhead)
            mediaframe = sq.transformed_time(playhead, item)

            measured_val = (item.name, otio.opentime.to_frames(mediaframe, 24))

            self.assertEqual(
                measured_val,
                expected_val,
                msg="Error with Search Time: {}, expected: {}, "
                "got {}".format(playhead, expected_val, measured_val)
            )

            # then test clip_if
            search_range = otio.opentime.TimeRange(
                otio.opentime.RationalTime(frame, 24),
                # with a 0 duration, should have the same result as above
            )

            item = list(sq.clip_if(search_range))[0]
            mediaframe = sq.transformed_time(playhead, item)

            measured_val = (item.name, otio.opentime.to_frames(mediaframe, 24))

            self.assertEqual(
                measured_val,
                expected_val,
                msg="Error with Search Time: {}, expected: {}, "
                "got {}".format(playhead, expected_val, measured_val)
            )


class MembershipTest(unittest.TestCase, otio_test_utils.OTIOAssertions):

    def test_remove_actually_removes(self):
        """Test that removed item is no longer 'in' composition."""
        tr = otio.schema.Track()
        cl = otio.schema.Clip()

        # test inclusion
        tr.append(cl)
        self.assertIn(cl, tr)

        # delete by index
        del tr[0]
        self.assertNotIn(cl, tr)

        # delete by slice
        tr = otio.schema.Track()
        tr.append(cl)
        del tr[:]
        self.assertNotIn(cl, tr)

        # delete by setting over item
        tr = otio.schema.Track()
        tr.append(cl)
        cl2 = otio.schema.Clip()
        tr[0] = cl2
        self.assertNotIn(cl, tr)

        # delete by pop
        tr = otio.schema.Track()
        tr.insert(0, cl)
        tr.pop()
        self.assertNotIn(cl, tr)


if __name__ == '__main__':
    unittest.main()
