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

    def visible(self):
        return True

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
        # if not isinstance(other, Item):
        #     raise TypeError("Parameter must be an Item, not {}".format(type(other)))
        visited = set([])
        while other._parent is not None and other._parent not in visited:
            if other._parent is self:
                return True
            visited.add(other)
            other = other._parent
            # if not isinstance(other, Item):
            #     raise TypeError("Invalid parent must be an Item, not {}".format(other))

        return False

    def _root_parent(self):
        return ([self] + self._ancestors())[-1]

    def _ancestors(self):
        ancestors = []
        item = self
        while item._parent != None:
            item = item._parent
            ancestors.append(item)
        return ancestors
        
    def _common_ancestor(self, other):
        mine = self._ancestors()
        theirs = other._ancestors()

        for my_parent, their_parent in zip(mine, theirs):
            if my_parent != their_parent:
                return my_parent

        return None

    def transformed_time(self, t, to_item):
        """
        Converts time t in the coordinate system of self to coordinate system of to_item.
        Note that self and to_item must be part of the same timeline (they must have a common ancestor).

        Example:
        0                      20
        [------*----D----------]
        [--A--|*----B----|--C--]
             100 101    110
        101 in B = 6 in D

        * = t argument
        """

        if to_item is None:
            to_item = self

        root = self._root_parent()
        
        # lets transform t to our parent's coordinate system, repeatedly until we get to the root
        item = self
        while item != root and item != to_item:
            
            parent = item._parent
            t -= item.trimmed_range().start_time
            t += parent.range_of_child(item).start_time
            
            item = parent
        
        ancestor = item
        
        # now lets walk down to the to_item
        item = to_item
        while item != root and item != ancestor:
            
            parent = item._parent
            t += item.trimmed_range().start_time
            t -= parent.range_of_child(item).start_time
            
            item = parent
        
        assert(item == ancestor)
        
        return t

        # if self == to_item or not to_item:
        #     return t
        #
        # # if not isinstance(to_item, Item):
        # #     raise TypeError("Reference space must be an Item, not {}".format(type(to_item)))
        #
        # if self.is_parent_of(to_item):
        #     source_min = self.range_of_child(to_item).start_time
        #     target_min = to_item.trimmed_range().start_time
        # elif to_item.is_parent_of(self):
        #     source_min = self.trimmed_range().start_time
        #     target_min = to_item.range_of_child(self).start_time
        # else:
        #     raise exceptions.NotAChildError(
        #         "Neither {} nor {} is a child or parent of the other, "
        #         "cannot transform time.".format(self, to_item)
        #     )
        #
        # return (t - source_min) + target_min

    def transformed_time_range(self, tr, to_item):
        return opentime.TimeRange(
            self.transformed_time(tr.start_time, to_item),
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

    def parent(self):
        return self._parent

    def _set_parent(self, new_parent):
        if self._parent is not None and (
            hasattr(self._parent, "remove") and 
            self in self._parent
        ):
            self._parent.remove(self)

        self._parent = new_parent
