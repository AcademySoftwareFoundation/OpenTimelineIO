""" Marker class.  Holds metadata over regions of time.  """

from .. import (
    core,
    opentime,
)


@core.register_type
class Marker(core.SerializeableObject):

    """ Holds metadata over time on a timeline """

    _serializeable_label = "Marker.2"
    _class_path = "marker.Marker"

    def __init__(
        self,
        name=None,
        marked_range=None,
        metadata=None,
    ):
        core.SerializeableObject.__init__(
            self,
        )
        self.name = name
        self.marked_range = marked_range

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    name = core.serializeable_field("name", str, "Name of this marker.")

    marked_range = core.serializeable_field(
        "marked_range",
        opentime.TimeRange,
        "Range this marker applies to."
    )

    # old name
    range = core.deprecated_field()

    metadata = core.serializeable_field(
        "metadata",
        dict,
        "Metadata dictionary."
    )

    def __eq__(self, other):
        try:
            return (
                (self.name, self.marked_range, self.metadata) ==
                (other.name, other.marked_range, other.metadata)
            )
        except (KeyError, AttributeError):
            return False

    def __hash__(self):
        return hash(
            (
                self.name,
                self.marked_range,
                tuple(self.metadata.items())
            )
        )

    def __repr__(self):
        return (
            "otio.schema.Marker("
            "name={}, "
            "marked_range={}, "
            "metadata={}"
            ")".format(
                repr(self.name),
                repr(self.marked_range),
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
                str(self.marked_range),
                str(self.metadata),
            )
        )


@core.upgrade_function_for(Marker, 2)
def _version_one_to_two(data):
    data["marked_range"] = data["range"]
    del data["range"]
    return data
