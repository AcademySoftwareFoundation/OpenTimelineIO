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

"""Test file for the stack algorithms library."""

import unittest
import os
import opentimelineio as otio


SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
MULTITRACK_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "multitrack.otio")
PREFLATTENED_EXAMPLE_PATH = os.path.join(SAMPLE_DATA_DIR, "preflattened.otio")


class StackAlgoTests(unittest.TestCase):
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
        self.assertListEqual(
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
        self.assertEqual(
            flat_track[:],
            self.trackZ[:]
        )

        stack = otio.schema.Stack(children=[
            self.trackZ,
            self.trackABC
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertEqual(
            flat_track[:],
            self.trackABC[:]
        )

    def test_flatten_gaps(self):
        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackDgE
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertEqual(flat_track[0], self.trackDgE[0])
        self.assertEqual(flat_track[1], self.trackABC[1])
        self.assertEqual(flat_track[2], self.trackDgE[2])
        self.assertIsNot(flat_track[0], self.trackDgE[0])
        self.assertIsNot(flat_track[1], self.trackABC[1])
        self.assertIsNot(flat_track[2], self.trackDgE[2])

        stack = otio.schema.Stack(children=[
            self.trackABC,
            self.trackgFg
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertEqual(flat_track[0], self.trackABC[0])
        self.assertEqual(flat_track[1], self.trackgFg[1])
        self.assertEqual(flat_track[2], self.trackABC[2])
        self.assertIsNot(flat_track[0], self.trackABC[0])
        self.assertIsNot(flat_track[1], self.trackgFg[1])
        self.assertIsNot(flat_track[2], self.trackABC[2])

    def test_flatten_gaps_with_trims(self):
        stack = otio.schema.Stack(children=[
            self.trackZ,
            self.trackDgE
        ])
        flat_track = otio.algorithms.flatten_stack(stack)
        self.assertEqual(flat_track[0], self.trackDgE[0])
        self.assertEqual(flat_track[1].name, "Z")
        self.assertEqual(
            flat_track[1].source_range,
            otio.opentime.TimeRange(
                otio.opentime.RationalTime(50, 24),
                otio.opentime.RationalTime(50, 24)
            )
        )
        self.assertEqual(flat_track[2], self.trackDgE[2])

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
        self.assertEqual(flat_track[1], self.trackgFg[1])
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
        self.assertEqual(flat_track[0], self.trackDgE[0])
        self.assertEqual(flat_track[1], self.trackABC[1])
        self.assertEqual(flat_track[2], self.trackDgE[2])

        tracks = [
            self.trackABC,
            self.trackgFg
        ]
        flat_track = otio.algorithms.flatten_stack(tracks)
        self.assertEqual(flat_track[0], self.trackABC[0])
        self.assertEqual(flat_track[1], self.trackgFg[1])
        self.assertEqual(flat_track[2], self.trackABC[2])

    def test_flatten_example_code(self):
        timeline = otio.adapters.read_from_file(MULTITRACK_EXAMPLE_PATH)
        preflattened = otio.adapters.read_from_file(PREFLATTENED_EXAMPLE_PATH)
        preflattened_track = preflattened.video_tracks()[0]
        flattened_track = otio.algorithms.flatten_stack(
            timeline.video_tracks()
        )

        # the names will be different, so clear them both
        preflattened_track.name = None
        flattened_track.name = None

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
