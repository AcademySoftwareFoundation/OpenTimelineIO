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

from .. import (
    core,
    opentime,
)

"""Gap Item - represents a transparent gap in content."""


@core.register_type
class Gap(core.Item):
    _serializable_label = "Gap.1"
    _class_path = "schema.Gap"

    def __init__(
        self,
        name=None,
        # note - only one of the following two arguments is accepted
        # if neither is provided, source_range will be set to an empty
        # TimeRange
        # Duration is provided as a convienence for creating a gap of a certain
        # length.  IE: Gap(duration=otio.opentime.RationalTime(300, 24))
        duration=None,
        source_range=None,
        effects=None,
        markers=None,
        metadata=None,
    ):
        if duration and source_range:
            raise RuntimeError(
                "Cannot instantiate with both a source range and a duration."
            )

        if duration:
            source_range = opentime.TimeRange(
                opentime.RationalTime(0, duration.rate),
                duration
            )
        elif source_range is None:
            # if neither is provided, seed TimeRange as an empty Source Range.
            source_range = opentime.TimeRange()

        core.Item.__init__(
            self,
            name=name,
            source_range=source_range,
            effects=effects,
            markers=markers,
            metadata=metadata
        )

    @staticmethod
    def visible():
        return False


# the original name for "gap" was "filler" - this will turn "Filler" found in
# OTIO files into Gap automatically.
core.register_type(Gap, "Filler")
