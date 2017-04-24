""" Algorithms for sequence objects.  """

import copy

from ..import (
    schema,
    exceptions,
)


def sequence_with_expanded_transitions(in_seq):
    """
    Expands transitions such that neighboring clips are trimmed into regions of
    overlap.  For example, if your sequence is:
        Clip1, T, Clip2

    will return:
        Clip1', Clip1_t, T, Clip2_t, Clip2'

    Where Clip1' is the part of Clip1 not in the transition, Clip1_t is the
    part inside the transition and so on.
    """

    sequence_to_modify = copy.deepcopy(in_seq)

    # we want to copy all the top level parameters and settings
    result_sequence = []

    iterable = iter(sequence_to_modify)
    prev_thing = None
    thing = next(iterable, None)
    next_thing = next(iterable, None)

    while thing is not None:
        if isinstance(thing, schema.Transition):
            expanded_trx = _expand_transition(thing, sequence_to_modify)
            result_sequence.append(expanded_trx)
        else:
            # not a transition, but might be trimmed by one coming up
            pre_transition = None
            next_transition = None

            if isinstance(prev_thing, schema.Transition):
                pre_transition = prev_thing

            if isinstance(next_thing, schema.Transition):
                next_transition = next_thing

            result_sequence.append(
                _trim_from_transitions(
                    thing,
                    pre=pre_transition,
                    post=next_transition
                )
            )
        prev_thing = thing
        thing = next_thing
        next_thing = next(iterable, None)

    return result_sequence


def _expand_transition(target_transition, from_sequence):
    result = from_sequence.neighbors_of(
        target_transition,
        schema.NeighborFillerPolicy.around_transitions
    )

    trx_duration = target_transition.in_offset + target_transition.out_offset

    # make copies of the before and after, and modify their in/out points
    pre = copy.deepcopy(result[0])

    if isinstance(pre, schema.Transition):
        raise exceptions.TransitionFollowingATransitionError(
            "cannot put two transitions next to each other in a  sequence: "
            "{}, {}".format(
                pre,
                target_transition
            )
        )
    pre.name = (pre.name or "") + "_transition_pre"
    if not pre.source_range:
        # @TODO: a method to create a default source range?
        pre.source_range = copy.deepcopy(pre.media_reference.available_range)

    if target_transition.in_offset is None:
        raise RuntimeError("in_offset is None on: {}".format(target_transition))

    if target_transition.out_offset is None:
        raise RuntimeError("in_offset is None on: {}".format(target_transition))

    pre.source_range.start_time = (
        pre.source_range.end_time_exclusive()
        - target_transition.in_offset
    )
    pre.source_range.duration = trx_duration.rescaled_to(
        pre.source_range.start_time
    )

    post = copy.deepcopy(result[2])
    if isinstance(post, schema.Transition):
        raise exceptions.TransitionFollowingATransitionError(
            "cannot put two transitions next to each other in a  sequence: "
            "{}, {}".format(
                target_transition,
                post
            )
        )
    post.name = (post.name or "") + "_transition_post"
    if not post.source_range:
        post.source_range = copy.deepcopy(post.media_reference.available_range)

    post.source_range.start_time = (
        post.source_range.start_time - target_transition.in_offset
    ).rescaled_to(post.source_range.start_time)
    post.source_range.duration = trx_duration.rescaled_to(
        post.source_range.start_time
    )

    return (pre, target_transition, post)


def _trim_from_transitions(thing, pre=None, post=None):
    result = copy.deepcopy(thing)

    if not result.source_range:
        result.source_range = copy.deepcopy(
            result.media_reference.available_range
        )

    if pre:
        result.source_range.start_time = (
            result.source_range.start_time + pre.out_offset
        )
        result.source_range.duration = (
            result.source_range.duration - pre.out_offset
        )

    if post:
        result.source_range.duration = (
            result.source_range.duration - post.in_offset
        )

    return result
