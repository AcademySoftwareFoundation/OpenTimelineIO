from .. import opentime

from . import serializeable_object


class Item(serializeable_object.SerializeableObject):
    _serializeable_label = "Item.1"
    _class_path = "core.Item"

    def __init__(
        self,
        name=None,
        source_range=None,
        effects=None,
        markers=None,
        metadata=None,
    ):
        serializeable_object.SerializeableObject.__init__(self)

        self.name = name
        self.source_range = source_range

        if effects is None:
            effects = []
        self.effects = effects

        if markers is None:
            markers = []
        self.markers = markers

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    name = serializeable_object.serializeable_field("name")
    source_range = serializeable_object.serializeable_field(
        "source_range", opentime.TimeRange)

    def duration(self):
        if self.source_range:
            return self.source_range.duration
        return self.computed_duration()

    def computed_duration(self):
        raise NotImplementedError

    markers = serializeable_object.serializeable_field("markers")
    effects = serializeable_object.serializeable_field("effects")
    metadata = serializeable_object.serializeable_field("metadata")

    def __repr__(self):
        return (
            "otio.{}("
            "name={}, "
            "source_range={}, "
            "effects={}, "
            "markers={}, "
            "metadata={}"
            ")".format(
                self._class_path,
                repr(self.name),
                repr(self.source_range),
                repr(self.effects),
                repr(self.markers),
                repr(self.metadata)
            )
        )

    def __str__(self):
        return "{}({}, {}, {}, {}, {})".format(
            self._class_path.split('.')[-1],
            self.name,
            str(self.source_range),
            str(self.effects),
            str(self.markers),
            str(self.metadata)
        )
