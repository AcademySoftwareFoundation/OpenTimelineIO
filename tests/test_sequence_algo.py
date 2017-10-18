#
# Copyright 2017 Pixar Animation Studios
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

"""Test file for the track algorithms library."""

import unittest
import copy

import opentimelineio as otio

# for debugging
# def print_expanded_tree(seq):
#     for thing in seq:
#         if isinstance(thing, tuple):
#             for i in thing:
#                 print "  ", i
#         else:
#             print thing


class TransitionExpansionTests(unittest.TestCase):
    """ test harness for transition expansion function """

    def test_expand_surrounded_by_clips(self):
        name = "test"
        rt = otio.opentime.RationalTime(5, 24)
        rt_2 = otio.opentime.RationalTime(1, 24)
        tr = otio.opentime.TimeRange(rt, rt + rt)
        avail_tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 24),
            otio.opentime.RationalTime(50, 24)
        )
        mr = otio.media_reference.External(
            available_range=avail_tr,
            target_url="/var/tmp/test.mov"
        )

        cl = otio.schema.Clip(
            name=name + "_pre",
            media_reference=mr,
            source_range=tr,
        )

        seq = otio.schema.Track()
        seq.append(cl)
        in_offset = rt
        out_offset = rt_2
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=in_offset,
            out_offset=out_offset,
            metadata={
                "foo": "bar"
            }
        )
        seq.append(trx)
        cl_2 = copy.deepcopy(cl)
        cl_2.name = name + "_post"
        seq.append(copy.copy(cl))

        pre_duration = copy.deepcopy(seq[0].source_range.duration)

        # print
        # print "BEFORE:"
        # print_expanded_tree(seq)
        seq2 = otio.algorithms.track_with_expanded_transitions(seq)
        # print
        # print "AFTER:"
        # print_expanded_tree(seq2)

        self.assertNotEqual(pre_duration, seq2[0].source_range.duration)

        # check ranges on results

        # first clip is trimmed
        self.assertEqual(
            seq2[0].source_range.duration,
            cl_2.source_range.duration - in_offset
        )

        self.assertEqual(
            seq2[1][0].source_range.start_time,
            cl.source_range.end_time_exclusive() - in_offset
        )
        self.assertEqual(
            seq2[1][0].source_range.duration,
            in_offset + out_offset
        )
        self.assertEqual(
            seq2[1][2].source_range.start_time,
            cl_2.source_range.start_time - in_offset
        )
        self.assertEqual(
            seq2[1][2].source_range.duration,
            in_offset + out_offset
        )

        # final clip is trimmed
        self.assertEqual(
            seq2[2].source_range.duration,
            cl_2.source_range.duration - out_offset
        )

        # make sure that both transition clips are the same length
        self.assertEqual(
            seq2[1][0].source_range.duration,
            seq2[1][2].source_range.duration
        )

        # big hammer stuff
        self.assertNotEqual(seq, seq2)
        self.assertNotEqual(seq[0], seq2[0])
        self.assertNotEqual(seq[-1], seq2[-1])
        self.assertNotEqual(seq[-1].source_range, seq2[-1].source_range)

    # leaving this here as a @TODO
    def DISABLED_test_expand_track(self):
        name = "test"
        rt = otio.opentime.RationalTime(5, 24)
        rt_2 = otio.opentime.RationalTime(1, 24)
        tr = otio.opentime.TimeRange(rt, rt + rt)
        avail_tr = otio.opentime.TimeRange(
            otio.opentime.RationalTime(0, 24),
            otio.opentime.RationalTime(50, 24)
        )
        mr = otio.media_reference.External(
            available_range=avail_tr,
            target_url="/var/tmp/test.mov"
        )

        cl = otio.schema.Clip(
            name=name + "_pre",
            media_reference=mr,
            source_range=tr,
        )

        seq = otio.schema.Track()
        seq.name = name
        seq.append(cl)
        in_offset = rt
        out_offset = rt_2
        trx = otio.schema.Transition(
            name="AtoB",
            transition_type=otio.schema.TransitionTypes.SMPTE_Dissolve,
            in_offset=in_offset,
            out_offset=out_offset,
            metadata={
                "foo": "bar"
            }
        )
        seq.append(trx)
        seq_2 = copy.deepcopy(seq)
        seq_2.name = name + "_post"
        seq.append(seq_2)

        pre_duration = copy.deepcopy(seq[0].source_range.duration)

        # print
        # print "BEFORE:"
        # print_expanded_tree(seq)
        expanded_seq = otio.algorithms.track_with_expanded_transitions(seq)
        # print
        # print "AFTER:"
        # print_expanded_tree(expanded_seq)

        self.assertNotEqual(
            pre_duration,
            expanded_seq[0].source_range.duration
        )

        # check ranges on results

        # first clip is trimmed
        self.assertEqual(
            expanded_seq[0].source_range.duration,
            seq_2.source_range.duration - in_offset
        )

        self.assertEqual(
            expanded_seq[1][0].source_range.start_time,
            cl.source_range.end_time_exclusive() - in_offset
        )
        self.assertEqual(
            expanded_seq[1][0].source_range.duration,
            in_offset + out_offset
        )
        self.assertEqual(
            expanded_seq[1][2].source_range.start_time,
            seq_2.source_range.start_time - in_offset
        )
        self.assertEqual(
            expanded_seq[1][2].source_range.duration,
            in_offset + out_offset
        )

        # final clip is trimmed
        self.assertEqual(
            expanded_seq[2].source_range.duration,
            seq_2.source_range.duration - out_offset
        )

        # make sure that both transition clips are the same length
        self.assertEqual(
            expanded_seq[1][0].source_range.duration,
            expanded_seq[1][2].source_range.duration
        )

        # big hammer stuff
        self.assertNotEqual(seq, expanded_seq)
        self.assertNotEqual(seq[0], expanded_seq[0])
        self.assertNotEqual(seq[-1], expanded_seq[-1])
        self.assertNotEqual(
            seq[-1].source_range,
            expanded_seq[-1].source_range
        )
