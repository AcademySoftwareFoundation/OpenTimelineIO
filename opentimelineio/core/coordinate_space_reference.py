#!/usr/bin/env python

"""
Coordinate Space Reference - reference a coordinate space on a specific object.
"""

class CoordinateSpaceReference(object):
    __doc__ = __doc__
    def __init__(self, source_object, space):
        self.source_object = source_object
        self.space = space

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
