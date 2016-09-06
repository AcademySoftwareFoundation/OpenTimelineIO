"""
Media Reference Classes and Functions.
"""

from . import (
    opentime,
    core,
)


@core.register_type
class MediaReference(core.SerializeableObject):
    """
    Base Media Reference Class.

    Currently handles string printing the child classes, which expose interface
    into its data dictionary.

    The requirement is that the schema is named so that external systems can
    fetch the required information correctly.
    """
    serializeable_label = "MediaReference.1"
    _name = "MediaReference"

    def __init__(
        self,
        name=None,
        available_range=None,
        metadata=None
    ):
        core.SerializeableObject.__init__(self)

        self.name = name
        self.available_range = available_range

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    name = core.serializeable_field("name")
    available_range = core.serializeable_field(
        "available_range",
        opentime.TimeRange
    )
    metadata = core.serializeable_field("metadata", dict)

    def __str__(self):
        return "{}()".format(self._name)

    def __repr__(self):
        return "otio.media_reference.{}()".format(self._name)

    def __hash__(self, other):
        return hash(
            self.name,
            self._name,
            self.available_range,
            self.metadata
        )


@core.register_type
class MissingReference(MediaReference):
    serializeable_label = "MissingReference.1"
    _name = "MissingReference"


@core.register_type
class External(MediaReference):
    serializeable_label = "ExternalReference.1"
    _name = "External"

    def __init__(
        self,
        target_url=None,
        available_range=None,
        metadata=None,
    ):
        MediaReference.__init__(
            self,
            available_range=available_range,
            metadata=metadata
        )

        self.target_url = target_url

    target_url = core.serializeable_field("target_url")

    def __str__(self):
        return 'External("{}")'.format(self.target_url)

    def __repr__(self):
        return 'otio.media_reference.External(target_url={})'.format(
            repr(self.target_url)
        )

    def __hash__(self, other):
        return hash(
            self.name,
            self._name,
            self.available_range,
            self.target_url,
            self.metadata
        )
