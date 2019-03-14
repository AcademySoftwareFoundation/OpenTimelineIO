#!/usr/bin/env python

""" Algorithms for translating time up and down the hierarchy. """

import opentimelineio as otio


# the different directions have slightly different rules and functions,
# so they've been broken up based on the direction of traversal
def _transform_time_child_to_parent(
        time_to_transform,
        child_space,
        parent_space,
        trim
):
    current = child_space

    while current.source_object() is not parent_space.source_object():
        # transform to the external space on the current object
        time_to_transform = current.source_object()._transform_time(
            time_to_transform,
            current,
            current.source_object().external_space()
        )

        to_parent = current.source_object().parent().transform_child_to_parent(
            current.source_object()
        )
        time_to_transform = to_parent * time_to_transform
        current = current.source_object().parent().internal_space()

    return time_to_transform, current


def _transform_time_parent_to_child(
        time_to_transform,
        child_space,
        parent_space,
        trim=True
):
    # need to build a traversal list since parent pointers are the only means
    # of traversing the hierarchy
    traversal_list = []
    current = child_space.source_object()
    while current is not parent_space.source_object():
        traversal_list.append(current)
        current = current.parent()

    traversal_list.append(parent_space.source_object())

    # reverse the list -- it gets traversed from parent to child
    traversal_list = list(reversed(traversal_list))

    destination_object = child_space.source_object()
    current = parent_space

    for ind, current_object in enumerate(traversal_list):
        # transform to the external space on the current object
        time_to_transform = current_object._transform_time(
            time_to_transform,
            current,
            current_object.internal_space()
        )

        # @TODO: need to translate from a non-external space
        # otherwise, translate to the next object
        next_obj = traversal_list[ind + 1]
        to_child = current_object.transform_child_to_parent(
            next_obj
        ).inverted()
        time_to_transform = to_child * time_to_transform

        current = next_obj.external_space()

        if next_obj is destination_object:
            break

    return time_to_transform, current


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
        time_to_transform = search_from.source_object()._transform_time(
            time_to_transform,
            from_space,
            from_space.source_object().internal_space()
        )
        # because the tracks external space is the same as the timeline's
        # internal space
        search_from = search_from.source_object().tracks.external_space()

    # because timeline doesn't participate in the hierarchy
    to_timeline = isinstance(search_to.source_object(), otio.schema.Timeline)
    if to_timeline:
        search_to = search_to.source_object().tracks.external_space()

    if search_from.source_object() is not search_to.source_object():
        if search_to.source_object().is_parent_of(search_from.source_object()):
            time_to_transform, search_from = _transform_time_child_to_parent(
                time_to_transform,
                search_from,
                search_to,
                trim
            )
        else:
            # check again to make sure the other way works
            if not (
                    search_from.source_object().is_parent_of(
                        search_to.source_object()
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

            time_to_transform, search_from = _transform_time_parent_to_child(
                time_to_transform,
                search_to,
                search_from,
                trim
            )

    # do the final object-internal transformation
    time_to_transform = search_to.source_object()._transform_time(
        time_to_transform,
        search_from,
        search_to,
        # trim
    )

    # apply back the transformation for the timeline at the top
    if to_timeline:
        time_to_transform = to_space.source_object()._transform_time(
            time_to_transform,
            to_space.source_object().internal_space(),
            to_space
        )

    # last thing to check is if the top object is a Timeline
    return time_to_transform
