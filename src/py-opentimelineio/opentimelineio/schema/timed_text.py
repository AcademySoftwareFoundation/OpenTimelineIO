from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.TimedText)
def __str__(self):
    return (
        'TimedText('
        '"{}", {}, {}, {})' .format(
            self.in_time,
            self.out_time,
            self.texts,
            self.style_ids
        )
    )


@add_method(_otio.TimedText)
def __repr__(self):
    return (
        'TimedText('
        'in_time={}, '
        'out_time={}, '
        'texts={}, '
        'style_ids={}'
        ')' .format(
            repr(self.in_time),
            repr(self.out_time),
            repr(self.texts),
            repr(self.style_ids)
        )
    )
