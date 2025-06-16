#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Test file for the track algorithms library."""

import unittest

import opentimelineio as otio
import opentimelineio.test_utils as otio_test_utils


class TimelineTrimmingTests(unittest.TestCase, otio_test_utils.OTIOAssertions):
    """ test harness for timeline trimming function """

    def make_sample_timeline(self):
        result = otio.adapters.read_from_string(
            """
            {
                "OTIO_SCHEMA": "Timeline.2",
                "canvas_size": null,
                "metadata": {},
                "name": null,
                "tracks": {
                    "OTIO_SCHEMA": "Stack.1",
                    "children": [
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
                    ],
                    "effects": [],
                    "markers": [],
                    "metadata": {},
                    "name": "tracks",
                    "source_range": null
                }
            }""",
            "otio_json"
        )

        return result, result.tracks[0]

    def test_trim_to_existing_range(self):
        original_timeline, original_track = self.make_sample_timeline()
        self.assertEqual(
            original_track.trimmed_range(),
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(150, 24)
            )
        )

        # trim to the exact range it already has
        trimmed = otio.algorithms.timeline_trimmed_to_range(
            original_timeline,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(150, 24)
            )
        )
        # it shouldn't have changed at all
        self.assertIsOTIOEquivalentTo(original_timeline, trimmed)

    def test_trim_to_longer_range(self):
        original_timeline, original_track = self.make_sample_timeline()
        # trim to a larger range
        trimmed = otio.algorithms.timeline_trimmed_to_range(
            original_timeline,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(-10, 24),
                duration=otio.opentime.RationalTime(160, 24)
            )
        )
        # it shouldn't have changed at all
        self.assertJsonEqual(original_timeline, trimmed)

    def test_trim_front(self):
        original_timeline, original_track = self.make_sample_timeline()
        # trim off the front (clip A and part of B)
        trimmed = otio.algorithms.timeline_trimmed_to_range(
            original_timeline,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(60, 24),
                duration=otio.opentime.RationalTime(90, 24)
            )
        )
        self.assertNotEqual(original_timeline, trimmed)
        trimmed = trimmed.tracks[0]

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
        original_timeline, original_track = self.make_sample_timeline()
        # trim off the end (clip C and part of B)
        trimmed_timeline = otio.algorithms.timeline_trimmed_to_range(
            original_timeline,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(0, 24),
                duration=otio.opentime.RationalTime(90, 24)
            )
        )
        # rest of the tests are on the track
        trimmed = trimmed_timeline.tracks[0]

        self.assertNotEqual(original_timeline, trimmed)
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
        original_timeline, original_track = self.make_sample_timeline()
        self.assertEqual(
            otio.opentime.RationalTime(150, 24),
            original_timeline.duration()
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
            original_timeline.duration()
        )

        # if you try to sever a Transition in the middle it should fail
        with self.assertRaises(otio.exceptions.CannotTrimTransitionsError):
            trimmed = otio.algorithms.timeline_trimmed_to_range(
                original_timeline,
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(5, 24),
                    duration=otio.opentime.RationalTime(50, 24)
                )
            )

        with self.assertRaises(otio.exceptions.CannotTrimTransitionsError):
            trimmed = otio.algorithms.timeline_trimmed_to_range(
                original_timeline,
                otio.opentime.TimeRange(
                    start_time=otio.opentime.RationalTime(45, 24),
                    duration=otio.opentime.RationalTime(50, 24)
                )
            )

        trimmed = otio.algorithms.timeline_trimmed_to_range(
            original_timeline,
            otio.opentime.TimeRange(
                start_time=otio.opentime.RationalTime(25, 24),
                duration=otio.opentime.RationalTime(50, 24)
            )
        )
        self.assertNotEqual(original_timeline, trimmed)

        expected = otio.adapters.read_from_string(
            """
            {
                "OTIO_SCHEMA": "Timeline.2",
                "canvas_size": null,
                "metadata": {},
                "name": null,
                "tracks": {
                    "OTIO_SCHEMA": "Stack.1",
                    "children": [
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
                                    "in_offset": {
                                        "OTIO_SCHEMA": "RationalTime.1",
                                        "rate": 24,
                                        "value": 12
                                    },
                                    "metadata": {},
                                    "name": null,
                                    "out_offset": {
                                        "OTIO_SCHEMA": "RationalTime.1",
                                        "rate": 24,
                                        "value": 20
                                    },
                                    "transition_type": null
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
                    ],
                    "effects": [],
                    "markers": [],
                    "metadata": {},
                    "name": "tracks",
                    "source_range": null
                }
            }
            """,
            "otio_json"
        )

        self.assertJsonEqual(expected, trimmed)


if __name__ == '__main__':
    unittest.main()
