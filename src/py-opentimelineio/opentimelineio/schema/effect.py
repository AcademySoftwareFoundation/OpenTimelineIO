# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. import _otio
from ..core._core_utils import add_method


@add_method(_otio.Effect)
def __str__(self):
    return "Effect({}, {}, {}, {})".format(
        str(self.name), str(self.effect_name), str(self.metadata), str(self.enabled)
    )


@add_method(_otio.Effect)
def __repr__(self):
    return (
        "otio.schema.Effect(name={}, effect_name={}, metadata={}, enabled={})".format(
            repr(self.name),
            repr(self.effect_name),
            repr(self.metadata),
            repr(self.enabled),
        )
    )
