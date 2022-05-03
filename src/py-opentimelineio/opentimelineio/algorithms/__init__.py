# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Algorithms for OTIO objects."""

# flake8: noqa
from .track_algo import (
    track_trimmed_to_range,
    track_with_expanded_transitions
)

from .stack_algo import (
    flatten_stack,
    top_clip_at_time,
)

from .filter import (
    filtered_composition,
    filtered_with_sequence_context
)
from .timeline_algo import (
    timeline_trimmed_to_range
)
