""" Marker class.  Holds metadata over regions of time.  """

from .. import (
    core,
    opentime,
)


@core.register_type
class Marker(core.SerializeableObject):

    """ Holds metadata over time on a timeline """

    _serializeable_label = "Marker.1"
    _class_path = "marker.Marker"

    def __init__(
        self,
        name=None,
        range=None,
        metadata=None,
    ):
        core.SerializeableObject.__init__(
            self,
        )
        self.name = name
        self.range = range

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    name = core.serializeable_field("name", str, "Name of this marker.")
    range = core.serializeable_field(
        "range",
        opentime.TimeRange,
        "Range this marker applies to."
    )
    metadata = core.serializeable_field(
        "metadata",
        dict,
        "Metadata dictionary."
    )

    def __eq__(self, other):
        try:
            return (
                (self.name, self.range, self.metadata) ==
                (other.name, other.range, other.metadata)
            )
        except (KeyError, AttributeError):
            return False

    def __hash__(self):
        return hash(
            (
                self.name,
                self.range,
                tuple(self.metadata.items())
            )
        )

    def __repr__(self):
        return (
            "otio.schema.Marker("
            "name={}, "
            "range={}, "
            "metadata={}"
            ")".format(
                repr(self.name),
                repr(self.range),
                repr(self.metadata),
            )
        )

    def __str__(self):
        return (
            "Marker("
            "{}, "
            "{}, "
            "{}"
            ")".format(
                str(self.name),
                str(self.range),
                str(self.metadata),
            )
        )
