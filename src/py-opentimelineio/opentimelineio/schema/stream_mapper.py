# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.StreamMapper)
def __str__(self):
    return (
        "StreamMapper("
        "{}, "
        "{}"
        ")".format(
            str(self.name),
            str(self.stream_map),
        )
    )


@add_method(_otio.StreamMapper)
def __repr__(self):
    return (
        "otio.schema.StreamMapper("
        "name={}, "
        "stream_map={}"
        ")".format(
            repr(self.name),
            repr(self.stream_map),
        )
    )
