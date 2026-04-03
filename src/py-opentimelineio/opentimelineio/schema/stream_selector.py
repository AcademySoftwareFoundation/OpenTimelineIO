# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.StreamSelector)
def __str__(self):
    return (
        "StreamSelector("
        "{}, "
        "{}, "
        "{}"
        ")".format(
            str(self.name),
            str(self.effect_name),
            str(self.output_streams),
        )
    )


@add_method(_otio.StreamSelector)
def __repr__(self):
    return (
        "otio.schema.StreamSelector("
        "name={}, "
        "effect_name={}, "
        "output_streams={}"
        ")".format(
            repr(self.name),
            repr(self.effect_name),
            repr(self.output_streams),
        )
    )
