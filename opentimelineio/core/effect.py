from . import (
    type_registry,
    serializable_object
)

import copy

@type_registry.register_type
class Effect(serializable_object.SerializableObject):
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

    name = serializable_object.serializable_field(
        "name",
        doc="Name of this effect object. Example: 'BlurByHalfEffect'."
    )
    effect_name = serializable_object.serializable_field(
        "effect_name",
        doc="Name of the kind of effect (example: 'Blur', 'Crop', 'Flip')."
    )
    metadata = serializable_object.serializable_field(
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
            "otio.core.Effect("
            "name={}, "
            "effect_name={}, "
            "metadata={}"
            ")".format(
                repr(self.name),
                repr(self.effect_name),
                repr(self.metadata),
            )
        )


@type_registry.register_type
class TimeEffect(Effect):
    "Base Time Effect Class"
    _serializable_label = "TimeEffect.1"

    def time_transform(self):
        raise NotImplementedError
