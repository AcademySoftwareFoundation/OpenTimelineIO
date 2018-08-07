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
    core,
)

__doc__ = """Implementation of functions for query time."""


def _path_in_parent_order(from_item, to_item):
    if to_item.is_parent_of(from_item):
        from_item_is_parent = False
        parent = to_item
        child = from_item
    elif from_item.is_parent_of(to_item):
        from_item_is_parent = True
        parent = from_item
        child = to_item
        # @TODO: find common parent here
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

    return result, from_item_is_parent

def _after_to_parent_before_transform(item):
    off = (item.range_in_parent().start_time - item.trimmed_range().start_time)
    return opentime.TimeTransform(offset=off)

def path_between(from_item, to_item):
    """
    Return a tuple of items starting with from_item and ending with to_item
    to walk across in order to arrive at to_item.
    """

    # check to find parent
    if to_item is from_item:
        return (from_item,)

    result, from_item_is_parent = _path_in_parent_order(from_item, to_item)

    if from_item_is_parent:
        result = reversed(result)

    return tuple(result)


def relative_transform(src_frame, dst_frame):
    if (
            not isinstance(src_frame, core.ReferenceFrame)
            or not isinstance(dst_frame, core.ReferenceFrame)
    ):
        raise NotImplementedError("relative_transform only takes ReferenceFrames")

    result = opentime.TimeTransform()

    if src_frame is dst_frame:
        return result

    src_item = src_frame.parent
    dst_item = dst_frame.parent

    # get the path of objects from one to the other, in parent order

    object_path = (src_item, )
    flipped = False

    if src_item is not dst_item:
        object_path, flipped = _path_in_parent_order(src_item, dst_item)
    elif src_frame is src_item.after_effects:
        flipped = True

    if flipped:
        src_frame, dst_frame = dst_frame, src_frame
        src_item, dst_item = dst_item, src_item

    for obj in object_path:
        # before -> after
        if (
                # if its an inbetween item
                obj not in (src_item, dst_item)

                # or if the start frame is before effects
                or (obj is src_item and src_frame is src_item.before_effects)

                # or if the final frame is after effects
                or (obj is dst_item and dst_frame is dst_item.after_effects)
        ):
            result = obj.effects_time_transform() * result

        # after -> parent.before
        if (
                # if its an inbetween item
                obj is not dst_item
        ):
            result = _after_to_parent_before_transform(obj) * result

    if flipped:
        result = result.inverted()

    return result



def range_of(
    src_frame,
    # must be a parent or child of item (Default is: item)
    dst_frame=None,
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

    if not isinstance(src_frame, core.ReferenceFrame):
        raise NotImplementedError("range of only takes ReferenceFrames")

    dst_frame = dst_frame or src_frame
    trimmed_to = trimmed_to or src_frame.parent

    # if we're going from the current to the same space, shortcut
    if (
            (src_frame is dst_frame)
            and (src_frame.parent is trimmed_to)
    ):
        return src_frame.parent.trimmed_range()

    source_item = src_frame.parent

    xform = relative_transform(src_frame=src_frame, dst_frame=dst_frame)

    range_to_xform = xform * source_item.trimmed_range(src_frame)

    if trimmed_to is not source_item:
        # walk trims all the way up to the trimmed to from source_item
        trim_path = path_between(source_item, trimmed_to)

        item_is_parent = source_item.is_parent_of(trimmed_to)
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
        # so transform them to the target_item space so that they can be
        # applied to range_to_xform
        trim_to_target_xform = relative_transform(trim_path[-1].after_effects, dst_frame)
        result_bounds = trim_to_target_xform * result_bounds

        # apply the new trim to the final bounds
        range_to_xform = result_bounds.clamp(range_to_xform)

    return range_to_xform
