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

"""A serializable collection of SerializableObjects."""

import collections

from .. import (
    core
)


@core.register_type
class SerializableCollection(
    core.SerializableObject,
    collections.MutableSequence
):
    """A kind of composition which can hold any serializable object.

    This composition approximates the concept of a `bin` - a collection of
    SerializableObjects that do not have any compositing meaning, but can
    serialize to/from OTIO correctly, with metadata and a named collection.
    """

    _serializable_label = "SerializableCollection.1"
    _class_path = "schema.SerializableCollection"

    def __init__(
        self,
        name=None,
        children=None,
        metadata=None,
    ):
        core.SerializableObject.__init__(self)

        self.name = name
        self._children = []
        if children:
            self._children = children
        self.metadata = metadata

    name = core.serializable_field(
        "name",
        str,
        doc="SerializableCollection name."
    )
    _children = core.serializable_field(
        "children",
        list,
        "SerializableObject contained by this container."
    )
    metadata = core.serializable_field(
        "metadata",
        dict,
        doc="Metadata dictionary for this SerializableCollection."
    )

    # @{ Stringification
    def __str__(self):
        return "SerializableCollection({}, {}, {})".format(
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

# the original name for "SerializableCollection" was "SerializeableCollection" -
# this will turn this misspelling found in OTIO files into the correct instance automatically.
core.register_type(SerializableCollection, 'SerializeableCollection')
