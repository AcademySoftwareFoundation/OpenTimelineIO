from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Marker)
def __str__(self):
    return 'Marker("{}", {}, {}, {})'.format(
        self.name,
        self.media_reference,
        self.source_range,
        self.metadata
    )


@add_method(_otio.Marker)
def __repr__(self):
    return (
        'otio.schema.Marker('
        'name={}, '
        'media_reference={}, '
        'source_range={}, '
        'metadata={}'
        ')'.format(
            repr(self.name),
            repr(self.media_reference),
            repr(self.source_range),
            repr(self.metadata),
        )
    )
