# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from . _core_utils import add_method
from .. import _otio

_otio.Item.__doc__ = """
An item in the timeline.

An Item can contain effects, markers, a source range, and metadata.
"""

@add_method(_otio.Item)
def __str__(self):
    return "{}({}, {}, {}, {}, {}, {})".format(
        self.__class__.__name__,
        self.name,
        str(self.source_range),
        str(self.effects),
        str(self.markers),
        str(self.enabled),
        str(self.metadata)
    )


@add_method(_otio.Item)
def __repr__(self):
    return (
        "otio.{}.{}("
        "name={}, "
        "source_range={}, "
        "effects={}, "
        "markers={}, "
        "enabled={}, "
        "metadata={}"
        ")".format(
            "core" if self.__class__ is _otio.Item else "schema",
            self.__class__.__name__,
            repr(self.name),
            repr(self.source_range),
            repr(self.effects),
            repr(self.markers),
            repr(self.enabled),
            repr(self.metadata)
        )
    )
