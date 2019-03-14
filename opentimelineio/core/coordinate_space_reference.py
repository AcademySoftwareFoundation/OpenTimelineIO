#!/usr/bin/env python
#
# Copyright 2019 Pixar Animation Studios
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

"""
Coordinate Space Reference - reference a coordinate space on a specific object.
"""

import weakref


class CoordinateSpaceReference(object):
    __doc__ = __doc__

    __slots__ = ["source_object", "space"]

    def __init__(self, source_object, space):
        object.__setattr__(self, "source_object", weakref.ref(source_object))
        object.__setattr__(self, "space", space)

    def __setattr__(self, key, val):
        """Enforces immutability """
        raise AttributeError("RationalTime is Immutable.")

    def __str__(self):
        return "CoordinateSpaceReference({}, {})".format(
            str(self.source_object),
            str(self.space),
        )

    def __repr__(self):
        return (
            "otio.core.CoordinateSpaceReference("
            "source_object={}, space={})".format(
                repr(self.source_object),
                repr(self.space),
            )
        )

    def __eq__(self, other):
        try:
            return (
                self.space is other.space
                and self.source_object() is other.source_object()
            )
        except AttributeError:
            return False
