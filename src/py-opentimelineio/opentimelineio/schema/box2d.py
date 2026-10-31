# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. import _otio
from ..core._core_utils import add_method


@add_method(_otio.Box2d)
def __str__(self):
    return "Box2d({}, {})".format(self.min, self.max)


@add_method(_otio.Box2d)
def __repr__(self):
    return "otio.schema.Box2d(min={}, max={})".format(repr(self.min), repr(self.max))
