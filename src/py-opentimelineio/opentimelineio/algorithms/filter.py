# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Algorithms for filtering OTIO files.  """

import copy

from .. import (
    schema
)


def _is_in(thing, container):
    return any(thing is item for item in container)


def _isinstance_in(child, typelist):
    return any(isinstance(child, t) for t in typelist)


def filtered_composition(
    root,
    unary_filter_fn,
    types_to_prune=None,
):
    """
    Filter a deep copy of root (and children) with ``unary_filter_fn``.

    The ``unary_filter_fn`` must have this signature:

    .. py:function:: func(item: typing.Any) -> list[typing.Any]
        :noindex:


    1. Make a deep copy of root
    2. Starting with root, perform a depth first traversal
    3. For each item (including root):

       a. If ``types_to_prune`` is not None and item is an instance of a type in
          ``types_to_prune``, prune it from the copy, continue.
       b. Otherwise, pass the copy to ``unary_filter_fn``.  If ``unary_filter_fn``:

          I.   Returns an object: add it to the copy, replacing original
          II.  Returns a tuple: insert it into the list, replacing original
          III. Returns None: prune it
    4. If an item is pruned, do not traverse its children
    5. Return the new deep copy.

    Example 1 (filter)::

        If your unary function is:
            def fn(thing):
                if thing.name == B:
                    return thing' # some transformation of B
                else:
                    return thing

        If you have a track: [A,B,C]

        filtered_composition(track, fn) => [A,B',C]

    Example 2 (prune)::

        If your unary function is:
            def fn(thing):
                if thing.name == B:
                    return None
                else:
                    return thing

        filtered_composition(track, fn) => [A,C]

    Example 3 (expand)::

        If your unary function is:
            def fn(thing):
                if thing.name == B:
                    return tuple(B_1,B_2,B_3)
                else:
                    return thing

        filtered_composition(track, fn) => [A,B_1,B_2,B_3,C]

    Example 4 (prune gaps)::

        track :: [Gap, A, Gap]
            filtered_composition(
                track, lambda _:_, types_to_prune=(otio.schema.Gap,)) => [A]

    :param SerializableObjectWithMetadata root: Object to filter on
    :param unary_filter_fn: Filter function
    :param tuple(type) types_to_prune: Types to prune. Example: (otio.schema.Gap,...)
    """

    # deep copy everything
    mutable_object = copy.deepcopy(root)

    prune_list = set()

    header_list = [mutable_object]

    if isinstance(mutable_object, schema.Timeline):
        header_list.append(mutable_object.tracks)

    iter_list = header_list + list(mutable_object.children_if())

    for child in iter_list:
        if _safe_parent(child) is not None and _is_in(child.parent(), prune_list):
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
    root,
    reduce_fn,
    types_to_prune=None,
):
    """Filter a deep copy of root (and children) with ``reduce_fn``.

    The ``reduce_fn`` must have this signature:

    .. currentmodule:: _

    .. py:function:: func(previous_item: typing.Any, current: typing.Any, next_item: typing.Any) -> list[typing.Any]  # noqa
        :noindex:

    1. Make a deep copy of root
    2. Starting with root, perform a depth first traversal
    3. For each item (including root):

       a. if types_to_prune is not None and item is an instance of a type
          in types_to_prune, prune it from the copy, continue.
       b. Otherwise, pass (prev, copy, and next) to reduce_fn. If ``reduce_fn``:

          I.   returns an object: add it to the copy, replacing original
          II.  returns a tuple: insert it into the list, replacing original
          III. returns None: prune it

          .. note:: ``reduce_fn`` is always passed objects from the original
                    deep copy, not what prior calls return. See below for examples

    4. If an item is pruned, do not traverse its children
    5. Return the new deep copy.

    Example 1 (filter)::

        >>> track = [A,B,C]
        >>> def fn(prev_item, thing, next_item):
        ...     if prev_item.name == A:
        ...         return D # some new clip
        ...     else:
        ...         return thing
        >>> filtered_with_sequence_context(track, fn) => [A,D,C]

        order of calls to fn:
            fn(None, A, B) => A
            fn(A, B, C) => D
            fn(B, C, D) => C # !! note that it was passed B instead of D.

    Example 2 (prune)::

        >>> track = [A,B,C]
        >>> def fn(prev_item, thing, next_item):
        ...    if prev_item.name == A:
        ...        return None # prune the clip
        ...   else:
        ...        return thing
        >>> filtered_with_sequence_context(track, fn) => [A,C]

        order of calls to fn:
            fn(None, A, B) => A
            fn(A, B, C) => None
            fn(B, C, D) => C # !! note that it was passed B instead of D.

    Example 3 (expand)::

        >>> def fn(prev_item, thing, next_item):
        ...     if prev_item.name == A:
        ...         return (D, E) # tuple of new clips
        ...     else:
        ...         return thing
        >>> filtered_with_sequence_context(track, fn) => [A, D, E, C]

         the order of calls to fn will be:
            fn(None, A, B) => A
            fn(A, B, C) => (D, E)
            fn(B, C, D) => C # !! note that it was passed B instead of D.

    :param SerializableObjectWithMetadata root: Object to filter on
    :param reduce_fn: Filter function
    :param tuple(type) types_to_prune: Types to prune. Example: (otio.schema.Gap,...)
    """

    # deep copy everything
    mutable_object = copy.deepcopy(root)

    prune_list = set()

    header_list = [mutable_object]

    if isinstance(mutable_object, schema.Timeline):
        header_list.append(mutable_object.tracks)

    iter_list = header_list + list(mutable_object.children_if())

    # expand to include prev, next when appropriate
    expanded_iter_list = []
    for child in iter_list:
        if _safe_parent(child) and isinstance(child.parent(), schema.Track):
            prev_item, next_item = child.parent().neighbors_of(child)
            expanded_iter_list.append((prev_item, child, next_item))
        else:
            expanded_iter_list.append((None, child, None))

    def _safe_name(x):
        return x.name if x else "<NONE>"

    for prev_item, child, next_item in expanded_iter_list:
        if _safe_parent(child) is not None and _is_in(child.parent(), prune_list):
            prune_list.add(child)
            continue

        parent = None
        child_index = None
        if _safe_parent(child) is not None:
            child_index = child.parent().index(child)
            parent = child.parent()
            del child.parent()[child_index]

        # first try to prune
        if types_to_prune and _isinstance_in(child, types_to_prune):
            result = None
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
