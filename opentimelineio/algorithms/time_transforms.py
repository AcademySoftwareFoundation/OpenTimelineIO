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

__doc__ = """Implementation of functions for query time."""

from .. import (
    opentime
)

def _transform_range(range_to_transform, from_space, to_space):
    if from_space is to_space:
        return range_to_transform

    parent_space = to_space
    child_space = from_space
    if from_space.is_parent_of(to_space):
        parent_space = from_space
        child_space = to_space

    # @TODO: here you go
    while parent_space



def range_of(
    item,
    in_scope=None, # must be a parent or child of item (Default is: item)
    trimmed_to=None, # must be a parent of item (default is: item)
    # with_transitions=False, #todo make this an enum
):

    range_in_item_space = item.trimmed_range()
    if trimmed_to is not None and trimmed_to is not item:
        range_in_item_space = _trim_to(item, trimmed_to)

    if in_scope is None or in_scope is item:
        return range_in_item_space

    return _transform_range(range_in_item_space, item, in_scope)



