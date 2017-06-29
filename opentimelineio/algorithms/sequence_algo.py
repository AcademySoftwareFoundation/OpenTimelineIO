""" Algorithms for sequence objects. """

import copy

from ..import (
    schema,
    exceptions,
)


def sequence_with_expanded_transitions(in_seq):
    """ Expands transitions such that neighboring clips are trimmed into
    regions of overlap.

    For example, if your sequence is:
        Clip1, T, Clip2

    will return:
        Clip1', Clip1_t, T, Clip2_t, Clip2'

    Where Clip1' is the part of Clip1 not in the transition, Clip1_t is the
    part inside the transition and so on.
    """

    result_sequence = []

    seq_iter = iter(in_seq)
    prev_thing = None
    thing = next(seq_iter, None)
    next_thing = next(seq_iter, None)

    while thing is not None:
        if isinstance(thing, schema.Transition):
            result_sequence.append(_expand_transition(thing, in_seq))
        else:
            # not a transition, but might be trimmed by one before or after
            # in the sequence
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

        # loop
        prev_thing = thing
        thing = next_thing
        next_thing = next(seq_iter, None)

    return result_sequence


def _expand_transition(target_transition, from_sequence):
    """ Expand transitions into the portions of pre-and-post clips that
    overlap with the transition.
    """

    result = from_sequence.neighbors_of(
        target_transition,
        schema.NeighborGapPolicy.around_transitions
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

    # ensure that pre.source_range is set, because it will get manipulated
    pre.source_range = copy.deepcopy(pre.trimmed_range())

    if target_transition.in_offset is None:
        raise RuntimeError(
            "in_offset is None on: {}".format(target_transition)
        )

    if target_transition.out_offset is None:
        raise RuntimeError(
            "out_offset is None on: {}".format(target_transition)
        )

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

    # ensure that post.source_range is set, because it will get manipulated
    post.source_range = copy.deepcopy(post.trimmed_range())

    post.source_range.start_time = (
        post.source_range.start_time - target_transition.in_offset
    ).rescaled_to(post.source_range.start_time)
    post.source_range.duration = trx_duration.rescaled_to(
        post.source_range.start_time
    )

    return (pre, target_transition, post)


def _trim_from_transitions(thing, pre=None, post=None):
    """ Trim clips next to transitions. """

    result = copy.deepcopy(thing)

    result.source_range = copy.deepcopy(result.trimmed_range())

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
