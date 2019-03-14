#!/usr/bin/env python

""" Algorithms for translating time up and down the hierarchy. """

import opentimelineio as otio


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

    search_from = from_space
    search_to = to_space

    # for the purpose of walking from A to B, if either argument is a Timeline
    # it needs to be turned into the stack, since there isn't a parent()
    # pointer back to the Timeline.

    # because timeline doesn't participate in the hierarchy
    from_timeline = isinstance(search_from.source_object(), otio.schema.Timeline)
    if from_timeline:
        search_from = search_from.source_object().tracks.external_space()

    # because timeline doesn't participate in the hierarchy
    to_timeline = isinstance(search_to.source_object(), otio.schema.Timeline)
    if to_timeline:
        search_to = search_to.source_object().tracks.external_space()

    # start with an identity transform
    transform = otio.opentime.TimeTransform()

    if from_space.source_object() is not to_space.source_object():

        # determine the correct parent
        child_space = search_from
        parent_space = search_to
        inverted = False

        if not (
                parent_space.source_object().is_parent_of(
                    child_space.source_object()
                )
        ):
            inverted = True
            tmp = child_space
            child_space = parent_space
            parent_space = tmp


        # check again to make sure the other way works
        if not (
                parent_space.source_object().is_parent_of(
                    child_space.source_object()
                )
        ):
            raise otio.exceptions.NotAChildError(
                "Objects {} and {} are not part of the same hierarchy.  "
                "One must be the parent of the other to transform from one "
                "space to the other.".format(
                    search_from,
                    search_to
                )
            )

        current = child_space

        while current.source_object() is not parent_space.source_object():
            # transform to the external space on the current object
            time_to_transform = parent_space.source_object()._transform_time(
                time_to_transform,
                current,
                current.source_object().external_space()
            )

            # @TODO: need to translate from a non-external space
            # otherwise, translate to the next object
            to_parent = current.source_object().parent().transform_child_to_parent(
                current.source_object()
            )
            time_to_transform = to_parent * time_to_transform
            current = current.source_object().parent().internal_space()

        from_space = current

    time_to_transform = transform * time_to_transform

    # do the object-internal transformation
    time_to_transform = to_space.source_object()._transform_time(
        time_to_transform,
        from_space,
        to_space,
        # trim
    )

    # last thing to check is if the top object is a Timeline
    return time_to_transform
