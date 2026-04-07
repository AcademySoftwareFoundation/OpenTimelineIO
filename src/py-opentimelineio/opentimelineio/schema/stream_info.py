# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.StreamInfo)
def __str__(self):
    return (
        "StreamInfo("
        "{}, "
        "{}, "
        "{}"
        ")".format(
            str(self.name),
            str(self.address),
            str(self.kind),
        )
    )


@add_method(_otio.StreamInfo)
def __repr__(self):
    return (
        "otio.schema.StreamInfo("
        "name={}, "
        "address={}, "
        "kind={}"
        ")".format(
            repr(self.name),
            repr(self.address),
            repr(self.kind),
        )
    )
