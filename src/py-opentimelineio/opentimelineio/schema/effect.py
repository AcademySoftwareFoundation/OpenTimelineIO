# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Effect)
def __str__(self):
    return (
        "Effect("
        "{}, "
        "{}, "
        "{}, "
        "{}"
        ")".format(
            str(self.name),
            str(self.effect_name),
            str(self.metadata),
            str(self.enabled)
        )
    )


@add_method(_otio.Effect)
def __repr__(self):
    return (
        "otio.schema.Effect("
        "name={}, "
        "effect_name={}, "
        "metadata={}, "
        "enabled={}"
        ")".format(
            repr(self.name),
            repr(self.effect_name),
            repr(self.metadata),
            repr(self.enabled)
        )
    )
