from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.TimedText)
def __str__(self):
    return (
        'TimedText('
        '"{}", "{}", "{}", {})' .format(
            self.text,
            self.in_time,
            self.out_time,
            self.style
        )
    )


@add_method(_otio.TimedText)
def __repr__(self):
    return (
        'TimedText('
        'text={}, '
        'in_time={}, '
        'out_time={}, '
        'style={}'
        ')' .format(
            repr(self.text),
            repr(self.in_time),
            repr(self.out_time),
            repr(self.style),
        )
    )