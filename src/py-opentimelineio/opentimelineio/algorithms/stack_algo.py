# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """ Algorithms for stack objects. """

from .. import (
    schema,
    opentime,
    _otio,
)


def top_clip_at_time(in_stack, t):
    """Return the topmost visible child that overlaps with time ``t``.

    Example::

        tr1: G1, A, G2
        tr2: [B------]
        G1, and G2 are gaps, A and B are clips.

    If ``t`` is within ``A``, ``A`` will be returned. If ``t`` is within ``G1`` or
    ``G2``, ``B`` will be returned.

    :param Stack in_stack: Stack
    :param RationalTime t: Time
    :returns: Top clip
    :rtype: Clip
    """

    # ensure that it only runs on stacks
    if not isinstance(in_stack, schema.Stack):
        raise ValueError(
            "Argument in_stack must be of type otio.schema.Stack, "
            "not: '{}'".format(
                type(in_stack)
            )
        )

    # build a range to use the `clip_if`method.
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
        if hasattr(track, "clip_if"):
            valid_results = list(
                c for c in track.clip_if(search_range, shallow_search=True)
                if c.visible()
            )

        # XXX doesn't handle nested tracks/stacks at the moment

        for result in valid_results:
            return result

    return None


flatten_stack = _otio.flatten_stack
