from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Transition)
def __str__(self):
    return 'Transition("{}", "{}", {}, {}, {})'.format(
        self.name,
        self.transition_type,
        self.in_offset,
        self.out_offset,
        self.metadata
    )


@add_method(_otio.Transition)
def __repr__(self):
    return (
        'otio.schema.Transition('
        'name={}, '
        'transition_type={}, '
        'in_offset={}, '
        'out_offset={}, '
        'metadata={}'
        ')'.format(
            repr(self.name),
            repr(self.transition_type),
            repr(self.in_offset),
            repr(self.out_offset),
            repr(self.metadata),
        )
    )
