# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.V2d)
def __str__(self):
    return 'V2d({}, {})'.format(
        self.x,
        self.y
    )


@add_method(_otio.V2d)
def __repr__(self):
    return (
        'otio.schema.V2d('
        'x={}, '
        'y={}'
        ')'.format(
            repr(self.x),
            repr(self.y),
        )
    )
