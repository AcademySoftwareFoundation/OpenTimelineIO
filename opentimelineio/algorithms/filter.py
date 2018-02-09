#!/usr/bin/env python
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

"""Algorithms for filtering OTIO files.  """

import copy
import opentimelineio as otio


def _is_in(thing, container):
    return any(thing is item for item in container)


def _isinstance_in(child, typelist):
    return any(isinstance(child, t) for t in typelist)


def filtered_items(
    input_object,
    unary_filter_fn,
    types_to_prune=None,
    types_to_filter=None,
):
    """Filter input_object with unary_filter_fn to make a new copy of object.

    unary_filter_fn will be called with the objects from input_object passed in
    as arguments one a a time, including the input_object itself, in a depth
    first traversal order.

    If unary function returns an object, that object will be inserted into the
    hierarchy, replacing whichever object was passed in to it.  If it returns
    None, that object will be pruned, and all of its children will be omitted
    from iteration.  If the function returns a tuple, that tuple will be
    inserted into the hierarchy.

    If you have a track: [A,B,C]

    If your unary function is:
        def fn(thing):
            if thing.name == B:
                return thing' # some transformation of B
            else:
                return thing

    filtered_items(track, fn) => [A,B',C]

    If your unary function is:
        def fn(thing):
            if thing.name == B:
                return None
            else:
                return thing

    filtered_items(track, fn) => [A,C]

    If your unary function is:
        def fn(thing):
            if thing.name == B:
                return tuple(B_1,B_2,B_3)
            else:
                return thing

    filtered_items(track, fn) => [A,B_1,B_2,B_3,C]
    """

    # deep copy everything
    mutable_object = copy.deepcopy(input_object)

    prune_list = set()

    header_list = [mutable_object]

    if isinstance(mutable_object, otio.schema.Timeline):
        header_list.append(mutable_object.tracks)

    iter_list = header_list + list(mutable_object.each_child())

    for child in iter_list:
        if (
            _safe_parent(child) is not None
            and _is_in(child.parent(), prune_list)
        ):
            prune_list.add(child)
            continue

        parent = None
        child_index = None
        if _safe_parent(child) is not None:
            child_index = child.parent().index(child)
            parent = child.parent()
            del child.parent()[child_index]

        # first try to prune
        if (types_to_prune and _isinstance_in(child, types_to_prune)):
            result = None
        # then try to pass through
        elif types_to_filter and not _isinstance_in(child, types_to_filter):
            result = child
        # finally call the user function
        else:
            result = unary_filter_fn(child)

        if child is mutable_object:
            mutable_object = result

        if result is None:
            prune_list.add(child)
            continue

        if type(result) is not tuple:
            result = [result]

        if parent is not None:
            parent[child_index:child_index] = result

    return mutable_object


def _safe_parent(child):
    if hasattr(child, 'parent'):
        return child.parent()
    return None


def filtered_with_sequence_context(
    input_object,
    reduce_fn,
    types_to_prune=None,
    types_to_filter=None,
):
    """Filter input_object with reduce_fn to make a new copy of object.

    reduce_fn will be called with the objects from input_object, in the form
    reduce_fn(prev_item, child, next_item) where prev_item and next_item are
    the result of calling child.parent().neighbors_of(child) *from the original
    sequence*, or None if the item is not in a sequence.

    If reduce_fn returns an object, that object will be inserted into the
    hierarchy, replacing whichever object was passed in to it.  If it returns
    None, that object will be pruned, and all of its children will be omitted
    from iteration.  If the function returns a tuple, that tuple will be
    inserted into the hierarchy.  If an object is pruned, it will still be
    passed into the next iteration as the prev_item call for the next item.

    If you have a track: [A,B,C]

    If your reduce_fn is:
        def fn(prev_item, thing, next_item):
            if prev_item.name == A:
                return D # new clip
            else:
                return thing

    if filtered_with_sequence_context(track, fn) is called, the order will be:
        fn(None, A, B) => A
        fn(A, B, C) => D
        fn(B, C, D) => C # !! note that it was passed B instead of D.
    So the result is:
        [A, D, C]

    If your reduce_fn is:
        def fn(prev_item, thing, next_item):
            if prev_item.name == A:
                return None # prune the clip
            else:
                return thing

    if filtered_with_sequence_context(track, fn) is called, the order will be:
        fn(None, A, B) => A
        fn(A, B, C) => None
        fn(B, C, D) => C # !! note that it was passed B instead of D.
    So the result is:
        [A, C]

    If your reduce_fn is:
        def fn(prev_item, thing, next_item):
            if prev_item.name == A:
                return (D, E) # tuple of new clips
            else:
                return thing

    if filtered_with_sequence_context(track, fn) is called, the order will be:
        fn(None, A, B) => A
        fn(A, B, C) => (D, E)
        fn(B, C, D) => C # !! note that it was passed B instead of D.
    So the result is:
        [A, D, E, C]

    Additionally, types_to_prune and types_to_filter let you skip or 
    prune classes without having to build logic into your function.

    The order of operation is:
        for each thing to iterate on: 
            1 if it isinstance of anything in the prune list, prune it.
            2 if it is not isinstance of anything in the types_to_filter, 
                or the types_to_filter is None, pass it through, without 
                giving it to your function
            3 otherwise, call the reduce_fn and process according to the result.
    """

    # deep copy everything
    mutable_object = copy.deepcopy(input_object)

    prune_list = set()

    header_list = [mutable_object]

    if isinstance(mutable_object, otio.schema.Timeline):
        header_list.append(mutable_object.tracks)

    iter_list = header_list + list(mutable_object.each_child())

    # expand to include prev, next when appropriate
    expanded_iter_list = []
    for child in iter_list:
        if (
            _safe_parent(child)
            and isinstance(child.parent(), otio.schema.Track)
        ):
            prev_item, next_item = child.parent().neighbors_of(child)
            expanded_iter_list.append((prev_item, child, next_item))
        else:
            expanded_iter_list.append((None, child, None))

    for prev_item, child, next_item in expanded_iter_list:
        if (
            _safe_parent(child) is not None
            and _is_in(child.parent(), prune_list)
        ):
            prune_list.add(child)
            continue

        parent = None
        child_index = None
        if _safe_parent(child) is not None:
            child_index = child.parent().index(child)
            parent = child.parent()
            del child.parent()[child_index]

        # first try to prune
        if (types_to_prune and _isinstance_in(child, types_to_prune)):
            result = None
        # then try to pass through
        elif types_to_filter and not _isinstance_in(child, types_to_filter):
            result = child
        # finally call the user function
        else:
            result = reduce_fn(prev_item, child, next_item)

        if child is mutable_object:
            mutable_object = result

        if result is None:
            prune_list.add(child)
            continue

        if type(result) is not tuple:
            result = [result]

        if parent is not None:
            parent[child_index:child_index] = result

    return mutable_object
