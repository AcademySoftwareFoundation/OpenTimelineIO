#
# Copyright 2017 Pixar Animation Studios
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

"""Composition base class.  An object that contains `Items`."""

import collections

from . import (
    serializable_object,
    type_registry,
    item,
    composable,
)

from .. import (
    opentime,
    exceptions
)


def _bisect_right(
        seq,
        tgt,
        key_func,
        lower_search_bound=0,
        upper_search_bound=None
):
    """Return the index of the last item in seq such that all e in seq[:index]
    have key_func(e) <= tgt, and all e in seq[index:] have key_func(e) > tgt.

    Thus, seq.insert(index, value) will insert value after the rightmost item
    such that meets the above condition.

    lower_search_bound and upper_search_bound bound the slice to be searched.

    Assumes that seq is already sorted.
    """

    if lower_search_bound < 0:
        raise ValueError('lower_search_bound must be non-negative')

    if upper_search_bound is None:
        upper_search_bound = len(seq)

    while lower_search_bound < upper_search_bound:
        midpoint_index = (lower_search_bound + upper_search_bound) // 2

        if tgt < key_func(seq[midpoint_index]):
            upper_search_bound = midpoint_index
        else:
            lower_search_bound = midpoint_index + 1

    return lower_search_bound


def _bisect_left(
        seq,
        tgt,
        key_func,
        lower_search_bound=0,
        upper_search_bound=None
):
    """Return the index of the last item in seq such that all e in seq[:index]
    have key_func(e) < tgt, and all e in seq[index:] have key_func(e) >= tgt.

    Thus, seq.insert(index, value) will insert value before the leftmost item
    such that meets the above condition.

    lower_search_bound and upper_search_bound bound the slice to be searched.

    Assumes that seq is already sorted.
    """

    if lower_search_bound < 0:
        raise ValueError('lower_search_bound must be non-negative')

    if upper_search_bound is None:
        upper_search_bound = len(seq)

    while lower_search_bound < upper_search_bound:
        midpoint_index = (lower_search_bound + upper_search_bound) // 2

        if key_func(seq[midpoint_index]) < tgt:
            lower_search_bound = midpoint_index + 1
        else:
            upper_search_bound = midpoint_index

    return lower_search_bound


@type_registry.register_type
class Composition(item.Item, collections.MutableSequence):
    """Base class for an OTIO Item that contains other Items.

    Should be subclassed (for example by Track and Stack), not used
    directly.
    """

    _serializable_label = "Composition.1"
    _composition_kind = "Composition"
    _modname = "core"
    _composable_base_class = composable.Composable

    def __init__(
        self,
        name=None,
        children=None,
        source_range=None,
        markers=None,
        effects=None,
        metadata=None
    ):
        item.Item.__init__(
            self,
            name=name,
            source_range=source_range,
            markers=markers,
            effects=effects,
            metadata=metadata
        )
        collections.MutableSequence.__init__(self)

        # Because we know that all children are unique, we store a set
        # of all the children as well to speed up __contain__ checks.
        self._child_lookup = set()

        self._children = []
        if children:
            # cannot simply set ._children to children since __setitem__ runs
            # extra logic (assigning ._parent pointers) and populates the
            # internal membership set _child_lookup.
            self.extend(children)

    _children = serializable_object.serializable_field(
        "children",
        list,
        "Items contained by this composition."
    )

    @property
    def composition_kind(self):
        """Returns a label specifying the kind of composition."""

        return self._composition_kind

    def __str__(self):
        return "{}({}, {}, {}, {})".format(
            self._composition_kind,
            str(self.name),
            str(self._children),
            str(self.source_range),
            str(self.metadata)
        )

    def __repr__(self):
        return (
            "otio.{}.{}("
            "name={}, "
            "children={}, "
            "source_range={}, "
            "metadata={}"
            ")".format(
                self._modname,
                self._composition_kind,
                repr(self.name),
                repr(self._children),
                repr(self.source_range),
                repr(self.metadata)
            )
        )

    transform = serializable_object.deprecated_field()

    def child_at_time(
            self,
            search_time,
            shallow_search=False,
    ):
        """Return the child that overlaps with time search_time.

        search_time is in the space of self.

        If shallow_search is false, will recurse into compositions.
        """

        range_map = self.range_of_all_children()

        # find the first item whose end_time_exclusive is after the
        first_inside_range = _bisect_left(
            seq=self._children,
            tgt=search_time,
            key_func=lambda child: range_map[child].end_time_exclusive(),
        )

        # find the last item whose start_time is before the
        last_in_range = _bisect_right(
            seq=self._children,
            tgt=search_time,
            key_func=lambda child: range_map[child].start_time,
            lower_search_bound=first_inside_range,
        )

        # limit the search to children who are in the search_range
        possible_matches = self._children[first_inside_range:last_in_range]

        result = None
        for thing in possible_matches:
            if range_map[thing].overlaps(search_time):
                result = thing
                break

        # if the search cannot or should not continue
        if (
                result is None
                or shallow_search
                or not hasattr(result, "child_at_time")
        ):
            return result

        # before you recurse, you have to transform the time into the
        # space of the child
        child_search_time = self.transformed_time(search_time, result)

        return result.child_at_time(child_search_time, shallow_search)

    def each_child(
            self,
            search_range=None,
            descended_from_type=composable.Composable,
            shallow_search=False,
    ):
        """ Generator that returns each child contained in the composition in
        the order in which it is found.

        Arguments:
            search_range: if specified, only children whose range overlaps with
                          the search range will be yielded.
            descended_from_type: if specified, only children who are a
                          descendent of the descended_from_type will be yielded.
            shallow_search: if True, will only search children of self, not
                            and not recurse into children of children.
        """
        if search_range:
            range_map = self.range_of_all_children()

            # find the first item whose end_time_inclusive is after the
            # start_time of the search range
            first_inside_range = _bisect_left(
                seq=self._children,
                tgt=search_range.start_time,
                key_func=lambda child: range_map[child].end_time_inclusive(),
            )

            # find the last item whose start_time is before the
            # end_time_inclusive of the search_range
            last_in_range = _bisect_right(
                seq=self._children,
                tgt=search_range.end_time_inclusive(),
                key_func=lambda child: range_map[child].start_time,
                lower_search_bound=first_inside_range,
            )

            # limit the search to children who are in the search_range
            children = self._children[first_inside_range:last_in_range]
        else:
            # otherwise search all the children
            children = self._children

        for child in children:
            # filter out children who are not descended from the specified type
            # shortcut the isinstance if descended_from_type is composable
            # (since all objects in compositions are already composables)
            is_descendant = descended_from_type == composable.Composable
            if is_descendant or isinstance(child, descended_from_type):
                yield child

            # if not a shallow_search, for children that are compositions,
            # recurse into their children
            if not shallow_search and hasattr(child, "each_child"):

                if search_range is not None:
                    search_range = self.transformed_time_range(search_range, child)

                for valid_child in child.each_child(
                        search_range,
                        descended_from_type,
                        shallow_search
                ):
                    yield valid_child

    def range_of_child_at_index(self, index):
        """Return the range of a child item in the time range of this
        composition.

        For example, with a track:
            [ClipA][ClipB][ClipC]

        The self.range_of_child_at_index(2) will return:
            TimeRange(ClipA.duration + ClipB.duration, ClipC.duration)

        To be implemented by subclass of Composition.
        """

        raise NotImplementedError

    def trimmed_range_of_child_at_index(self, index):
        """Return the trimmed range of the child item at index in the time
        range of this composition.

        For example, with a track:

                       [     ]

            [ClipA][ClipB][ClipC]

        The range of index 2 (ClipC) will be just like
        range_of_child_at_index() but trimmed based on this Composition's
        source_range.

        To be implemented by child.
        """

        raise NotImplementedError

    def range_of_all_children(self):
        """Return a dict mapping children to their range in this object."""

        raise NotImplementedError

    def __copy__(self):
        result = super(Composition, self).__copy__()

        # Children are *not* copied with a shallow copy since the meaning is
        # ambiguous - they have a parent pointer which would need to be flipped
        # or they would need to be copied, which implies a deepcopy().
        #
        # This follows from the python documentation on copy/deepcopy:
        # https://docs.python.org/2/library/copy.html
        #
        # """
        # - A shallow copy constructs a new compound object and then (to the
        #   extent possible) inserts references into it to the objects found in
        #   the original.
        # - A deep copy constructs a new compound object and then, recursively,
        #   inserts copies into it of the objects found in the original.
        # """
        result._children = []

        return result

    def __deepcopy__(self, md):
        result = super(Composition, self).__deepcopy__(md)

        # deepcopy should have already copied the children, so only parent
        # pointers need to be updated.
        [c._set_parent(result) for c in result._children]

        # we also need to reconstruct the membership set of _child_lookup.
        result._child_lookup.update(result._children)

        return result

    def _path_to_child(self, child):
        if not isinstance(child, composable.Composable):
            raise TypeError(
                "An object child of 'Composable' is required,"
                " not type '{}'".format(
                    type(child)
                )
            )

        current = child
        parents = []

        while(current is not self):
            try:
                current = current.parent()
            except AttributeError:
                raise exceptions.NotAChildError(
                    "Item '{}' is not a child of '{}'.".format(child, self)
                )

            parents.append(current)

        return parents

    def range_of_child(self, child, reference_space=None):
        """The range of the child in relation to another item
        (reference_space), not trimmed based on this
        composition's source_range.

        Note that reference_space must be in the same timeline as self.

        For example:

            |     [-----]     | seq

            [-----------------] Clip A

        If ClipA has duration 17, and seq has source_range: 5, duration 15,
        seq.range_of_child(Clip A) will return (0, 17)
        ignoring the source range of seq.

        To get the range of the child with the source_range applied, use the
        trimmed_range_of_child() method.
        """

        if not reference_space:
            reference_space = self

        parents = self._path_to_child(child)

        current = child
        result_range = None

        for parent in parents:
            index = parent.index(current)
            parent_range = parent.range_of_child_at_index(index)

            if not result_range:
                result_range = parent_range
                current = parent
                continue

            result_range = opentime.TimeRange(
                start_time=result_range.start_time + parent_range.start_time,
                duration=result_range.duration
            )
            current = parent

        if reference_space is not self:
            result_range = self.transformed_time_range(
                result_range,
                reference_space
            )

        return result_range

    def handles_of_child(self, child):
        """If media beyond the ends of this child are visible due to adjacent
        Transitions (only applicable in a Track) then this will return the
        head and tail offsets as a tuple of RationalTime objects. If no handles
        are present on either side, then None is returned instead of a
        RationalTime.

        Example usage:
        >>> head, tail = track.handles_of_child(clip)
        >>> if head:
        ...     print('Do something')
        >>> if tail:
        ...     print('Do something else')
        """
        return (None, None)

    def trimmed_range_of_child(self, child, reference_space=None):
        """Get range of the child in reference_space coordinates, after the
        self.source_range is applied.

        Example
        |     [-----]     | seq
        [-----------------] Clip A

        If ClipA has duration 17, and seq has source_range: 5, duration 10,
        seq.trimmed_range_of_child(Clip A) will return (5, 10)
        Which is trimming the range according to the source_range of seq.

        To get the range of the child without the source_range applied, use the
        range_of_child() method.

        Another example
        |  [-----]   | seq source range starts on frame 4 and goes to frame 8
        [ClipA][ClipB] (each 6 frames long)

        >>> seq.range_of_child(CLipA)
        0, duration 6
        >>> seq.trimmed_range_of_child(ClipA):
        4, duration 2
        """

        if not reference_space:
            reference_space = self

        if not reference_space == self:
            raise NotImplementedError

        parents = self._path_to_child(child)

        current = child
        result_range = None

        for parent in parents:
            index = parent.index(current)
            parent_range = parent.trimmed_range_of_child_at_index(index)

            if not result_range:
                result_range = parent_range
                current = parent
                continue

            result_range.start_time += parent_range.start_time
            current = parent

        if not self.source_range or not result_range:
            return result_range

        new_start_time = max(
            self.source_range.start_time,
            result_range.start_time
        )

        # trimmed out
        if new_start_time >= result_range.end_time_exclusive():
            return None

        # compute duration
        new_duration = min(
            result_range.end_time_exclusive(),
            self.source_range.end_time_exclusive()
        ) - new_start_time

        if new_duration.value < 0:
            return None

        return opentime.TimeRange(new_start_time, new_duration)

    def trim_child_range(self, child_range):
        if not self.source_range:
            return child_range

        # cropped out entirely
        past_end_time = self.source_range.start_time >= child_range.end_time_exclusive()
        before_start_time = \
            self.source_range.end_time_exclusive() <= child_range.start_time

        if past_end_time or before_start_time:
            return None

        if child_range.start_time < self.source_range.start_time:
            child_range = opentime.range_from_start_end_time(
                self.source_range.start_time,
                child_range.end_time_exclusive()
            )

        if (
            child_range.end_time_exclusive() >
            self.source_range.end_time_exclusive()
        ):
            child_range = opentime.range_from_start_end_time(
                child_range.start_time,
                self.source_range.end_time_exclusive()
            )

        return child_range

    # @{ SerializableObject override.
    def _update(self, d):
        """Like the dictionary .update() method.

        Update the data dictionary of this SerializableObject with the .data
        of d if d is a SerializableObject or if d is a dictionary, d itself.
        """

        # use the parent update function
        super(Composition, self)._update(d)

        # ...except for the 'children' field, which needs to run through the
        # insert method so that _parent pointers are correctly set on children.
        self._children = []
        self.extend(d.get('children', []))
    # @}

    # @{ collections.MutableSequence implementation
    def __getitem__(self, item):
        return self._children[item]

    def _setitem_slice(self, key, value):
        set_value = set(value)

        # check if any members in the new slice are repeated
        if len(set_value) != len(value):
            raise ValueError(
                "Instancing not allowed in Compositions, {} contains repeated"
                " items.".format(value)
            )

        old = self._children[key]
        if old:
            set_old = set(old)
            set_outside_old = set(self._children).difference(set_old)

            isect = set_outside_old.intersection(set_value)
            if isect:
                raise ValueError(
                    "Attempting to insert duplicates of items {} already "
                    "present in container, instancing not allowed in "
                    "Compositions".format(isect)
                )

            # update old parent
            for val in old:
                val._set_parent(None)
                self._child_lookup.remove(val)

        # insert into _children
        self._children[key] = value

        # update new parent
        if value:
            for val in value:
                val._set_parent(self)
                self._child_lookup.add(val)

    def __setitem__(self, key, value):
        # fetch the current thing at that index/slice
        old = self._children[key]

        # in the case of key being a slice, old and value are both sequences
        if old is value:
            return

        if isinstance(key, slice):
            return self._setitem_slice(key, value)

        if value in self:
            raise ValueError(
                "Composable {} already present in this container, instancing"
                " not allowed in otio compositions.".format(value)
            )

        # unset the old child's parent and delete the membership entry.
        if old is not None:
            old._set_parent(None)
            self._child_lookup.remove(old)

        # put it into our list of children
        self._children[key] = value

        # set the new parent
        if value is not None:
            value._set_parent(self)

            # put it into our membership tracking set
            self._child_lookup.add(value)

    def insert(self, index, item):
        """Insert an item into the composition at location `index`."""

        if not isinstance(item, self._composable_base_class):
            raise TypeError(
                "Not allowed to insert an object of type {0} into a {1}, only"
                " objects descending from {2}. Tried to insert: {3}".format(
                    type(item),
                    type(self),
                    self._composable_base_class,
                    str(item)
                )
            )

        if item in self:
            raise ValueError(
                "Composable {} already present in this container, instancing"
                " not allowed in otio compositions.".format(item)
            )

        # set the item's parent and add it to our membership tracking and list
        # of children
        item._set_parent(self)
        self._child_lookup.add(item)
        self._children.insert(index, item)

    def __contains__(self, item):
        """Use our internal membership tracking set to speed up searches."""
        return item in self._child_lookup

    def __len__(self):
        """The len() of a Composition is the # of children in it.
        Note that this also means that a Composition with no children
        is considered False, so take care to test for "if foo is not None"
        versus just "if foo" when the difference matters."""
        return len(self._children)

    def __delitem__(self, key):
        # grab the old value
        old = self._children[key]

        # remove it from the membership tracking set and clear parent
        if old is not None:
            if isinstance(key, slice):
                for val in old:
                    self._child_lookup.remove(val)
                    val._set_parent(None)
            else:
                self._child_lookup.remove(old)
                old._set_parent(None)

        # remove it from our list of children
        del self._children[key]
