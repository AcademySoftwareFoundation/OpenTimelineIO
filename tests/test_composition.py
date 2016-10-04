#!/usr/bin/env python

import unittest

import opentimelineio as otio


class CompositionTests(unittest.TestCase):

    def test_cons(self):
        it = otio.core.Item()
        co = otio.core.Composition(name="test", children=[it])
        self.assertEquals(co.name, "test")
        self.assertEquals(co._children, [it])
        self.assertEquals(co.composition_kind, "Composition")

    def test_iterable(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertEquals(co[0], it)
        self.assertEquals([i for i in co], [it])
        self.assertEquals(len(co), 1)

    def test_parent_manip(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertEquals(it._parent, co)


class StackTest(unittest.TestCase):

    def test_cons(self):
        st = otio.schema.Stack(name="test")
        self.assertEquals(st.name, "test")

    def test_serialize(self):
        st = otio.schema.Stack(name="test", children=[])

        encoded = otio.adapters.otio_json.write_to_string(st)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEquals(st, decoded)

    def test_str(self):
        st = otio.schema.Stack(name="foo", children=[])
        self.assertMultiLineEqual(
            str(st),
            "Stack(" +
            str(st.name) + ", " +
            str(st._children) + ", " +
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
            "children=" + repr(st._children) + ", " +
            "source_range=" + repr(st.source_range) + ", " +
            "metadata=" + repr(st.metadata) +
            ")"
        )

    def test_range_of_child(self):
        st = otio.schema.Stack(name="foo", children=[
            otio.schema.Clip(
                name="clip1",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=100, rate=24),
                    duration=otio.opentime.RationalTime(
                        value=50, rate=24)
                )
            ),
            otio.schema.Clip(
                name="clip2",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=101, rate=24),
                    duration=otio.opentime.RationalTime(
                        value=50, rate=24)
                )
            ),
            otio.schema.Clip(
                name="clip3",
                source_range=otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(
                        value=102, rate=24),
                    duration=otio.opentime.RationalTime(
                        value=50, rate=24)
                )
            )
        ])

        # The Stack should be as long as the longest child
        self.assertEquals(
            st.duration(),
            otio.opentime.RationalTime(value=50, rate=24)
        )

        # Stacked items should all start at time zero
        self.assertEquals(
            st.range_of_child_at_index(0).start_time,
            otio.opentime.RationalTime()
        )
        self.assertEquals(
            st.range_of_child_at_index(1).start_time,
            otio.opentime.RationalTime()
        )
        self.assertEquals(
            st.range_of_child_at_index(2).start_time,
            otio.opentime.RationalTime()
        )

        self.assertEquals(
            st.range_of_child_at_index(0).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEquals(
            st.range_of_child_at_index(1).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEquals(
            st.range_of_child_at_index(2).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )


class SequenceTest(unittest.TestCase):

    def test_serialize(self):
        sq = otio.schema.Sequence(name="foo", children=[])

        encoded = otio.adapters.otio_json.write_to_string(sq)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEquals(sq, decoded)

    def test_str(self):
        sq = otio.schema.Sequence(name="foo", children=[])
        self.assertMultiLineEqual(
            str(sq),
            "Sequence(" +
            str(sq.name) + ", " +
            str(sq._children) + ", " +
            str(sq.source_range) + ", " +
            str(sq.metadata) +
            ")"
        )

    def test_repr(self):
        sq = otio.schema.Sequence(name="foo", children=[])
        self.assertMultiLineEqual(
            repr(sq),
            "otio.schema.Sequence(" +
            "name=" + repr(sq.name) + ", " +
            "children=" + repr(sq._children) + ", " +
            "source_range=" + repr(sq.source_range) + ", " +
            "metadata=" + repr(sq.metadata) +
            ")"
        )

    def test_range(self):
        length = otio.opentime.RationalTime(5, 1)
        tr = otio.opentime.TimeRange(otio.opentime.RationalTime(), length)
        it = otio.core.Item(source_range=tr)
        sq = otio.schema.Sequence(children=[it])
        self.assertEquals(sq.range_of_child_at_index(0), tr)

        sq = otio.schema.Sequence(children=[it, it, it])
        self.assertEquals(len(sq), 1)

        sq = otio.schema.Sequence(
            children=[it, it.copy(), it.copy(), it.copy()],
        )
        self.assertEquals(
            sq.range_of_child_at_index(index=1),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(5, 1),
                otio.opentime.RationalTime(5, 1)
            )
        )
        self.assertEquals(
            sq.range_of_child_at_index(index=0),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 1),
                otio.opentime.RationalTime(5, 1)
            )
        )
        self.assertEquals(
            sq.range_of_child_at_index(index=-1),
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(15, 1),
                otio.opentime.RationalTime(5, 1)
            )
        )
        self.assertRaises(
            otio.exceptions.NoSuchChildAtIndex,
            lambda: sq.range_of_child_at_index(index=11)
        )
        self.assertEquals(sq.duration(), length + length + length + length)

    def test_range_of_child(self):
        sq = otio.schema.Sequence(
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

        # The Sequence should be as long as the children summed up
        self.assertEquals(
            sq.duration(),
            otio.opentime.RationalTime(value=150, rate=24)
        )

        # @TODO: should include time transforms

        # Sequenced items should all land end-to-end
        self.assertEquals(
            sq.range_of_child_at_index(0).start_time,
            otio.opentime.RationalTime()
        )
        self.assertEquals(
            sq.range_of_child_at_index(1).start_time,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEquals(
            sq.range_of_child_at_index(2).start_time,
            otio.opentime.RationalTime(value=100, rate=24)
        )
        self.assertEquals(
            sq.range_of_child(sq[2]),
            sq.range_of_child_at_index(2)
        )

        self.assertEquals(
            sq.range_of_child_at_index(0).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEquals(
            sq.range_of_child_at_index(1).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )
        self.assertEquals(
            sq.range_of_child_at_index(2).duration,
            otio.opentime.RationalTime(value=50, rate=24)
        )

    def test_range_nested(self):
        sq = otio.schema.Sequence(
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

        #  Subtle point, but copy() of a list returns an empty list with a copy
        #  of all of its metadata, but not of its data.  To get that you need
        #  to deepcopy().
        self.assertEquals(len(sq.copy()), 0)

        sq_c = sq.deepcopy()
        other_sq = otio.schema.Sequence(name="outer", children=[sq_c])

        # import ipdb; ipdb.set_trace()
        self.assertRaises(
            otio.exceptions.NotAChildError,
            lambda: other_sq.range_of_child(sq[1])
        )

        other_sq = otio.schema.Sequence(
            name="outer",
            children=[sq.deepcopy(), sq]
        )

        result_range_pre = other_sq.range_of_child_at_index(0)
        result_range_post = sq.range_of_child_at_index(1)

        result = otio.opentime.TimeRange(
            (
                result_range_pre.start_time +
                result_range_pre.duration +
                result_range_post.start_time
            ),
            result_range_post.duration
        )
        self.assertEquals(other_sq.range_of_child(sq[1]), result)


if __name__ == '__main__':
    unittest.main()
