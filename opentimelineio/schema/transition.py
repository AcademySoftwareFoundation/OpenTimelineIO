""" Transition base class """

from .. import (
    opentime,
    core,
)


@core.register_type
class Transition(core.Sequenceable):
    """ Represents a transition between two items.  """

    _serializeable_label = "Transition.1"

    def __init__(
        self,
        name=None,
        transition_type="",
        parameters=None,
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
        self.name = name
        if parameters is None:
            parameters = {}
        self.parameters = parameters
        self.transition_type = transition_type
        self.in_offset = in_offset
        self.out_offset = out_offset

    name = core.serializeable_field("name", doc="Name of this clip.")
    transition_type = core.serializeable_field(
        "transition_type",
        doc="Kind of transition"
    )
    parameters = core.serializeable_field(
        "parameters",
        doc="Parameters of the transition."
    )
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

    def __str__(self):
        return 'Transition("{}", "{}", {}, {})'.format(
            self.name,
            self.transition_type,
            self.parameters,
            self.metadata
        )

    def __repr__(self):
        return (
            'otio.schema.Transition('
            'name={}, '
            'transition_type={}, '
            'parameters={}, '
            'metadata={}'
            ')'.format(
                repr(self.name),
                repr(self.transition_type),
                repr(self.parameters),
                repr(self.metadata),
            )
        )

