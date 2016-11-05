#!/usr/bin/env python

from .. import core

__doc__ = """ Filler Item - represents a gap in content. """


@core.register_type
class Filler(core.Item):
    _serializeable_label = "Filler.1"
    _class_path = "schema.Filler"

    @staticmethod
    def visible():
        return False
