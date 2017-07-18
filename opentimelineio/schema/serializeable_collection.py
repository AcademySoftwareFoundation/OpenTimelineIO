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

__doc__ = """
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
