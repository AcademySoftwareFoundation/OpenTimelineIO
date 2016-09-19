"""
Composition Stack/Sequence Implementation
"""

import collections
import itertools

from .. import (
    opentime,
)

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
        transform=None,
        metadata=None
    ):
        item.Item.__init__(
            self,
            name=name,
            source_range=source_range,
            metadata=metadata
        )
        collections.MutableSequence.__init__(self)

        if children is None:
            self.children = []
        else:
            self.children = children

        self.transform = transform

    children = serializeable_object.serializeable_field("children")

    @property
    def composition_kind(self):
        return self._composition_kind

    def __str__(self):
        return "{}({}, {}, {}, {}, {})".format(
            self._composition_kind,
            str(self.name),
            str(self.children),
            str(self.source_range),
            str(self.transform),
            str(self.metadata)
        )

    def __repr__(self):
        return (
            "otio.{}.{}("
            "name={}, "
            "children={}, "
            "source_range={}, "
            "transform={}, "
            "metadata={}"
            ")".format(
                self._modname,
                self._composition_kind,
                repr(self.name),
                repr(self.children),
                repr(self.source_range),
                repr(self.transform),
                repr(self.metadata)
            )
        )

    transform = serializeable_object.serializeable_field(
        "transform",
        opentime.TimeTransform
    )

    def each_clip(self, search_range=None):
        if search_range is not None and self.transform is not None:
            search_range = self.transform.applied_to(search_range)
        return itertools.chain.from_iterable(
            (
                c.each_clip(search_range) for i, c in enumerate(self.children)
                if search_range is None or (
                    self.range_of_child_at_index(i).overlaps(search_range)
                )
            )
        )

    def range_of_child_at_index(self, index):
        raise NotImplementedError

    # @{ collections.MutableSequence implementation
    def __getitem__(self, item):
        return self.children[item]

    def __setitem__(self, key, value):
        self.children[key] = value

    def insert(self, key, value):
        self.children.insert(key, value)

    def __len__(self):
        return len(self.children)

    def __delitem__(self, item):
        del self.children[item]
    # @}
