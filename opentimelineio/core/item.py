"""
Item base class.  Things with range that ultimately point at media:
    - Composition (and children)
    - Clip
    - Filler
"""

from .. import (
    opentime,
    exceptions,
)

from . import serializeable_object


class Item(serializeable_object.SerializeableObject):
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

    name = serializeable_object.serializeable_field("name")
    source_range = serializeable_object.serializeable_field(
        "source_range",
        opentime.TimeRange
    )

    def duration(self):
        if self.source_range:
            return self.source_range.duration
        return self.computed_duration()

    def computed_duration(self):
        raise NotImplementedError

    def trimmed_range(self):
        if self.source_range:
            return self.source_range

        dur = self.duration()
        return opentime.TimeRange(opentime.RationalTime(0, dur.rate), dur)

    def is_parent_of(self, other):
        visited = set([])
        while other._parent is not None and other._parent not in visited:
            if other._parent is self:
                return True
            visited.add(other)
            other = other.parent

        return False

    def transformed_time(self, rt, reference_space):
        """
        Converts from rt in the coordinate system of self to the child or
        parent coordinate system of reference_space.

        Example:
        0                      20
        [------*----D----------]
        [--A--|*----B----|--C--]
             100 101    110
        101 in B = 6 in D

        * = rt argument
        """

        if self == reference_space or not reference_space:
            return rt

        if self.is_parent_of(reference_space):
            source_min = self.range_of_child(reference_space).start_time
            target_min = reference_space.trimmed_range().start_time
        elif reference_space.is_parent_of(self):
            source_min = self.trimmed_range().start_time
            target_min = reference_space.range_of_child(self).start_time
        else:
            raise exceptions.NotAChildError(
                "Neither {} nor {} is a child or parent of the other, "
                "cannot transform time.".format(self, reference_space)
            )

        return (rt - source_min) + target_min

    def transformed_time_range(self, tr, reference_space):
        return opentime.TimeRange(
            self.transformed_time(tr.start_time, reference_space),
            tr.duration
        )

    markers = serializeable_object.serializeable_field("markers")
    effects = serializeable_object.serializeable_field("effects")
    metadata = serializeable_object.serializeable_field("metadata")

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

    def set_parent(self, new_parent):
        if self._parent is not None and self in self._parent:
            self._parent.remove(self)

        self._parent = new_parent
