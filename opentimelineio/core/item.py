"""Implementation of the Item base class.  OTIO Objects that contain media."""

from .. import (
    opentime,
)

from . import serializeable_object


class Item(serializeable_object.SerializeableObject):
    """Item base class.  Things with range that ultimately point at media:
        - Composition (and children)
        - Clip
        - Filler
    """

    _serializeable_label = "Item.1"
    _class_path = "core.Item"

    def __init__(
        self,
        name=None,
        source_range=None,
        effects=None,
        markers=None,
        metadata=None,
    ):
        serializeable_object.SerializeableObject.__init__(self)

        self.name = name
        self.source_range = source_range

        if effects is None:
            effects = []
        self.effects = effects

        if markers is None:
            markers = []
        self.markers = markers

        if metadata is None:
            metadata = {}
        self.metadata = metadata

        self._parent = None

    name = serializeable_object.serializeable_field("name", doc="Item name.")
    source_range = serializeable_object.serializeable_field(
        "source_range",
        opentime.TimeRange,
        doc="Range of source to trim to.  Can be None or a TimeRange."
    )

    @staticmethod
    def visible():
        """Return the visibility of the Item. By default True."""

        return True

    def duration(self):
        """The duration of the Item."""

        if self.source_range:
            return self.source_range.duration
        return self.computed_duration()

    def computed_duration(self):
        """Implemented by child classes, computes the duration of the Item."""

        raise NotImplementedError

    def trimmed_range(self):
        """The range after applying the source range."""

        if self.source_range:
            return self.source_range

        dur = self.duration()
        return opentime.TimeRange(opentime.RationalTime(0, dur.rate), dur)

    def is_parent_of(self, other):
        """Returns true if self is a parent of other."""

        visited = set([])
        while other._parent is not None and other._parent not in visited:
            if other._parent is self:
                return True
            visited.add(other)
            other = other._parent

        return False

    def _root_parent(self):
        return ([self] + self._ancestors())[-1]

    def _ancestors(self):
        ancestors = []
        item = self
        while item._parent is not None:
            item = item._parent
            ancestors.append(item)
        return ancestors

    def transformed_time(self, t, to_item):
        """Converts time t in the coordinate system of self to coordinate 
        system of to_item.

        Note that self and to_item must be part of the same timeline (they must
        have a common ancestor).

        Example:
        0                      20
        [------*----D----------]
        [--A--|*----B----|--C--]
             100 101    110
        101 in B = 6 in D

        * = t argument
        """

        # does not operate in place
        import copy
        result = copy.copy(t)

        if to_item is None:
            return result

        root = self._root_parent()

        # transform t to root  parent's coordinate system
        item = self
        while item != root and item != to_item:

            parent = item._parent
            result -= item.trimmed_range().start_time
            result += parent.range_of_child(item).start_time

            item = parent

        ancestor = item

        # transform from root parent's coordinate system to to_item
        item = to_item
        while item != root and item != ancestor:

            parent = item._parent
            result += item.trimmed_range().start_time
            result -= parent.range_of_child(item).start_time

            item = parent

        assert(item == ancestor)

        return result

    def transformed_time_range(self, tr, to_item):
        """Transforms the timerange tr to the range of child or self to_item.

        """

        return opentime.TimeRange(
            self.transformed_time(tr.start_time, to_item),
            tr.duration
        )

    markers = serializeable_object.serializeable_field(
        "markers",
        doc="List of markers on this item."
    )
    effects = serializeable_object.serializeable_field(
        "effects",
        doc="List of effects on this item."
    )
    metadata = serializeable_object.serializeable_field(
        "metadata",
        doc="Metadata dictionary for this item."
    )

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

    def parent(self):
        """Return the parent pointer."""

        return self._parent

    def _set_parent(self, new_parent):
        if self._parent is not None and (
            hasattr(self._parent, "remove") and
            self in self._parent
        ):
            self._parent.remove(self)

        self._parent = new_parent
