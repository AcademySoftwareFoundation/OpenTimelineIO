#!/usr/bin/env python

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
