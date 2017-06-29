#!/usr/bin/env python

from .. import core

__doc__ = """Gap Item - represents a transparent gap in content."""


@core.register_type
class Gap(core.Item):
    _serializeable_label = "Gap.1"
    _class_path = "schema.Gap"

    @staticmethod
    def visible():
        return False


# the original name for "gap" was "filler" - this will turn "Filler" found in
# OTIO files into Gap automatically.
core.register_type(Gap, "Filler")
