# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. import _otio
from ..core._core_utils import add_method


@add_method(_otio.Color)
def __str__(self):
    return "Color({}, ({}, {}, {}, {}))".format(
        repr(self.name), self.r, self.g, self.b, self.a
    )


@add_method(_otio.Color)
def __repr__(self):
    return "otio.core.Color(name={}, r={}, g={}, b={}, a={})".format(
        repr(self.name), repr(self.r), repr(self.g), repr(self.b), repr(self.a)
    )
