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

import copy

from .. import (
    opentime,
    # schema,
)

__doc__ = """Implementation of functions for query time."""


def _transform_range(range_to_transform, from_space, to_space, trim_to=None):
    found_trim = trim_to is None
    found_transform = to_space is None

    # from_space is a parent of either to_space or trim_to
    if (
        (to_space and not to_space.is_parent_of(from_space))
        or (not to_space and from_space.is_parent_of(trim_to))
    ):
        child_space = to_space if to_space is not None else trim_to
        parent_space = from_space

        while not found_transform or not found_trim:
            parent_range = child_space.range_in_parent()
            if not found_trim:
                trim_parent_range = child_space.trimmed_range_in_parent()
                if trim_parent_range.start_time != parent_range.start_time:
                    start_max = max(
                        trim_parent_range.start_time,
                        parent_range.start_time
                    )
                    range_to_transform.start_time = start_max

                # import ipdb; ipdb.set_trace()
                if child_space.parent() is trim_to or child_space is trim_to:
                    found_trim = True
                range_to_transform.duration = min(
                    range_to_transform.duration,
                    trim_parent_range.duration
                )

            if not found_transform:
                child_range = child_space.trimmed_range()
                parent_offset = (
                    parent_range.start_time
                    - range_to_transform.start_time
                )
                range_to_transform.start_time = (
                    child_range.start_time
                    - parent_offset
                )

                if child_space.parent() is parent_space:
                    found_transform = True

            child_space = child_space.parent()
    else:
        child_space = from_space
        parent_space = to_space

        while not found_transform or not found_trim:
            parent_range = child_space.range_in_parent()
            # parent_range = child_space.trimmed_range()
            if not found_trim:
                trim_parent_range = child_space.trimmed_range_in_parent()
                if trim_parent_range.start_time != parent_range.start_time:
                    diff = (
                        trim_parent_range.start_time
                        - parent_range.start_time
                    )
                    range_to_transform.start_time += diff

                # import ipdb; ipdb.set_trace()
                if child_space.parent() is trim_to:
                    found_trim = True
                range_to_transform.duration = min(
                    range_to_transform.duration,
                    trim_parent_range.duration
                )

            if not found_transform:
                range_to_transform.start_time += parent_range.start_time
                if child_space.parent() is parent_space:
                    found_transform = True

            child_space = child_space.parent()

    return range_to_transform


def _trimmed_range(range_to_trim, from_space, trim_to):
    if not trim_to:
        return range_to_trim

    # assume that:
    # 1) range_to_trim is a unique copy already
    # 2) range_to_trim is in the space of from_space

    # import ipdb; ipdb.set_trace()

    # search direction
    if from_space.is_parent_of(trim_to):
        # child -> parent
        path_from_trim = _path_to_parent(trim_to, from_space)
        path_to_trim = reversed(path_from_trim)

        # trim from parent down to trim_to (ending in trim_to space)
        for (child, parent) in path_to_trim:
            trimmed_c_range = copy.deepcopy(
                parent.trimmed_range_of_child(child)
            )

            # trim the range to the current child
            start_time = max(
                range_to_trim.start_time,
                trimmed_c_range.start_time
            )

            end_time = min(
                range_to_trim.end_time_exclusive(),
                trimmed_c_range.end_time_exclusive()
            )

            range_in_parent = opentime.range_from_start_end_time(
                start_time,
                end_time
            )

            # project this into the child space
            offset = (
                start_time
                - trimmed_c_range.start_time
            )

            start_time_in_child = offset + child.trimmed_range().start_time
            range_to_trim.start_time = start_time_in_child
            range_to_trim.duration = range_in_parent.duration

        # project trimmed range from trim_to space back up into the from_space
        for (child, parent) in path_from_trim:
            range_in_parent = parent.range_of_child(child)

            offset = (
                range_in_parent.start_time -
                child.trimmed_range().start_time
            )

            range_to_trim.start_time += offset

    else:
        # child -> parent
        path_to_trim = _path_to_parent(from_space, trim_to)
        path_from_trim = reversed(path_to_trim)

        # import ipdb; ipdb.set_trace()

        # trim from_space up to trim_to
        for (child, parent) in path_to_trim:
            range_in_parent = parent.range_of_child(child)

            offset = (
                range_in_parent.start_time
                - child.trimmed_range().start_time
            )

            # projected range_to_trim up into parent space
            range_to_trim.start_time += offset

            # trim in parent space
            # @TODO: this shouldn't need to deepcopy
            trimmed_c_range = copy.deepcopy(
                parent.trimmed_range_of_child(child)
            )

            # trim the range to the current child
            start_time = max(
                range_to_trim.start_time,
                trimmed_c_range.start_time
            )

            end_time = min(
                range_to_trim.end_time_exclusive(),
                trimmed_c_range.end_time_exclusive()
            )

            # # project this into the child space
            # offset = (
            #     child.trimmed_range().start_time
            #     - trimmed_c_range.start_time
            # )
            #
            # start_time_in_child = offset + start_time
            # end_time_in_child = offset + end_time
            #
            range_to_trim = opentime.range_from_start_end_time(
                start_time,
                end_time
            )

        # project trimmed range from trim_to space back down into the
        # from_space
        for (child, parent) in path_from_trim:
            # range_in_parent = parent.range_of_child(child)
            #
            # offset = (
            #     range_in_parent.start_time -
            #     child.trimmed_range().start_time
            # )
            #
            # range_to_trim.start_time += offset

            offset = (
                child.trimmed_range().start_time
                - parent.range_of_child(child).start_time
            )

            range_to_trim.start_time += offset

    return range_to_trim


def _path_to_parent(*args, **kwargs):
    return []

def relative_transform(from_item, to_item):
    result = opentime.TimeTransform()

    # check to find parent
    if to_item.is_parent_of(from_item):
        from_item_is_parent = False
        parent = to_item
        child = from_item
    elif from_item.is_parent_of(to_item):
        from_item_is_parent = True
        parent = from_item
        child = to_item
    else:
        raise RuntimeError(
            "No transform from {} to {}, not members of the same "
            "hierarchy.".format(from_item, to_item)
        )

    while child is not parent:
        result = child.local_to_parent_transform() * result
        child = child.parent()

    if from_item_is_parent:
        result = result.inverted()

    return result





# @TODO: CURRENTLY ONLY WORKS IF item is a child of relative_to AND TRIMMED_TO
def range_of(
    item,
    relative_to=None,    # must be a parent or child of item (Default is: item)
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

    # @TODO: start without thinking about trims

    # if we're going from the current to the same space, shortcut
    if item is relative_to:
        return item.trimmed_range()

    xform = relative_transform(from_item=item, to_item=relative_to)

    return xform * item.trimmed_range()

    


    # if relative_to is item:
    #     relative_to = None
    #
    # if trimmed_to is item:
    #     trimmed_to = None

    # @TODO: should this already be a copy?
    # range_in_item_space = copy.deepcopy(item.trimmed_range())

    # @TODO: in the clip, trimmed_range returns a value in media space, *not*
    #        in the intrinsic [0,dur) space as it does in most other cases.
    # if relative_to is not None and isinstance(item, schema.Clip):
    #     range_in_item_space.start_time.value = 0

    # if relative_to is None and trimmed_to is None:
    #     return range_in_item_space

    # trimmed_range = _trimmed_range(range_in_item_space, item, trimmed_to)

    # return _transform_range(range_in_item_space, item, relative_to)
