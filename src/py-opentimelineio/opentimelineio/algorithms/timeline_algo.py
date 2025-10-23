# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Algorithms for timeline objects."""

import copy

from . import (
    track_algo
)


def timeline_trimmed_to_range(in_timeline, trim_range):
    """
    Returns a new timeline that is a copy of the in_timeline, but with items
    outside the trim_range removed and items on the ends trimmed to the
    trim_range.

    .. note:: the timeline is never expanded, only shortened.

    Please note that you could do nearly the same thing non-destructively by
    just setting the :py:class:`.Track`\'s source_range but sometimes you want to
    really cut away the stuff outside and that's what this function is meant for.

    :param Timeline in_timeline: Timeline to trim
    :param TimeRange trim_range:
    :returns: New trimmed timeline
    :rtype: Timeline
    """
    new_timeline = copy.deepcopy(in_timeline)

    for track_num, child_track in enumerate(in_timeline.tracks):
        # @TODO: put the trim_range into the space of the tracks
        # new_range = new_timeline.tracks.transformed_time_range(
        #     trim_range,
        #     child_track
        # )

        # trim the track and assign it to the new stack.
        new_timeline.tracks[track_num] = track_algo.track_trimmed_to_range(
            child_track,
            trim_range
        )

    return new_timeline
