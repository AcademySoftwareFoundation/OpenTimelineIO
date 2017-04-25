#!/usr/bin/env python

"""
Test file for the sequence algorithms library.
"""

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

        seq = otio.schema.Sequence()
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
        seq2 = otio.algorithms.sequence_with_expanded_transitions(seq)
        # print
        # print "AFTER:"
        # print_expanded_tree(seq2)

        self.assertNotEquals(pre_duration, seq2[0].source_range.duration)

        # check ranges on results

        # first clip is trimmed
        self.assertEquals(
            seq2[0].source_range.duration,
            cl_2.source_range.duration - in_offset
        )

        self.assertEquals(
            seq2[1][0].source_range.start_time,
            cl.source_range.end_time_exclusive() - in_offset
        )
        self.assertEquals(
            seq2[1][0].source_range.duration,
            in_offset + out_offset
        )
        self.assertEquals(
            seq2[1][2].source_range.start_time,
            cl_2.source_range.start_time - in_offset
        )
        self.assertEquals(
            seq2[1][2].source_range.duration,
            in_offset + out_offset
        )

        # final clip is trimmed
        self.assertEquals(
            seq2[2].source_range.duration,
            cl_2.source_range.duration - out_offset
        )

        # make sure that both transition clips are the same length
        self.assertEquals(
            seq2[1][0].source_range.duration,
            seq2[1][2].source_range.duration
        )

        # big hammer stuff
        self.assertNotEquals(seq, seq2)
        self.assertNotEquals(seq[0], seq2[0])
        self.assertNotEquals(seq[-1], seq2[-1])
        self.assertNotEquals(seq[-1].source_range, seq2[-1].source_range)

    # leaving this here as a @TODO
    def DISABLED_test_expand_sequence(self):
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

        seq = otio.schema.Sequence()
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
        expanded_seq = otio.algorithms.sequence_with_expanded_transitions(seq)
        # print
        # print "AFTER:"
        # print_expanded_tree(expanded_seq)

        self.assertNotEquals(
            pre_duration,
            expanded_seq[0].source_range.duration
        )

        # check ranges on results

        # first clip is trimmed
        self.assertEquals(
            expanded_seq[0].source_range.duration,
            seq_2.source_range.duration - in_offset
        )

        self.assertEquals(
            expanded_seq[1][0].source_range.start_time,
            cl.source_range.end_time_exclusive() - in_offset
        )
        self.assertEquals(
            expanded_seq[1][0].source_range.duration,
            in_offset + out_offset
        )
        self.assertEquals(
            expanded_seq[1][2].source_range.start_time,
            seq_2.source_range.start_time - in_offset
        )
        self.assertEquals(
            expanded_seq[1][2].source_range.duration,
            in_offset + out_offset
        )

        # final clip is trimmed
        self.assertEquals(
            expanded_seq[2].source_range.duration,
            seq_2.source_range.duration - out_offset
        )

        # make sure that both transition clips are the same length
        self.assertEquals(
            expanded_seq[1][0].source_range.duration,
            expanded_seq[1][2].source_range.duration
        )

        # big hammer stuff
        self.assertNotEquals(seq, expanded_seq)
        self.assertNotEquals(seq[0], expanded_seq[0])
        self.assertNotEquals(seq[-1], expanded_seq[-1])
        self.assertNotEquals(
            seq[-1].source_range,
            expanded_seq[-1].source_range
        )
