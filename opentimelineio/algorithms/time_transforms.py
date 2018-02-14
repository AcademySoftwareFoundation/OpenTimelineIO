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
    schema
)

__doc__ = """Implementation of functions for query time."""


def _transform_range(range_to_transform, from_space, to_space, trim_to=None):
    found_trim = trim_to is None
    found_transform = to_space is None

    while not found_transform or not found_trim:
        parent_range = from_space.range_in_parent()
        if not found_trim:
            trim_parent_range = from_space.trimmed_range_in_parent()
            if trim_parent_range.start_time != parent_range.start_time:
                diff = trim_parent_range.start_time - parent_range.start_time

            range_to_transform.start_time += diff

            if from_space.parent() is trim_to:
                found_trim = True
            range_to_transform.duration = min(
                range_to_transform.duration,
                trim_parent_range.duration
            )

        if not found_transform:
            range_to_transform.start_time += parent_range.start_time
            if from_space.parent() is to_space:
                found_transform = True

        from_space = from_space.parent()

    return range_to_transform


# @TODO: CURRENTLY ONLY WORKS IF item is a child of IN_SCOPE AND TRIMMED_TO
def range_of(
    item,
    # @TODO: scope?  Or space? reference frame?
    in_scope=None,    # must be a parent or child of item (Default is: item)
    trimmed_to=None,  # must be a parent of item (default is: item)
    # with_transitions=False, # @TODO
):
    """ Return the range of the specified item in the specified scope, trimmed
    to the specified scope.

    item      :: otio.core.Item
    in_scope  :: otio.core.Item (if None, will default to item space)
    trimmed_to:: otio.core.Item (if None, will default to item space)

    For example:
        # time ranges are written as (start frame, duration) in 24hz.
        A1:: Clip       trimmed_range = (10, 20)
        T1:: Track      [A1], trimmed_range = (2, 5)

        range_of(A, in_scope=A1, trimmed_to=A1)  => (10, 20)
        range_of(A, in_scope=T1, trimmed_to=A1)  => (0,  20)
        range_of(A, in_scope=A1, trimmed_to=T1)  => (12, 5)
        range_of(A, in_scope=T1, trimmed_to=T1)  => (2,  5)
    """

    if in_scope is item:
        in_scope = None

    if trimmed_to is item:
        trimmed_to = None

    # @TODO: should this already be a copy?
    range_in_item_space = copy.deepcopy(item.trimmed_range())

    # @TODO: in the clip, trimmed_range returns a value in media space, *not*
    #        in the intrinsic [0,dur) space.
    if in_scope is not None and isinstance(item, schema.Clip):
        range_in_item_space.start_time.value = 0

    if in_scope is None and trimmed_to is None:
        return range_in_item_space

    return _transform_range(range_in_item_space, item, in_scope, trimmed_to)
