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

__doc__ = """ Algorithms for stack objects. """

from .. import (
    schema,
    opentime,
    _otio,
)


def top_clip_at_time(in_stack, t):
    """Return the topmost visible child that overlaps with time t.

    Example:
    tr1: G1, A, G2
    tr2: [B------]
    G1, and G2 are gaps, A and B are clips.

    If t is within A, a will be returned.  If t is within G1 or G2, B will be
    returned.
    """

    # ensure that it only runs on stacks
    if not isinstance(in_stack, schema.Stack):
        raise ValueError(
            "Argument in_stack must be of type otio.schema.Stack, "
            "not: '{}'".format(
                type(in_stack)
            )
        )

    # build a range to use the `each_child`method.
    search_range = opentime.TimeRange(
        start_time=t,
        # 0 duration so we are just sampling a point in time.
        # XXX Should this duration be equal to the length of one sample?
        #     opentime.RationalTime(1, rate)?
        duration=opentime.RationalTime(0, t.rate)
    )

    # walk through the children of the stack in reverse order.
    for track in reversed(in_stack):
        valid_results = []
        if hasattr(track, "each_child"):
            valid_results = list(
                c for c in track.each_clip(search_range, shallow_search=True)
                if c.visible()
            )

        # XXX doesn't handle nested tracks/stacks at the moment

        for result in valid_results:
            return result

    return None


flatten_stack = _otio.flatten_stack
