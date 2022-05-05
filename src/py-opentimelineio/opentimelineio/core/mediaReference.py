# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from . _core_utils import add_method
from .. import _otio


@add_method(_otio.MediaReference)
def __str__(self):
    return "{}({}, {}, {}, {})".format(
        self.__class__.__name__,
        repr(self.name),
        repr(self.available_range),
        repr(self.available_image_bounds),
        repr(self.metadata)
    )


@add_method(_otio.MediaReference)
def __repr__(self):
    return (
        "otio.{}.{}("
        "name={},"
        " available_range={},"
        " available_image_bounds={},"
        " metadata={}"
        ")"
    ).format(
        "core" if self.__class__ is _otio.MediaReference else "schema",
        self.__class__.__name__,
        repr(self.name),
        repr(self.available_range),
        repr(self.available_image_bounds),
        repr(self.metadata)
    )
