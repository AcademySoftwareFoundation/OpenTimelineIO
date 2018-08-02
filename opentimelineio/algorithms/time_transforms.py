#
# Copyright 2018 Pixar Animation Studios
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

from .. import (
    opentime,
)

__doc__ = """Implementation of functions for query time."""


def path_between(from_item, to_item):
    """
    Return a tuple of items starting with from_item and ending with to_item
    to walk across in order to arrive at to_item.
    """

    # @TODO: Should this always return items in parent order?

    # check to find parent
    if to_item is from_item:
        return (from_item,)
    elif to_item.is_parent_of(from_item):
        from_item_is_parent = False
        parent = to_item
        child = from_item
    elif from_item.is_parent_of(to_item):
        from_item_is_parent = True
        parent = from_item
        child = to_item
    else:
        raise RuntimeError(
            "No path from {} to {}, not members of the same "
            "hierarchy.".format(from_item, to_item)
        )

    result = []
    while child is not parent:
        result.append(child)
        child = child.parent()
    result.append(parent)

    if from_item_is_parent:
        result = reversed(result)

    return tuple(result)


def relative_transform(from_item, to_item):
    result = opentime.TimeTransform()

    if from_item is to_item:
        return result

    path = path_between(from_item, to_item)

    from_item_is_parent = from_item.is_parent_of(to_item)
    if from_item_is_parent:
        path = list(reversed(path))

    for child in path[:-1]:
        result = child.local_to_parent_transform() * result

    if from_item_is_parent:
        result = result.inverted()

    return result


# @TODO: Target is something along these lines:
# range_of(cl.before_effects, parent_track.after_effects, trimmed_to=parent_track)

def range_of(
    source_frame,
    target_frame=None, # must be a parent or child of item (Default is: item)
    trimmed_to=None,  # must be a parent of item (default is: item)
    # with_transitions=False, # @TODO
):
    """ Return the range of the specified item in the specified scope, trimmed
    to the specified scope.

    item         :: otio.core.Item
    relative_to  :: otio.core.Item (if None, will default to item space)
    trimmed_to   :: otio.core.Item (if None, will default to item space)

    For example:
        # time ranges are written as (start frame, duration) in 24hz.
        A1:: Clip       trimmed_range = (10, 20)
        T1:: Track      [A1], trimmed_range = (2, 5)

        range_of(A1, relative_to=A1, trimmed_to=A1)  => (10, 20)
        range_of(A1, relative_to=T1, trimmed_to=A1)  => (0,  20)
        range_of(A1, relative_to=A1, trimmed_to=T1)  => (12, 5)
        range_of(A1, relative_to=T1, trimmed_to=T1)  => (2,  5)
    """

    relative_to = relative_to or item
    trimmed_to = trimmed_to or item

    # if we're going from the current to the same space, shortcut
    if ((item is relative_to) and (item is trimmed_to)):
        return item.trimmed_range()

    xform = relative_transform(from_item=item, to_item=relative_to)

    range_to_xform = xform * item.trimmed_range()

    if trimmed_to is not item:
        # walk trims all the way up to the trimmed to from item
        trim_path = path_between(item, trimmed_to)

        item_is_parent = item.is_parent_of(trimmed_to)
        if item_is_parent:
            trim_path = list(reversed(trim_path))

        result_bounds = None
        for count, child in enumerate(trim_path):
            result_bounds = result_bounds or child.trimmed_range()
            result_bounds = child.trimmed_range().clamp(result_bounds)

            # if this has a parent *and* it isn't the last thing in the chain
            if child.parent() and not count == len(trim_path) - 1:
                result_bounds = (
                    child.local_to_parent_transform()
                    * result_bounds
                )

        # at this point result_bounds should be trimmed in the parent space
        # so transform them to the relative_to space so that they can be
        # applied to range_to_xform
        trim_to_target_xform = relative_transform(trim_path[-1], relative_to)
        result_bounds = trim_to_target_xform * result_bounds

        # apply the new trim to the final bounds
        range_to_xform = result_bounds.clamp(range_to_xform)

    return range_to_xform
