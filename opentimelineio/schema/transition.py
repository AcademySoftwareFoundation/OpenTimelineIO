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

"""Transition base class"""

from .. import (
    opentime,
    core,
    exceptions,
)

import copy


class TransitionTypes:
    """Enum encoding types of transitions.

    This is for representing "Dissolves" and "Wipes" defined by the
    multi-source effect as defined by SMPTE 258M-2004 7.6.3.2

    Other effects are handled by the `schema.Effect` class.
    """

    # @{ SMPTE transitions.
    SMPTE_Dissolve = "SMPTE_Dissolve"
    # SMPTE_Wipe = "SMPTE_Wipe" -- @TODO
    # @}

    # Non SMPTE transitions.
    Custom = "Custom_Transition"


@core.register_type
class Transition(core.Composable):
    """Represents a transition between two items."""

    _serializable_label = "Transition.1"

    def __init__(
        self,
        name=None,
        transition_type=None,
        # @TODO: parameters will be added later as needed (SMPTE_Wipe will
        #        probably require it)
        # parameters=None,
        in_offset=None,
        out_offset=None,
        metadata=None
    ):
        core.Composable.__init__(
            self,
            name=name,
            metadata=metadata
        )

        # init everything as None first, so that we will catch uninitialized
        # values via exceptions
        # if parameters is None:
        #     parameters = {}
        # self.parameters = parameters
        self.transition_type = transition_type
        self.in_offset = copy.deepcopy(in_offset)
        self.out_offset = copy.deepcopy(out_offset)

    transition_type = core.serializable_field(
        "transition_type",
        required_type=type(TransitionTypes.SMPTE_Dissolve),
        doc="Kind of transition, as defined by the "
        "schema.transition.TransitionTypes enum."
    )
    # parameters = core.serializable_field(
    #     "parameters",
    #     doc="Parameters of the transition."
    # )
    in_offset = core.serializable_field(
        "in_offset",
        required_type=opentime.RationalTime,
        doc="Amount of the previous clip this transition overlaps, exclusive."
    )
    out_offset = core.serializable_field(
        "out_offset",
        required_type=opentime.RationalTime,
        doc="Amount of the next clip this transition overlaps, exclusive."
    )

    def __str__(self):
        return 'Transition("{}", "{}", {}, {}, {})'.format(
            self.name,
            self.transition_type,
            self.in_offset,
            self.out_offset,
            # self.parameters,
            self.metadata
        )

    def __repr__(self):
        return (
            'otio.schema.Transition('
            'name={}, '
            'transition_type={}, '
            'in_offset={}, '
            'out_offset={}, '
            # 'parameters={}, '
            'metadata={}'
            ')'.format(
                repr(self.name),
                repr(self.transition_type),
                repr(self.in_offset),
                repr(self.out_offset),
                # repr(self.parameters),
                repr(self.metadata),
            )
        )

    @staticmethod
    def overlapping():
        return True

    def duration(self):
        return self.in_offset + self.out_offset

    def range_in_parent(self):
        """Find and return the range of this item in the parent."""
        if not self.parent():
            raise exceptions.NotAChildError(
                "No parent of {}, cannot compute range in parent.".format(self)
            )

        return self.parent().range_of_child(self)

    def trimmed_range_in_parent(self):
        """Find and return the timmed range of this item in the parent."""
        if not self.parent():
            raise exceptions.NotAChildError(
                "No parent of {}, cannot compute range in parent.".format(self)
            )

        return self.parent().trimmed_range_of_child(self)
