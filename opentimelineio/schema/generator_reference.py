"""
Generators are media references that _produce_ media rather than refer to it.
"""

from .. import (
    core,
)


@core.register_type
class GeneratorReference(core.MediaReference):
    """
    Base class for Generators.

    Generators are media references that become "generators" in editorial
    systems.  For example, color bars or a solid color.
    """

    _serializable_label = "GeneratorReference.1"
    _name = "GeneratorReference"

    def __init__(
        self,
        name=None,
        generator_kind=None,
        available_range=None,
        parameters=None,
        metadata=None
    ):
        super(GeneratorReference, self).__init__(
            name,
            available_range,
            metadata
        )

        if parameters is None:
            parameters = {}
        self.parameters = parameters
        self.generator_kind = generator_kind

    parameters = core.serializable_field(
        "parameters",
        dict,
        doc="Dictionary of parameters for generator."
    )
    generator_kind = core.serializable_field(
        "generator_kind",
        required_type=type(""),
        # @TODO: need to clarify if this also has an enum of supported types
        # / generic
        doc="Kind of generator reference, as defined by the "
        "schema.generator_reference.GeneratorReferenceTypes enum."
    )

    def __str__(self):
        return 'GeneratorReference("{}", "{}", {}, {})'.format(
            self.name,
            self.generator_kind,
            self.parameters,
            self.metadata
        )

    def __repr__(self):
        return (
            'otio.schema.GeneratorReference('
            'name={}, '
            'generator_kind={}, '
            'parameters={}, '
            'metadata={}'
            ')'.format(
                repr(self.name),
                repr(self.generator_kind),
                repr(self.parameters),
                repr(self.metadata),
            )
        )
