#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Implementation of Effect OTIO class."""

from .. import (
    core
)

import copy


@core.register_type
class Effect(core.SerializableObject):
    _serializable_label = "Effect.1"

    def __init__(
        self,
        name=None,
        effect_name=None,
        metadata=None
    ):
        super(Effect, self).__init__()
        self.name = name
        self.effect_name = effect_name
        self.metadata = copy.deepcopy(metadata) if metadata else {}

    name = core.serializable_field(
        "name",
        doc="Name of this effect object. Example: 'BlurByHalfEffect'."
    )
    effect_name = core.serializable_field(
        "effect_name",
        doc="Name of the kind of effect (example: 'Blur', 'Crop', 'Flip')."
    )
    metadata = core.serializable_field(
        "metadata",
        dict,
        doc="Metadata dictionary."
    )

    def __str__(self):
        return (
            "Effect("
            "{}, "
            "{}, "
            "{}"
            ")".format(
                str(self.name),
                str(self.effect_name),
                str(self.metadata),
            )
        )

    def __repr__(self):
        return (
            "otio.schema.Effect("
            "name={}, "
            "effect_name={}, "
            "metadata={}"
            ")".format(
                repr(self.name),
                repr(self.effect_name),
                repr(self.metadata),
            )
        )


@core.register_type
class TimeEffect(Effect):
    "Base Time Effect Class"
    _serializable_label = "TimeEffect.1"
    pass


@core.register_type
class LinearTimeWarp(TimeEffect):
    "A time warp that applies a linear scale across the entire clip"
    _serializable_label = "LinearTimeWarp.1"

    def __init__(self, name=None, time_scalar=1, metadata=None):
        Effect.__init__(
            self,
            name=name,
            effect_name="LinearTimeWarp",
            metadata=metadata
        )
        self.time_scalar = time_scalar

    time_scalar = core.serializable_field(
        "time_scalar",
        doc="Linear time scalar applied to clip.  "
        "2.0 = double speed, 0.5 = half speed."
    )


@core.register_type
class FreezeFrame(LinearTimeWarp):
    "Hold the first frame of the clip for the duration of the clip."
    _serializable_label = "FreezeFrame.1"

    def __init__(self, name=None, metadata=None):
        LinearTimeWarp.__init__(
            self,
            name=name,
            time_scalar=0,
            metadata=metadata
        )
        self.effect_name = "FreezeFrame"
