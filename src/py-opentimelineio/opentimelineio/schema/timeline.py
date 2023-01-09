# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Timeline)
def __str__(self):
    return f'Timeline("{str(self.name)}", {str(self.tracks)})'


@add_method(_otio.Timeline)
def __repr__(self):
    return (
        "otio.schema.Timeline(name={}, tracks={})".format(
            repr(self.name),
            repr(self.tracks)
        )
    )
