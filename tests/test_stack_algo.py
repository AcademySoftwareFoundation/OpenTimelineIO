#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test file for the stack algorithms library."""

import unittest
import os
import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
MULTITRACK_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "multitrack.otio")
PREFLATTENED_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "preflattened.otio")


class StackAlgoTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    """ test harness for stack algo functions """

    def setUp(self):
        self.trackZ = otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "Z",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 150
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

        self.trackZd = otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "enabled": false,
                    "metadata": {},
                    "name": "Z",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 150
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

        self.track_d = otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "enabled": true,
                    "metadata": {},
                    "name": "Z",
                    "source_range": {
                        "OTIO_SCHEMA": "TimeRange.1",
                        "duration": {
                            "OTIO_SCHEMA": "RationalTime.1",
                            "rate": 24,
                            "value": 150
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
            "enabled": false,
            "metadata": {},
            "name": "Sequence1",
            "source_range": null
        }
        """, "otio_json")

        self.trackABC = otio.adapters.read_from_string("""
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

        self.trackDgE = otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Clip.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "D",
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
                    "OTIO_SCHEMA": "Gap.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "g",
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
                    "name": "E",
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

        self.trackgFg = otio.adapters.read_from_string("""
        {
            "OTIO_SCHEMA": "Track.1",
            "children": [
                {
                    "OTIO_SCHEMA": "Gap.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "g1",
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
                    "name": "F",
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
                    "OTIO_SCHEMA": "Gap.1",
                    "effects": [],
                    "markers": [],
                    "media_reference": null,
                    "metadata": {},
                    "name": "g2",
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

    def test_flatten_single_track(self):
        stack = otio.schema.Stack(children=[
            self.trackABC
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        # the result should be equivalent
        self.assertJsonEqual(
            flat_track[:],
            self.trackABC[:]
        )
        # but not the same actual objects
        self.assertIsNot(
            flat_track[0],
            self.trackABC[0]
        )
        self.assertIsNot(
            flat_track[1],
            self.trackABC[1]
        )
        self.assertIsNot(
            flat_track[2],
            self.trackABC[2]
        )

    def test_flatten_obscured_track(self):
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackZ
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertJsonEqual(
            flat_track[:],
            self.trackZ[:]
        )

        # It is an error to add an item to composition if it is already in
        # another composition.  This clears out the old test composition
        # (and also clears out its parent pointers).
        del stack
        stack = otio.schema.Stack(
            children=[
                self.trackZ,
                self.trackABC,
            ]
        )
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertJsonEqual(
            flat_track[:],
            self.trackABC[:]
        )

    def test_flatten_disabled_clip(self):
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackZ
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertJsonEqual(
            flat_track[:],
            self.trackZ[:]
        )
        del stack
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackZd
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertJsonEqual(
            flat_track[:],
            self.trackABC[:]
        )

    def test_flatten_disabled_track(self):
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackZ
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertJsonEqual(
            flat_track[:],
            self.trackZ[:]
        )
        del stack
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.track_d
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertJsonEqual(
            flat_track[:],
            self.trackABC[:]
        )

    def test_flatten_gaps(self):
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackDgE
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertIsOTIOEquivalentTo(flat_track[0], self.trackDgE[0])
        self.assertIsOTIOEquivalentTo(flat_track[1], self.trackABC[1])
        self.assertIsOTIOEquivalentTo(flat_track[2], self.trackDgE[2])
        self.assertIsNot(flat_track[0], self.trackDgE[0])
        self.assertIsNot(flat_track[1], self.trackABC[1])
        self.assertIsNot(flat_track[2], self.trackDgE[2])

        # create a new stack out of the old parts, delete the old stack first
        del stack
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackgFg
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertIsOTIOEquivalentTo(flat_track[0], self.trackABC[0])
        self.assertIsOTIOEquivalentTo(flat_track[1], self.trackgFg[1])
        self.assertIsOTIOEquivalentTo(flat_track[2], self.trackABC[2])
        self.assertIsNot(flat_track[0], self.trackABC[0])
        self.assertIsNot(flat_track[1], self.trackgFg[1])
        self.assertIsNot(flat_track[2], self.trackABC[2])

    def test_flatten_gaps_with_trims(self):
        stack = otio.schema.Stack(children=[
            self.trackZ,
            self.trackDgE
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertIsOTIOEquivalentTo(flat_track[0], self.trackDgE[0])
        self.assertEqual(flat_track[1].name, "Z")
        self.assertEqual(
            flat_track[1].source_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(50, 24),
                otio.opentime.RationalTime(50, 24)
            )
        )
        self.assertIsOTIOEquivalentTo(flat_track[2], self.trackDgE[2])

        del stack
        stack = otio.schema.Stack(children=[
            self.trackZ,
            self.trackgFg
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertEqual(flat_track[0].name, "Z")
        self.assertEqual(
            flat_track[0].source_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(0, 24),
                otio.opentime.RationalTime(50, 24)
            )
        )
        self.assertIsOTIOEquivalentTo(flat_track[1], self.trackgFg[1])
        self.assertEqual(flat_track[2].name, "Z")
        self.assertEqual(
            flat_track[2].source_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(100, 24),
                otio.opentime.RationalTime(50, 24)
            )
        )

    def test_flatten_list_of_tracks(self):
        tracks = [
            self.trackABC,
            self.trackDgE
        ]
        flat_track = otio.algorithms.flatten_stack(tracks)
        self.assertIsOTIOEquivalentTo(flat_track[0], self.trackDgE[0])
        self.assertIsOTIOEquivalentTo(flat_track[1], self.trackABC[1])
        self.assertIsOTIOEquivalentTo(flat_track[2], self.trackDgE[2])

        tracks = [
            self.trackABC,
            self.trackgFg
        ]
        flat_track = otio.algorithms.flatten_stack(tracks)
        self.assertIsOTIOEquivalentTo(flat_track[0], self.trackABC[0])
        self.assertIsOTIOEquivalentTo(flat_track[1], self.trackgFg[1])
        self.assertIsOTIOEquivalentTo(flat_track[2], self.trackABC[2])

    def test_flatten_example_code(self):
        timeline = otio.adapters.read_from_file(MULTITRACK_EXAMPLE_PATH)
        preflattened = otio.adapters.read_from_file(PREFLATTENED_EXAMPLE_PATH)
        preflattened_track = preflattened.video_tracks()[0]
        flattened_track = otio.algorithms.flatten_stack(
            timeline.video_tracks()
        )

        # the names will be different, so clear them both
        preflattened_track.name = ""
        flattened_track.name = ""

        self.assertOTIOEqual(
            preflattened_track,
            flattened_track
        )

    def assertOTIOEqual(self, a, b):
        self.maxDiff = None
        self.assertMultiLineEqual(
            otio.adapters.write_to_string(a, 'otio_json'),
            otio.adapters.write_to_string(b, 'otio_json')
        )

    def test_flatten_with_transition(self):
        stack = otio.schema.Stack(
            children=[
                self.trackABC,
                self.trackDgE,
            ]
        )
        stack[1].insert(
            1,
            otio.schema.Transition(
                name="test_transition",
                in_offset=otio.opentime.RationalTime(10, 24),
                out_offset=otio.opentime.RationalTime(15, 24)
            )
        )
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertEqual(3, len(self.trackABC))
        self.assertEqual(4, len(stack[1]))
        self.assertEqual(4, len(flat_track))
        self.assertEqual(flat_track[1].name, "test_transition")

    def test_top_child_at_time(self):
        stack = otio.schema.Stack(
            children=[
                self.trackABC,
                self.trackDgE,
            ]
        )

        top_child = otio.algorithms.top_clip_at_time(
            stack,
            otio.opentime.RationalTime(0, 24)
        )
        self.assertEqual(top_child, self.trackDgE[0])

        stack.append(
            otio.schema.Track(
                children=[
                    otio.schema.Gap(
                        source_range=otio.opentime.TimeRange(
                            otio.opentime.RationalTime(0, 24),
                            otio.opentime.RationalTime(10, 24)
                        )
                    )
                ]
            )
        )

        top_child = otio.algorithms.top_clip_at_time(
            stack,
            otio.opentime.RationalTime(0, 24)
        )
        self.assertEqual(top_child, self.trackDgE[0])


if __name__ == '__main__':
    unittest.main()
