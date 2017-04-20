""" Transition base class """

from .. import (
    opentime,
    core,
)


class TransitionTypes:
    """ Enum encoding types of transitions.

    This is for representing "Dissolves" and "Wipes" defined by the
    multi-source effect as defined by:
        SMPTE 258M-2004 7.6.3.2

    Other effects are handled by the `schema.Effect` class.
    """

    # @{ SMPTE transitions.
    SMPTE_Dissolve = "SMPTE_Dissolve"
    # SMPTE_Wipe = "SMPTE_Wipe" -- @TODO
    # @}

    # Non SMPTE transitions.
    Custom = "Custom_Transition"


@core.register_type
class Transition(core.Sequenceable):
    """ Represents a transition between two items.  """

    _serializeable_label = "Transition.1"

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
        core.Sequenceable.__init__(
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
        self.in_offset = in_offset
        self.out_offset = out_offset

    transition_type = core.serializeable_field(
        "transition_type",
        required_type=type(TransitionTypes.SMPTE_Dissolve),
        doc="Kind of transition, as defined by the "
        "schema.transition.TransitionTypes enum."
    )
    # parameters = core.serializeable_field(
    #     "parameters",
    #     doc="Parameters of the transition."
    # )
    in_offset = core.serializeable_field(
        "in_offset",
        required_type=opentime.RationalTime,
        doc="Amount of the previous clip this transition overlaps, exclusive."
    )
    out_offset = core.serializeable_field(
        "out_offset",
        required_type=opentime.RationalTime,
        doc="Amount of the next clip this transition overlaps, exclusive."
    )

    def duration(self):
        return opentime.RationalTime()

    def each_clip(self, *_, **__):
        return []

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
