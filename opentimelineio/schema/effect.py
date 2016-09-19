"""
Implementation of Effect OTIO class.
"""

from .. import (
    core
)


@core.register_type
class Effect(core.SerializeableObject):
    _serializeable_label = "Effect.1"

    def __init__(
        self,
        name=None,
        effect_name=None,
        metadata=None
    ):
        core.SerializeableObject.__init__(self)
        self.name = name
        self.effect_name = effect_name

        if metadata is None:
            metadata = {}
        self.metadata = metadata
        self.metadata = metadata

    name = core.serializeable_field("name")
    effect_name = core.serializeable_field("effect_name")
    metadata = core.serializeable_field("metadata", dict)

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
