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

"""Algorithms for timeline objects."""

import copy

from . import (
    track_algo
)


def timeline_trimmed_to_range(in_timeline, trim_range):
    """Returns a new timeline that is a copy of the in_timeline, but with items
    outside the trim_range removed and items on the ends trimmed to the
    trim_range. Note that the timeline is never expanded, only shortened.
    Please note that you could do nearly the same thing non-destructively by
    just setting the Track's source_range but sometimes you want to really cut
    away the stuff outside and that's what this function is meant for."""
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
