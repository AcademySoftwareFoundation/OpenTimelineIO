""" Marker class.  Holds metadata over regions of time.  """

from .. import (
    core,
    opentime,
)


class MarkerColor:
    """ Enum encoding colors of markers as strings.  """

    Red = "RED"
    Green = "GREEN"
    Blue = "BLUE"
    Cyan = "CYAN"
    Magenta = "MAGENTA"
    Yellow = "YELLOW"
    Black = "BLACK"
    White = "WHITE"


@core.register_type
class Marker(core.SerializeableObject):

    """ Holds metadata over time on a timeline """

    _serializeable_label = "Marker.2"
    _class_path = "marker.Marker"

    def __init__(
        self,
        name=None,
        marked_range=None,
        color_string=MarkerColor.Red,
        metadata=None,
    ):
        core.SerializeableObject.__init__(
            self,
        )
        self.name = name
        self.marked_range = marked_range
        self.color_string = color_string

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    name = core.serializeable_field("name", str, "Name of this marker.")

    marked_range = core.serializeable_field(
        "marked_range",
        opentime.TimeRange,
        "Range this marker applies to."
    )

    color_string = core.serializeable_field(
        "color_string",
        required_type=type(MarkerColor.Red),
        doc="Color string for this marker (for example: 'RED'), based on the "
        "otio.schema.marker.MarkerColor enum."
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
