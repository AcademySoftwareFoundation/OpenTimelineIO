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

"""Implementation of the Item base class.  OTIO Objects that contain media."""

import copy

from .. import (
    opentime,
    exceptions,
)

from . import (
    serializable_object,
    composable,
    coordinate_space_reference,
    effect,
)


class spaces(object):
    InternalSpace = "ITEM_INTERNALSPACE"
    TrimmedSpace = "ITEM_TRIMMEDSPACE"
    EffectsSpace = "ITEM_EFFECTSSPACE"
    ExternalSpace = "ITEM_EXTERNALSPACE"
    """ @XXX: note that the order of this list goes from EXTERNAL to INTERNAL.

    The reason for this is that not all of the effects have transformations
    on time that are invertible (or 1-1).  For example, a rock and roll effect
    (or ping pong) will play a clip in one direction, then play the same frames
    backwards in time order.

    This means that looking from the frame up, it may not be possible to
    determine which frame of the global space is being played.  By making this
    list go in this order, the likely computable transform or mapping is
    emphasized rather than being inverted.
    """
    SPACE_ORDER = [ExternalSpace, EffectsSpace, TrimmedSpace, InternalSpace]

    @staticmethod
    def index(space):
        return spaces.SPACE_ORDER.index(space)


class Item(composable.Composable):
    """An Item is a Composable that can be part of a Composition or Timeline.

    More specifically, it is a Composable that has meaningful duration.

    Can also hold effects and markers.

    Base class of:
        - Composition (and children)
        - Clip
        - Gap
    """

    _serializable_label = "Item.1"
    _class_path = "core.Item"

    def __init__(
        self,
        name=None,
        source_range=None,
        effects=None,
        markers=None,
        metadata=None,
    ):
        super(Item, self).__init__(name=name, metadata=metadata)

        self.source_range = copy.deepcopy(source_range)
        self.effects = copy.deepcopy(effects) if effects else []
        self.markers = copy.deepcopy(markers) if markers else []

    name = serializable_object.serializable_field("name", doc="Item name.")
    source_range = serializable_object.serializable_field(
        "source_range",
        opentime.TimeRange,
        doc="Range of source to trim to.  Can be None or a TimeRange."
    )

    @staticmethod
    def visible():
        """Return the visibility of the Item. By default True."""

        return True

    def duration(self):
        """Convience wrapper for the trimmed_range.duration of the item."""

        return self.trimmed_range().duration

    def available_range(self):
        """Implemented by child classes, available range of media."""

        raise NotImplementedError

    def trimmed_range(self):
        """The range after applying the source range."""
        if self.source_range is not None:
            return copy.copy(self.source_range)

        return self.available_range()

    def visible_range(self):
        """The range of this item's media visible to its parent.
        Includes handles revealed by adjacent transitions (if any).
        This will always be larger or equal to trimmed_range()."""
        result = self.trimmed_range()
        if self.parent():
            head, tail = self.parent().handles_of_child(self)
            if head:
                result = opentime.TimeRange(
                    start_time=result.start_time - head,
                    duration=result.duration + head
                )
            if tail:
                result = opentime.TimeRange(
                    start_time=result.start_time,
                    duration=result.duration + tail
                )
        return result

    def trimmed_range_in_parent(self):
        """Find and return the trimmed range of this item in the parent."""
        if not self.parent():
            raise exceptions.NotAChildError(
                "No parent of {}, cannot compute range in parent.".format(self)
            )

        return self.parent().trimmed_range_of_child(self)

    def range_in_parent(self):
        """Find and return the untrimmed range of this item in the parent."""
        if not self.parent():
            raise exceptions.NotAChildError(
                "No parent of {}, cannot compute range in parent.".format(self)
            )

        return self.parent().range_of_child(self)

    def transformed_time(self, t, to_item):
        """Converts time t in the coordinate system of self to coordinate
        system of to_item.

        Note that self and to_item must be part of the same timeline (they must
        have a common ancestor).

        Example:

            0                      20
            [------t----D----------]
            [--A-][t----B---][--C--]
            100    101    110
            101 in B = 6 in D

        t = t argument
        """

        if not isinstance(t, opentime.RationalTime):
            raise ValueError(
                "transformed_time only operates on RationalTime, not {}".format(
                    type(t)
                )
            )

        # does not operate in place
        result = copy.copy(t)

        if to_item is None:
            return result

        root = self._root_parent()

        # transform t to root  parent's coordinate system
        item = self
        while item != root and item != to_item:

            parent = item.parent()
            result -= item.trimmed_range().start_time
            result += parent.range_of_child(item).start_time

            item = parent

        ancestor = item

        # transform from root parent's coordinate system to to_item
        item = to_item
        while item != root and item != ancestor:

            parent = item.parent()
            result += item.trimmed_range().start_time
            result -= parent.range_of_child(item).start_time

            item = parent

        assert(item is ancestor)

        return result

    def transformed_time_range(self, tr, to_item):
        """Transforms the timerange tr to the range of child or self to_item."""

        return opentime.TimeRange(
            self.transformed_time(tr.start_time, to_item),
            tr.duration
        )

    markers = serializable_object.serializable_field(
        "markers",
        doc="List of markers on this item."
    )
    effects = serializable_object.serializable_field(
        "effects",
        doc="List of effects on this item."
    )
    metadata = serializable_object.serializable_field(
        "metadata",
        doc="Metadata dictionary for this item."
    )

    # @{ Coordinate Spaces
    def internal_space(self):
        return coordinate_space_reference.CoordinateSpaceReference(
            self,
            spaces.InternalSpace
        )

    def _trimmed_to_internal(self):
        return opentime.TimeTransform(
            scale=1.0,
            offset=self.trimmed_range().start_time
        )

    def trimmed_space(self):
        return coordinate_space_reference.CoordinateSpaceReference(
            self,
            spaces.TrimmedSpace
        )

    def _trim(self, time_to_trim):
        if self.source_range is not None and not self.source_range.overlaps(
                time_to_trim
        ):
            return None
        return time_to_trim

    def _effects_to_trimmed(self):
        trimmed_to_effects_xform = opentime.TimeTransform()
        for ef in self.effects:
            if isinstance(ef, effect.TimeEffect):
                trimmed_to_effects_xform *= ef.time_transform()
        return trimmed_to_effects_xform

    def effects_space(self):
        return coordinate_space_reference.CoordinateSpaceReference(
            self,
            spaces.EffectsSpace
        )

    def _external_to_effects(self):
        return opentime.TimeTransform()

    def external_space(self):
        return coordinate_space_reference.CoordinateSpaceReference(
            self,
            spaces.ExternalSpace
        )

    def _transform_time(
            self,
            time_to_transform,
            from_space,
            to_space,
            trim=True
    ):
        """
        Transform time_to_transform from_space to to_space (only in this object)
        """
        if time_to_transform is None:
            return None

        if from_space == to_space:
            return time_to_transform

        if (
                from_space.source_object() is not self
                or to_space.source_object() is not self
        ):
            raise ValueError(
                "Error: can only translate from the same object.  Got:"
                " from_space: {} (id: {}) and to_space: {} (id: {}), "
                "self id: {}".format(
                    from_space.source_object(),
                    id(from_space.source_object()),
                    to_space.source_object(),
                    id(to_space.source_object()),
                    id(self)
                )
            )

        from_space_index = spaces.SPACE_ORDER.index(from_space.space)
        to_space_index = spaces.SPACE_ORDER.index(to_space.space)

        conversion_list = [
            # 2->3 or 3->2              2
            (self._external_to_effects, lambda _: _),
            # 1->2 or 2->1              1
            (self._effects_to_trimmed, lambda _:_),
            # 0->1 or 1->0              0
            (self._trimmed_to_internal, self._trim),
        ]

        start = from_space_index
        end = to_space_index
        reverse_search = to_space_index < from_space_index
        increment = 1
        if reverse_search:
            increment = -1
            # if searching from back to front, shift indices down one
            # to fit the conversion list
            start = from_space_index - 1
            end = to_space_index - 1

        # go one past the end
        while start != end:
            (converter, trimmer) = conversion_list[start]
            this_transform = converter()
            if reverse_search:
                this_transform = this_transform.inverted()
                if trim:
                    # source range is expressed in internal space, which is what
                    # trims the inputs
                    time_to_transform = trimmer(time_to_transform)
                if time_to_transform is None:
                    return None

            time_to_transform = this_transform * time_to_transform
            if trim and not reverse_search:
                # source range is expressed in internal space, which is what
                # trims the inputs
                time_to_transform = trimmer(time_to_transform)
            if time_to_transform is None:
                return None
            start += increment

        return time_to_transform
    # @}

    def __repr__(self):
        return (
            "otio.{}("
            "name={}, "
            "source_range={}, "
            "effects={}, "
            "markers={}, "
            "metadata={}"
            ")".format(
                self._class_path,
                repr(self.name),
                repr(self.source_range),
                repr(self.effects),
                repr(self.markers),
                repr(self.metadata)
            )
        )

    def __str__(self):
        return "{}({}, {}, {}, {}, {})".format(
            self._class_path.split('.')[-1],
            self.name,
            str(self.source_range),
            str(self.effects),
            str(self.markers),
            str(self.metadata)
        )
