"""
A serializeable collection of SerializeableObjects.
"""

import collections

from .. import (
    core
)


@core.register_type
class SerializeableCollection(
    core.SerializeableObject,
    collections.MutableSequence
):
    """
    A special kind of composition which can hold any serializeable object.
     
    This composition approximates the concept of a `bin` - a collection of 
    SerializeableObjects that do not have any compositing meaning, but can
    serialize to/from OTIO correctly, with metadata and a named collection.
    """

    _serializeable_label = "SerializeableCollection.1"
    _class_path = "schema.SerializeableCollection"

    def __init__(
        self,
        name=None,
        children=None,
        metadata=None,
    ):
        core.SerializeableObject.__init__(self)

        self.name = name
        self._children = []
        if children:
            self._children = children
        self.metadata = metadata

    name = core.serializeable_field(
        "name",
        str,
        doc="SerializeableCollection name."
    )
    _children = core.serializeable_field(
        "children", 
        list,
        "SerializeableObject contained by this container."
    )
    metadata = core.serializeable_field(
        "metadata",
        dict,
        doc="Metadata dictionary for this SerializeableCollection."
    )


    # @{ Stringification
    def __str__(self):
        return "SerializeableCollection({}, {}, {})".format(
            str(self.name),
            str(self._children),
            str(self.metadata)
        )

    def __repr__(self):
        return (
            "otio.{}("
            "name={}, "
            "children={}, "
            "metadata={}"
            ")".format(
                self._class_path,
                repr(self.name),
                repr(self._children),
                repr(self.metadata)
            )
        )
    # @}

    # @{ collections.MutableSequence implementation
    def __getitem__(self, item):
        return self._children[item]

    def __setitem__(self, key, value):
        self._children[key] = value

    def insert(self, index, item):
        self._children.insert(index, item)

    def __len__(self):
        return len(self._children)

    def __delitem__(self, item):
        del self._children[item]
    # @}
