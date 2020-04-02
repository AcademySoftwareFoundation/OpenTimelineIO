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

"""Test file for the track algorithms library."""

import unittest
import copy

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils

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
        mr = otio.schema.ExternalReference(
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
        seq.append(copy.deepcopy(cl))

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
        mr = otio.schema.ExternalReference(
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


class TrackTrimmingTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    """ test harness for track trimming function """

    def make_sample_track(self):
        return otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "A",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 50
                        },
                        "start_time": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 0.0
                        }
                    }
                },
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "B",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 50
                        },
                        "start_time": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 0.0
                        }
                    }
                },
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "C",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 50
                        },
                        "start_time": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 0.0
                        }
                    }
                }
            ],
            "effects": [],
            "kind": "Video",
            "markers": [],
            "metadata": {},
            "name": "Sequence1",
            "source_range": null
        }
        """, "otio_json")

    def test_trim_to_existing_range(self):
        original_track = self.make_sample_track()
        self.assertEqual(
            original_track.trimmed_range(),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(150, 24)
            )
        )

        # trim to the exact range it already has
        trimmed = otio.algorithms.track_trimmed_to_range(
            original_track,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(150, 24)
            )
        )
        # it shouldn't have changed at all
        self.assertIsOTIOEquivalentTo(original_track, trimmed)

    def test_trim_to_longer_range(self):
        original_track = self.make_sample_track()
        # trim to a larger range
        trimmed = otio.algorithms.track_trimmed_to_range(
            original_track,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(-10, 24),
                duration=otio.opentime.RationalTime(160, 24)
            )
        )
        # it shouldn't have changed at all
        self.assertJsonEqual(original_track, trimmed)

    def test_trim_front(self):
        original_track = self.make_sample_track()
        # trim off the front (clip A and part of B)
        trimmed = otio.algorithms.track_trimmed_to_range(
            original_track,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(60, 24),
                duration=otio.opentime.RationalTime(90, 24)
            )
        )
        self.assertNotEqual(original_track, trimmed)
        self.assertEqual(len(trimmed), 2)
        self.assertEqual(
            trimmed.trimmed_range(),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(90, 24)
            )
        )
        # did clip B get trimmed?
        self.assertEqual(trimmed[0].name, "B")
        self.assertEqual(
            trimmed[0].trimmed_range(),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(10, 24),
                duration=otio.opentime.RationalTime(40, 24)
            )
        )
        # clip C should have been left alone
        self.assertIsOTIOEquivalentTo(trimmed[1], original_track[2])

    def test_trim_end(self):
        original_track = self.make_sample_track()
        # trim off the end (clip C and part of B)
        trimmed = otio.algorithms.track_trimmed_to_range(
            original_track,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(90, 24)
            )
        )
        self.assertNotEqual(original_track, trimmed)
        self.assertEqual(len(trimmed), 2)
        self.assertEqual(
            trimmed.trimmed_range(),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(90, 24)
            )
        )
        # clip A should have been left alone
        self.assertIsOTIOEquivalentTo(trimmed[0], original_track[0])
        # did clip B get trimmed?
        self.assertEqual(trimmed[1].name, "B")
        self.assertEqual(
            trimmed[1].trimmed_range(),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(40, 24)
            )
        )

    def test_trim_with_transitions(self):
        original_track = self.make_sample_track()
        self.assertEqual(
            otio.opentime.RationalTime(150, 24),
            original_track.duration()
        )
        self.assertEqual(len(original_track), 3)

        # add a transition
        tr = otio.schema.Transition(
            in_offset=otio.opentime.RationalTime(12, 24),
            out_offset=otio.opentime.RationalTime(20, 24)
        )
        original_track.insert(1, tr)
        self.assertEqual(len(original_track), 4)
        self.assertEqual(
            otio.opentime.RationalTime(150, 24),
            original_track.duration()
        )

        # if you try to sever a Transition in the middle it should fail
        with self.assertRaises(otio.exceptions.CannotTrimTransitionsError):
            trimmed = otio.algorithms.track_trimmed_to_range(
                original_track,
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(5, 24),
                    duration=otio.opentime.RationalTime(50, 24)
                )
            )

        with self.assertRaises(otio.exceptions.CannotTrimTransitionsError):
            trimmed = otio.algorithms.track_trimmed_to_range(
                original_track,
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(45, 24),
                    duration=otio.opentime.RationalTime(50, 24)
                )
            )

        trimmed = otio.algorithms.track_trimmed_to_range(
            original_track,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(25, 24),
                duration=otio.opentime.RationalTime(50, 24)
            )
        )
        self.assertNotEqual(original_track, trimmed)

        expected = otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "A",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 25
                        },
                        "start_time": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 25.0
                        }
                    }
                },
                {
                    "OTIO_SCHEMA": "Transition.1",
                    "name": "",
                    "metadata": {},
                    "transition_type": "",
                    "in_offset": {
                        "OTIO_SCHEMA": "RationalTime.1",
                        "rate": 24,
                        "value": 12
                    },
                    "out_offset": {
                        "OTIO_SCHEMA": "RationalTime.1",
                        "rate": 24,
                        "value": 20
                    }
                },
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "B",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 25
                        },
                        "start_time": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 0.0
                        }
                    }
                }
            ],
            "effects": [],
            "kind": "Video",
            "markers": [],
            "metadata": {},
            "name": "Sequence1",
            "source_range": null
        }
        """, "otio_json")

        self.assertJsonEqual(expected, trimmed)


if __name__ == '__main__':
    unittest.main()
