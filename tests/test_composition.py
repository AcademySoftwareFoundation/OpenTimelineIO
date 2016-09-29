#!/usr/bin/env python

import unittest

import opentimelineio as otio


class CompositionTests(unittest.TestCase):

    def test_cons(self):
        bo = otio.core.Item()
        co = otio.core.Composition(name="test", children=[bo])
        self.assertEquals(co.name, "test")
        self.assertEquals(co.children, [bo])
        self.assertEquals(co.composition_kind, "Composition")

    def test_iterable(self):
        bo = otio.core.Item()
        co = otio.core.Composition(children=[bo])
        self.assertEquals(co[0], bo)
        self.assertEquals([i for i in co], [bo])
        self.assertEquals(len(co), 1)


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
            str(st.children) + ", " +
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
            "children=" + repr(st.children) + ", " +
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
            st.duration(), otio.opentime.RationalTime(value=50, rate=24))

        # Stacked items should all start at time zero
        self.assertEquals(st.range_of_child_at_index(
            0).start_time, otio.opentime.RationalTime())
        self.assertEquals(st.range_of_child_at_index(
            1).start_time, otio.opentime.RationalTime())
        self.assertEquals(st.range_of_child_at_index(
            2).start_time, otio.opentime.RationalTime())

        self.assertEquals(st.range_of_child_at_index(
            0).duration, otio.opentime.RationalTime(value=50, rate=24))
        self.assertEquals(st.range_of_child_at_index(
            1).duration, otio.opentime.RationalTime(value=50, rate=24))
        self.assertEquals(st.range_of_child_at_index(
            2).duration, otio.opentime.RationalTime(value=50, rate=24))


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
            str(sq.children) + ", " +
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
            "children=" + repr(sq.children) + ", " +
            "source_range=" + repr(sq.source_range) + ", " +
            "metadata=" + repr(sq.metadata) +
            ")"
        )

    def test_range(self):
        length = otio.opentime.RationalTime(5, 1)
        tr = otio.opentime.TimeRange(otio.opentime.RationalTime(), length)
        bo = otio.core.Item(source_range=tr)
        sq = otio.schema.Sequence(children=[bo, bo, bo, bo])
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

        sq = otio.schema.Sequence(name="foo", children=[
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

        # The Sequence should be as long as the children summed up
        self.assertEquals(
            sq.duration(), otio.opentime.RationalTime(value=150, rate=24))

        # Sequenced items should all land end-to-end
        self.assertEquals(sq.range_of_child_at_index(
            0).start_time, otio.opentime.RationalTime())
        self.assertEquals(sq.range_of_child_at_index(
            1).start_time, otio.opentime.RationalTime(value=50, rate=24))
        self.assertEquals(sq.range_of_child_at_index(
            2).start_time, otio.opentime.RationalTime(value=100, rate=24))

        self.assertEquals(sq.range_of_child_at_index(
            0).duration, otio.opentime.RationalTime(value=50, rate=24))
        self.assertEquals(sq.range_of_child_at_index(
            1).duration, otio.opentime.RationalTime(value=50, rate=24))
        self.assertEquals(sq.range_of_child_at_index(
            2).duration, otio.opentime.RationalTime(value=50, rate=24))

if __name__ == '__main__':
    unittest.main()
