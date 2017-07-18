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
Composable class definition.  An object that can be composed by sequences.
"""

from . import serializeable_object
from . import type_registry


@type_registry.register_type
class Composable(serializeable_object.SerializeableObject):
    """An object that can be composed by sequences.

    Base class of:
        Item
        Transition
    """

    name = serializeable_object.serializeable_field(
        "name",
        doc="Composable name."
    )
    metadata = serializeable_object.serializeable_field(
        "metadata",
        doc="Metadata dictionary for this Composable."
    )

    _serializeable_label = "Composable.1"
    _class_path = "core.Composable"

    def __init__(self, name=None, metadata=None):
        super(Composable, self).__init__()
        self._parent = None

        # initialize the serializeable fields
        self.name = name

        if metadata is None:
            metadata = {}
        self.metadata = metadata

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
        while seqi._parent is not None:
            seqi = seqi._parent
            ancestors.append(seqi)
        return ancestors

    def parent(self):
        """Return the parent Composable, or None if self has no parent."""

        return self._parent

    def _set_parent(self, new_parent):
        if self._parent is not None and (
            hasattr(self._parent, "remove") and
            self in self._parent
        ):
            self._parent.remove(self)

        self._parent = new_parent

    def is_parent_of(self, other):
        """Returns true if self is a parent or ancestor of other."""

        visited = set([])
        while other._parent is not None and other._parent not in visited:
            if other._parent is self:
                return True
            visited.add(other)
            other = other._parent

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
