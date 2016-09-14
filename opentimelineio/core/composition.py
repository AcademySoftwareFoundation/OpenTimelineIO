"""
Composition Stack/Sequence Implementation
"""

import collections
import itertools

from . import (
    serializeable_object,
    type_registry,
    item
)


@type_registry.register_type
class Composition(item.Item, collections.MutableSequence):
    _serializeable_label = "Composition.1"
    _composition_kind = "Composition"
    _modname = "core"

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
            # need to assign the parent points, so it has to run through 
            # __setitem__
            self.extend(children)

    _children = serializeable_object.serializeable_field("children", list)

    @property
    def composition_kind(self):
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

    transform = serializeable_object.deprecated_field()

    def each_clip(self, search_range=None):
        return itertools.chain.from_iterable(
            (
                c.each_clip(search_range) for i, c in enumerate(self._children)
                if search_range is None or (
                    self.range_of_child_at_index(i).overlaps(search_range)
                )
            )
        )

    def range_of_child_at_index(self, index):
        raise NotImplementedError

    def _set_self_as_parent_of(self, value):
        if value._parent is not None:
            value._parent._children.remove(value)
        
        value._parent = self

    # @{ collections.MutableSequence implementation
    def __getitem__(self, item):
        return self._children[item]

    def __setitem__(self, key, value):
        self._set_self_as_parent_of(value)
        self._children[key] = value

    def insert(self, key, value):
        self._set_self_as_parent_of(value)
        self._children.insert(key, value)

    def __len__(self):
        return len(self._children)

    def __delitem__(self, item):
        item._parent = None
        del self._children[item]
    # @}
