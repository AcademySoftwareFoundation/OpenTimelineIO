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



def _filtered_iterable(iterable, unary_filter_fn):
    # filter the root object
    new_parent = unary_filter_fn(copy.deepcopy(iterable))
    if not new_parent:
        return None

    # empty the new parent
    del new_parent[:]

    # filter the children
    for child in iterable:
        filtered_child = filtered_items(child, unary_filter_fn)
        if filtered_child:
            if not isinstance(filtered_child, tuple):
                filtered_child = [filtered_child]
            new_parent.extend(filtered_child)

    return new_parent

def filtered_items(input_object, unary_filter_fn):
    """Create a new copy of input_object whose children have been processed by 
    unary_filter_fn.  If unary_filter_fn returns an object, that object will 
    get placed there, otherwise if unary_filter_fn returns none, it will be 
    skipped.
    """

    if isinstance(input_object, otio.schema.Timeline):
        result = copy.deepcopy(input_object)
        del result.tracks[:]
        child = filtered_items(input_object.tracks, unary_filter_fn)
        if child:
            result.tracks.extend(child)
    elif isinstance(input_object, otio.core.Composition):
        result = copy.deepcopy(input_object)
        del result[:]
        child = _filtered_iterable(input_object, unary_filter_fn)
        if child:
            result.extend(child)
    else:
        result = unary_filter_fn(input_object)

    return result


def _reduced_iterable(iterable, reduce_fn, prev=None, next_item=None):
    # filter the root object
    new_parent = reduce_fn(prev, copy.deepcopy(iterable), next_item)
    if not new_parent:
        return None

    # empty the new parent
    del new_parent[:]

    target_iter = iter(iterable)

    prev_item = None
    current_item = next(target_iter, None)
    next_item = next(target_iter, None)

    while current_item is not None:
        reduced_child = reduced_items(current_item, reduce_fn, prev_item, next_item)
        if reduced_child:
            if not isinstance(reduced_child, tuple):
                reduced_child = [reduced_child]
            new_parent.extend(reduced_child)

         # iterate
        prev_item = current_item
        current_item = next_item
        next_item = next(target_iter, None)

    return new_parent

def reduced_items(input_object, reduce_fn, prev_item=None, next_item=None):
    """Create a new copy of input_object whose children have been processed by 
    reduce_fn, which is a function that takes three arguments: 
        (prev, current, next)
    If reduce_fn returns an object, that object will get placed there (as 
    current), otherwise if reduce_fn returns none, it will be skipped.

    If an object from the parent is skipped, it will still be the prev item to
    the next invocation.

    EG if you filter [A,B,C] and your reduce_fn removes B only, the reduce_fn 
    will be called three times with the arguments:
        (None, A, B) => modified version of A
        (A, B, C) => None
        (B, C, None) => modified version of C.

    Every argument has been deepcopy'd from the source, so this is non 
    destructive.
    """

    if isinstance(input_object, otio.schema.Timeline):
        result = copy.deepcopy(input_object)
        del result.tracks[:]
        child = reduced_items(input_object.tracks, reduce_fn)
        if child:
            result.tracks.extend(child)
    elif isinstance(input_object, otio.core.Composition):
        result = copy.deepcopy(input_object)
        del result[:]
        child = _reduced_iterable(input_object, reduce_fn)
        if child:
            result.extend(child)
    else:
        result = reduce_fn(prev_item, input_object, next_item)

    return result


