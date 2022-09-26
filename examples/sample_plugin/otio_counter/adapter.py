# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
import opentimelineio as otio

"""
This is the implementation of the contrived example adapter that simply writes
the number of tracks in the timeline to a file, or will read an integer from a
file and create a timeline with that number of tracks.

This would be where your plugin implementation would be.
"""


def write_to_string(input_otio):
    return '{}'.format(len(input_otio.tracks))


def read_from_string(input_str):
    t = otio.schema.Timeline()

    for i in range(int(input_str)):
        t.tracks.append(otio.schema.Track())

    return t
