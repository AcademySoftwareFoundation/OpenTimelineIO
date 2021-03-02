from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Bounds)
def __str__(self):
    return 'Bounds("{}", {}, {})'.format(
        self.name,
        self.box,
        self.metadata
    )


@add_method(_otio.Bounds)
def __repr__(self):
    return (
        'otio.schema.Bounds('
        'name={}, '
        'box={}, '
        'metadata={}'
        ')'.format(
            repr(self.name),
            repr(self.box),
            repr(self.metadata),
        )
    )
