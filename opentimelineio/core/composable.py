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

"""Composable class definition.

An object that can be composed by tracks.
"""

import weakref

from . import serializable_object
from . import type_registry

import copy


@type_registry.register_type
class Composable(serializable_object.SerializableObject):
    """An object that can be composed by tracks.

    Base class of:
        Item
        Transition
    """

    name = serializable_object.serializable_field(
        "name",
        doc="Composable name."
    )
    metadata = serializable_object.serializable_field(
        "metadata",
        doc="Metadata dictionary for this Composable."
    )

    _serializable_label = "Composable.1"
    _class_path = "core.Composable"

    def __init__(self, name=None, metadata=None):
        super(Composable, self).__init__()
        self._parent = None

        # initialize the serializable fields
        self.name = name
        self.metadata = copy.deepcopy(metadata) if metadata else {}

    @staticmethod
    def visible():
        """Return the visibility of the Composable. By default True."""

        return False

    @staticmethod
    def overlapping():
        """Return whether an Item is overlapping. By default False."""

        return False

    # @{ functions to express the composable hierarchy
    def _root_parent(self):
        return ([self] + self._ancestors())[-1]

    def _ancestors(self):
        ancestors = []
        seqi = self
        while seqi.parent() is not None:
            seqi = seqi.parent()
            ancestors.append(seqi)
        return ancestors

    def parent(self):
        """Return the parent Composable, or None if self has no parent."""

        return self._parent() if self._parent is not None else None

    def _set_parent(self, new_parent):
        if new_parent is not None and self.parent() is not None:
            raise ValueError(
                "Composable named '{}' is already in a composition named '{}',"
                " remove from previous parent before adding to new one."
                " Composable: {}, Composition: {}".format(
                    self.name,
                    self.parent() is not None and self.parent().name or None,
                    self,
                    self.parent()
                )
            )
        self._parent = weakref.ref(new_parent) if new_parent is not None else None

    def is_parent_of(self, other):
        """Returns true if self is a parent or ancestor of other."""

        visited = set([])
        while other.parent() is not None and other.parent() not in visited:
            if other.parent() is self:
                return True
            visited.add(other)
            other = other.parent()

        return False

    # @}

    def __repr__(self):
        return (
            "otio.{}("
            "name={}, "
            "metadata={}"
            ")".format(
                self._class_path,
                repr(self.name),
                repr(self.metadata)
            )
        )

    def __str__(self):
        return "{}({}, {})".format(
            self._class_path.split('.')[-1],
            self.name,
            str(self.metadata)
        )
