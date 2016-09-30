from .. import (
    core,
    media_reference as mr,
    exceptions
)


@core.register_type
class Clip(core.Item):
    _serializeable_label = "Clip.1"

    def __init__(
        self,
        name=None,
        media_reference=None,
        source_range=None,
    ):
        core.Item.__init__(
            self,
            name=name,
            source_range=source_range,
        )
        # init everything as None first, so that we will catch uninitialized
        # values via exceptions
        self.name = name

        if not media_reference:
            media_reference = mr.MissingReference()
        self.media_reference = media_reference

        self.properties = {}

    name = core.serializeable_field("name")
    transform = core.deprecated_field()
    media_reference = core.serializeable_field(
        "media_reference",
        mr.MediaReference
    )

    def computed_duration(self):
        if self.source_range is not None:
            return self.source_range.duration

        if self.media_reference.available_range is not None:
            return self.media_reference.available_range.duration

        raise exceptions.CannotComputeDurationError(
            "No source_range on clip or available_range on media_reference for"
            " clip: {}".format(self)
        )

    def __str__(self):
        return 'Clip("{}", {}, {})'.format(
            self.name,
            self.media_reference,
            self.source_range
        )

    def __repr__(self):
        return (
            'otio.schema.Clip('
            'name={}, '
            'media_reference={}, '
            'source_range={}'
            ')'.format(
                repr(self.name),
                repr(self.media_reference),
                repr(self.source_range),
            )
        )

    def each_clip(self, search_range=None):
        yield self
