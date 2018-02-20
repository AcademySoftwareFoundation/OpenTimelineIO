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
        metadata=None
    ):
        item.Item.__init__(
            self,
            name=name,
            source_range=source_range,
            metadata=metadata
        )
        collections.MutableSequence.__init__(self)

        self._children = []
        if children:
            # cannot simply set ._children to children since __setitem__ runs
            # extra logic (assigning ._parent pointers).
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

    def each_child(
        self,
        search_range=None,
        descended_from_type=composable.Composable
    ):
        for i, child in enumerate(self._children):
            # filter out children who are not in the search range
            if (
                search_range
                and not self.range_of_child_at_index(i).overlaps(search_range)
            ):
                continue

            # filter out children who are not descended from the specified type
            if (
                descended_from_type == composable.Composable
                or isinstance(child, descended_from_type)
            ):
                yield child

            # for children that are compositions, recurse into their children
            if hasattr(child, "each_child"):
                for valid_child in (
                    c for c in child.each_child(
                        search_range,
                        descended_from_type
                    )
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
                current = current._parent
            except AttributeError:
                raise exceptions.NotAChildError(
                    "Item '{}' is not a child of '{}'.".format(child, self)
                )

            parents.append(current)

        return parents

    def index_of_child(self, child):
        """Returns the index of the given child object within this Composition.
        Unlike index() this method checks for the exact child object, not
        objects that are equal to the given child.

        If the child is not found, a NotAChildError is thrown. If multiple
        instances of the child are found, an InstancingNotAllowedError is
        thrown."""
        indexes = [i for i, c in enumerate(self) if c is child]
        if len(indexes) == 0:
            raise exceptions.NotAChildError(
                "Item '{}' is not a child of '{}'.".format(child, self)
            )
        if len(indexes) > 1:
            raise exceptions.InstancingNotAllowedError(
                "Item '{}' is used multiple times as child of '{}'.".format(
                    child,
                    self
                )
            )
        return indexes[0]

    def range_of_child(self, child, reference_space=None):
        """The range of the child in relation to another item
        (reference_space), not trimmed based on this
        composition's source_range.

        Note that reference_space must be in the same timeline as self.

        For example,

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
            index = parent.index_of_child(current)
            parent_range = parent.range_of_child_at_index(index)

            if not result_range:
                result_range = parent_range
                current = parent
                continue

            result_range.start_time = (
                result_range.start_time
                + parent_range.start_time
            )
            current = parent

        if reference_space is not self:
            result_range = self.transformed_time_range(
                result_range,
                reference_space
            )

        return result_range

    def children_at_time(self, t):
        """ Which children overlap time t? """

        result = []
        for index, child in enumerate(self):
            if self.range_of_child_at_index(index).contains(t):
                result.append(child)

        return result

    def top_clip_at_time(self, t):
        """Return the first visible child that overlaps with time t."""

        for child in self.children_at_time(t):
            if hasattr(child, "top_clip_at_time"):
                return child.top_clip_at_time(self.transformed_time(t, child))
            elif not child.visible():
                continue
            else:
                return child

        return None

    def handles_of_child(self, child):
        """If media beyond the ends of this child are visible due to adjacent
        Transitions (only applicable in a Track) then this will return the
        head and tail offsets as a tuple of RationalTime objects. If no handles
        are present on either side, then None is returned instead of a
        RationalTime.

        Example usage:
        head, tail = track.handles_of_child(clip)
        if head:
          ...
        if tail:
          ...
        """
        return (None, None)

    def trimmed_range_of_child(self, child, reference_space=None):
        """ Return range of the child in reference_space coordinates, after the
        self.source_range is applied.

        For example,

        |     [-----]     | seq
        [-----------------] Clip A

        If ClipA has duration 17, and seq has source_range: 5, duration 10,
        seq.trimmed_range_of_child(Clip A) will return (5, 10)
        Which is trimming the range according to the source_range of seq.

        To get the range of the child without the source_range applied, use the
        range_of_child() method.

        Another example:
        |  [-----]   | seq source range starts on frame 4 and goes to frame 8
        [ClipA][ClipB] (each 6 frames long)

        seq.range_of_child(CLipA):
            0, duration 6
        seq.trimmed_range_of_child(ClipA):
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
            index = parent.index_of_child(current)
            parent_range = parent.trimmed_range_of_child_at_index(index)

            if not result_range:
                result_range = parent_range
                current = parent
                continue

            result_range.start_time = (
                result_range.start_time
                + parent_range.start_time
            )
            current = parent

        if not self.source_range:
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
        if (
            self.source_range.start_time >= child_range.end_time_exclusive()
            or self.source_range.end_time_exclusive() <= child_range.start_time
        ):
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
    def update(self, d):
        """Like the dictionary .update() method.

        Update the data dictionary of this SerializableObject with the .data
        of d if d is a SerializableObject or if d is a dictionary, d itself.
        """

        # use the parent update function
        super(Composition, self).update(d)

        # ...except for the 'children' field, which needs to run through the
        # insert method so that _parent pointers are correctly set on children.
        self._children = []
        self.extend(d.get('children', []))
    # @}

    # @{ collections.MutableSequence implementation
    def __getitem__(self, item):
        return self._children[item]

    def __setitem__(self, key, value):
        old = self._children[key]
        if old is value:
            return

        # unset the old child's parent
        if old is not None:
            if isinstance(key, slice):
                for val in old:
                    val._set_parent(None)
            else:
                old._set_parent(None)

        # put it into our list of children
        self._children[key] = value

        # set the new parent
        if value is not None:
            if isinstance(key, slice):
                for val in value:
                    val._set_parent(self)
            else:
                value._set_parent(self)

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

        item._set_parent(self)
        self._children.insert(index, item)

    def __len__(self):
        """The len() of a Composition is the # of children in it.
        Note that this also means that a Composition with no children
        is considered False, so take care to test for "if foo is not None"
        versus just "if foo" when the difference matters."""
        return len(self._children)

    def __delitem__(self, key):
        # grab the old value
        old = self._children[key]

        # remove it from our list of children
        del self._children[key]

        # unset the old value's parent
        if old is not None:
            if isinstance(key, slice):
                for val in old:
                    val._set_parent(None)
            else:
                old._set_parent(None)
    # @}
