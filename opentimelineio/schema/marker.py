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

"""Marker class.  Holds metadata over regions of time."""

from .. import (
    core,
    opentime,
)


class MarkerColor:
    """ Enum encoding colors of markers as strings.  """

    PINK = "PINK"
    RED = "RED"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    CYAN = "CYAN"
    BLUE = "BLUE"
    PURPLE = "PURPLE"
    MAGENTA = "MAGENTA"
    BLACK = "BLACK"
    WHITE = "WHITE"


@core.register_type
class Marker(core.SerializableObject):

    """ Holds metadata over time on a timeline """

    _serializable_label = "Marker.2"
    _class_path = "marker.Marker"

    def __init__(
        self,
        name=None,
        marked_range=None,
        color=MarkerColor.RED,
        metadata=None,
    ):
        core.SerializableObject.__init__(
            self,
        )
        self.name = name
        self.marked_range = marked_range
        self.color = color
        self.metadata = metadata or {}

    name = core.serializable_field("name", doc="Name of this marker.")

    marked_range = core.serializable_field(
        "marked_range",
        opentime.TimeRange,
        "Range this marker applies to, relative to the Item this marker is "
        "attached to (e.g. the Clip or Track that owns this marker)."
    )

    color = core.serializable_field(
        "color",
        required_type=type(MarkerColor.RED),
        doc="Color string for this marker (for example: 'RED'), based on the "
        "otio.schema.marker.MarkerColor enum."
    )

    # old name
    range = core.deprecated_field()

    metadata = core.serializable_field(
        "metadata",
        dict,
        "Metadata dictionary."
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
