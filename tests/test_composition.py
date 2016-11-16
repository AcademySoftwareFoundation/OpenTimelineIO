#!/usr/bin/env python

import unittest

import opentimelineio as otio


class CompositionTests(unittest.TestCase):

    def test_cons(self):
        it = otio.core.Item()
        co = otio.core.Composition(name="test", children=[it])
        self.assertEqual(co.name, "test")
        self.assertEqual(co._children, [it])
        self.assertEqual(co.composition_kind, "Composition")

    def test_iterable(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertEqual(co[0], it)
        self.assertEqual([i for i in co], [it])
        self.assertEqual(len(co), 1)

    def test_parent_manip(self):
        it = otio.core.Item()
        co = otio.core.Composition(children=[it])
        self.assertEqual(it._parent, co)


class StackTest(unittest.TestCase):

    def test_cons(self):
        st = otio.schema.Stack(name="test")
        self.assertEqual(st.name, "test")

    def test_serialize(self):
        st = otio.schema.Stack(name="test", children=[])

        encoded = otio.adapters.otio_json.write_to_string(st)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(st, decoded)

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


class SequenceTest(unittest.TestCase):

    def test_serialize(self):
        sq = otio.schema.Sequence(name="foo", children=[])

        encoded = otio.adapters.otio_json.write_to_string(sq)
        decoded = otio.adapters.otio_json.read_from_string(encoded)
        self.assertEqual(sq, decoded)

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
        self.assertEqual(sq.range_of_child_at_index(0), tr)

        sq = otio.schema.Sequence(children=[it, it, it])
        self.assertEqual(len(sq), 1)

        sq = otio.schema.Sequence(
            children=[it, it.copy(), it.copy(), it.copy()],
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
        self.assertEqual(len(sq.copy()), 0)

        sq_c = sq.deepcopy()
        other_sq = otio.schema.Sequence(name="outer", children=[sq_c])

        # import ipdb; ipdb.set_trace()
        with self.assertRaises(otio.exceptions.NotAChildError):
            other_sq.range_of_child(sq[1])

        other_sq = otio.schema.Sequence(
            name="outer",
            children=[sq.deepcopy(), sq]
        )

        result_range_pre = sq.range_of_child_at_index(0)
        result_range_post = sq.range_of_child_at_index(1)

        result = otio.opentime.TimeRange(
            (
                result_range_pre.start_time +
                result_range_pre.duration
            ),
            result_range_post.duration
        )
        self.assertEqual(other_sq.range_of_child(sq[1]), result)

    def test_setitem(self):
        seq = otio.schema.Sequence()
        it = otio.schema.Clip()
        it_2 = otio.schema.Clip()

        seq.append(it)
        self.assertEqual(len(seq), 1)

        seq[0] = it_2
        self.assertEqual(len(seq), 1)

    def test_transformed_time(self):
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
        fl = otio.schema.Filler(
            name="FILLER",
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
        st = otio.schema.Stack(name="foo_stack", children=[fl, sq])

        clip1 = sq[0]
        clip2 = sq[1]
        clip3 = sq[2]
        self.assertEqual(clip1.name, "clip1")
        self.assertEqual(clip2.name, "clip2")
        self.assertEqual(clip3.name, "clip3")

        self.assertEqual(st.top_clip_at_time(
            otio.opentime.RationalTime(-1, 24)), None)
        self.assertEqual(
            st.top_clip_at_time(otio.opentime.RationalTime(0, 24)),
            clip1
        )

        self.assertEqual(sq.top_clip_at_time(
            otio.opentime.RationalTime(-1, 24)),
            None
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(0, 24)),
            clip1
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(49, 24)),
            clip1
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(50, 24)),
            clip2
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(99, 24)),
            clip2
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(100, 24)),
            clip3
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(149, 24)),
            clip3
        )
        self.assertEqual(
            sq.top_clip_at_time(otio.opentime.RationalTime(150, 24)),
            None
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


class EdgeCases(unittest.TestCase):

    def test_empty_compositions(self):
        timeline = otio.schema.Timeline()
        self.assertEqual(len(timeline.tracks), 0)
        self.assertEqual(
            timeline.tracks.duration(),
            otio.opentime.RationalTime(
                0,
                24))


def _nest(item):
    parent = item.parent()
    index = parent.index(item)
    wrapper = otio.schema.Stack()
    # swap out the item for the wrapper
    parent[index] = wrapper
    # now put the item inside the wrapper
    wrapper.append(item)
    return wrapper


class NestingTest(unittest.TestCase):

    def test_deeply_nested(self):
        # Take a single clip of media (frames 100-200) and nest it into a bunch
        # of layers
        # Nesting it should not shift the media at all.
        # At one level:
        # Timeline:
        #  Stack: [0-99]
        #   Sequence: [0-99]
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
        track = otio.schema.Sequence()
        clip = otio.schema.Clip()
        media = otio.media_reference.MissingReference()
        media.available_range = media_range
        clip.media_reference = media
        track.append(clip)
        stack.append(track)

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

        # now nest it many layers deeper
        wrappers = []
        num_wrappers = 10
        for i in range(num_wrappers):
            # print "Nesting", (i+1), "levels deep"
            wrapper = _nest(clip)
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

    def test_trimming(self):
        sq = otio.schema.Sequence(
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
                otio.schema.Sequence(
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
            playhead = otio.opentime.RationalTime(frame, 24)
            item = sq.top_clip_at_time(playhead)
            mediaframe = sq.transformed_time(playhead, item)
            self.assertEqual(
                (
                    item.name,
                    otio.opentime.to_frames(mediaframe, 24)
                ),
                expected_val
            )

if __name__ == '__main__':
    unittest.main()
