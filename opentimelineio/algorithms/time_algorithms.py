#!/usr/bin/env python

""" Algorithms for translating time up and down the hierarchy. """


def transform_time(
        time_to_transform,
        from_space,
        to_space,
        trim=True
):
    """Transform time_to_transform from from_space to to_space.

    If trim is true, apply trimming operations (source_range, etc) along the way.

    If the time_to_transform is trimmed out entirely, transform_time will return
    None.
    """
    # if the space is already correct
    if from_space == to_space:
        return time_to_transform

    if from_space.source_object() is not to_space.source_object():
        # determine the correct parent
        # child_object = from_space.source_object
        # parent_object = to_space.source_object
        raise NotImplementedError("separate objects")

    return to_space.source_object()._transform_time(
        time_to_transform,
        from_space,
        to_space,
        trim
    )
