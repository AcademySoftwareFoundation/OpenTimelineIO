#!/usr/bin/env python
#
# Copyright Contributors to the OpenTimelineIO project
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Test harness for the filter algorithms."""

import unittest
import copy

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class FilterTest(unittest.TestCase, otio_test_utils.OTIOAssertions):
    maxDiff = None

    def test_copy_track(self):
        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        test = otio.algorithms.filtered_composition(tr, lambda _: _)

        self.assertJsonEqual(tr, test)

    def test_copy_stack(self):
        """Test a no op filter that copies the timeline."""

        md = {'test': 'bar'}
        tr = otio.schema.Stack(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        result = otio.algorithms.filtered_composition(tr, lambda _: _)

        self.assertJsonEqual(tr, result)
        self.assertIsNot(tr[0], result)

    def test_prune_clips_starting_with_a(self):
        """test a filter that removes things whose name starts with 'a'"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))
        tr.append(otio.schema.Clip(name='a_cl3', metadata=md))
        tr_2 = otio.schema.Track(name='a', metadata=md)
        tr_2.append(otio.schema.Clip(name='cl1', metadata=md))
        tr_2.append(otio.schema.Clip(name='a_cl2', metadata=md))
        tr.append(tr_2)

        visited = []

        def nothing_that_starts_with_a(thing):
            visited.append(thing.name)
            if thing.name.startswith('a'):
                return None
            else:
                return thing

        result = otio.algorithms.filtered_composition(
            tr,
            nothing_that_starts_with_a
        )

        # make sure that the track being pruned means the child was never
        # visited
        self.assertNotIn('a_cl2', visited)

        # match the desired behavior of the function
        del tr[2]
        del tr[1]

        self.assertJsonEqual(tr, result)

    def test_prune_clips(self):
        """test a filter that removes clips"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        def no_clips(thing):
            if not isinstance(thing, otio.schema.Clip):
                return thing
            return None

        result = otio.algorithms.filtered_composition(tr, no_clips)
        self.assertEqual(0, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # emptying the track should have the same effect
        del tr[:]
        self.assertIsOTIOEquivalentTo(tr, result)

    def test_prune_by_type_args(self):
        """Test pruning using the types_to_prune list"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        result = otio.algorithms.filtered_composition(
            tr,
            lambda _: _,
            types_to_prune=(otio.schema.Clip,)
        )
        self.assertEqual(0, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # emptying the track should have the same effect
        del tr[:]
        self.assertIsOTIOEquivalentTo(tr, result)

    def test_copy(self):
        md = {'test': 'bar'}
        tl = otio.schema.Timeline(name='foo', metadata=md)
        tl.tracks.append(otio.schema.Track(name='track1', metadata=md))
        tl.tracks[0].append(otio.schema.Clip(name='cl1', metadata=md))

        test = otio.algorithms.filtered_composition(tl, lambda _: _)

        # make sure the original timeline didn't get nuked
        self.assertEqual(len(tl.tracks), 1)

        self.assertJsonEqual(tl, test)

    def test_insert_tuple(self):
        """test a reduce that takes each clip in a sequence and triples it"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        def triple_clips(thing):
            if not isinstance(thing, otio.schema.Clip):
                return thing
            return (thing, copy.deepcopy(thing), copy.deepcopy(thing))

        result = otio.algorithms.filtered_composition(tr, triple_clips)
        self.assertEqual(3, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # emptying the track should have the same effect
        tr.extend([copy.deepcopy(tr[0]), copy.deepcopy(tr[0])])
        self.assertJsonEqual(tr, result)


class ReduceTest(unittest.TestCase, otio_test_utils.OTIOAssertions):
    maxDiff = None

    def test_copy_track(self):
        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        self.assertJsonEqual(
            tr,
            otio.algorithms.filtered_with_sequence_context(
                tr,
                # no op - ignore all arguments and return original thing
                lambda _, thing, __: thing
            )
        )

    def test_copy_stack(self):
        """Test a no op reduce that copies the timeline."""

        md = {'test': 'bar'}
        tr = otio.schema.Stack(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        result = otio.algorithms.filtered_with_sequence_context(
            tr,
            # no op - ignore all arguments and return original thing
            lambda _, thing, __: thing
        )
        self.assertJsonEqual(tr, result)
        self.assertIsNot(tr[0], result)

    def test_prune_clips(self):
        """test a reduce that removes clips"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        def no_clips(_, thing, __):
            if not isinstance(thing, otio.schema.Clip):
                return thing
            return None

        result = otio.algorithms.filtered_with_sequence_context(tr, no_clips)
        self.assertEqual(0, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # emptying the track should have the same effect
        del tr[:]
        self.assertIsOTIOEquivalentTo(tr, result)

    def test_prune_clips_using_types_to_prune(self):
        """Test pruning otio.schema.clip using the types_to_prune argument"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        result = otio.algorithms.filtered_with_sequence_context(
            tr,
            # no op - ignore all arguments and return original thing
            lambda _, thing, __: thing,
            # instead use types_to_prune
            types_to_prune=(otio.schema.Clip,)
        )
        self.assertEqual(0, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # emptying the track should have the same effect
        del tr[:]
        self.assertIsOTIOEquivalentTo(tr, result)

    def test_insert_tuple(self):
        """test a reduce that takes each clip in a sequence and triples it"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        tr.append(otio.schema.Clip(name='cl1', metadata=md))

        def triple_clips(_, thing, __):
            if not isinstance(thing, otio.schema.Clip):
                return thing
            return (thing, copy.deepcopy(thing), copy.deepcopy(thing))

        result = otio.algorithms.filtered_with_sequence_context(
            tr,
            triple_clips
        )
        self.assertEqual(3, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # emptying the track should have the same effect
        tr.extend((copy.deepcopy(tr[0]), copy.deepcopy(tr[0])))
        self.assertJsonEqual(tr, result)

    def test_prune_clips_after_transitions(self):
        """test a reduce that removes clips that follow transitions"""

        md = {'test': 'bar'}
        tr = otio.schema.Track(name='foo', metadata=md)
        for i in range(5):
            ind = str(i)
            if i in (2, 3):
                tr.append(otio.schema.Transition(name='should_be_pruned' + ind))
            tr.append(otio.schema.Clip(name='cl' + ind, metadata=md))

        def no_clips_after_transitions(prev, thing, __):
            if (
                isinstance(prev, otio.schema.Transition) or
                isinstance(thing, otio.schema.Transition)
            ):
                return None
            return thing

        result = otio.algorithms.filtered_with_sequence_context(
            tr,
            no_clips_after_transitions
        )

        # emptying the track of transitions and the clips they follow and
        # should have the same effect
        del tr[2:6]
        self.assertJsonEqual(tr, result)

        self.assertEqual(3, len(result))
        self.assertEqual(tr.metadata, result.metadata)

        # ...but that things have been properly deep copied
        self.assertIsNot(tr.metadata, result.metadata)

    def test_copy(self):
        """Test that a simple reduce results in a copy"""
        md = {'test': 'bar'}
        tl = otio.schema.Timeline(name='foo', metadata=md)
        tl.tracks.append(otio.schema.Track(name='track1', metadata=md))
        tl.tracks[0].append(otio.schema.Clip(name='cl1', metadata=md))

        test = otio.algorithms.filtered_with_sequence_context(
            tl,
            # no op - ignore all arguments and return original thing
            lambda _, thing, __: thing
        )

        # make sure the original timeline didn't get nuked
        self.assertEqual(len(tl.tracks), 1)
        self.assertJsonEqual(tl, test)

    def test_prune_correct_duplicate(self):
        """test a reduce that removes the correct duplicate clip"""

        md = {'test': 'bar'}
        tr = otio.schema.Track()
        tr.append(otio.schema.Clip(metadata=md))
        tr.append(otio.schema.Gap())
        tr.append(otio.schema.Clip(metadata=md))
        tr.append(otio.schema.Gap())
        tr.append(otio.schema.Clip(metadata=md))

        clips = []

        def no_clip_2(_, thing, __):
            if isinstance(thing, otio.schema.Clip):
                clips.append(thing)
                if len(clips) == 2:
                    return None
            return thing

        result = otio.algorithms.filtered_with_sequence_context(tr, no_clip_2)
        self.assertEqual(4, len(result))
        self.assertTrue(isinstance(result[0], otio.schema.Clip))
        self.assertTrue(isinstance(result[1], otio.schema.Gap))
        self.assertTrue(isinstance(result[2], otio.schema.Gap))
        self.assertTrue(isinstance(result[3], otio.schema.Clip))


if __name__ == '__main__':
    unittest.main()
