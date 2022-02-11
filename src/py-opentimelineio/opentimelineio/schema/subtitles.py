from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Subtitles)
def __str__(self):
    return (
        'Subtitles('
        '{}, {}, {}, {}, "{}", {}, {}, {})' .format(
            self.extent_x,
            self.extent_y,
            self.padding_x,
            self.padding_y,
            self.background_color,
            self.background_opacity,
            self.display_alignment,
            str(self.timed_texts)
        )
    )


@add_method(_otio.Subtitles)
def __repr__(self):
    return (
        'Subtitles('
        'extent_x={}, '
        'extent_y={}, '
        'padding_x={}, '
        'padding_y={}, '
        'background_color={}, '
        'background_opacity={}, '
        'display_alignment={}, '
        'timed_texts={} '
        ')' .format(
            repr(self.extent_x),
            repr(self.extent_y),
            repr(self.padding_x),
            repr(self.padding_y),
            repr(self.background_color),
            repr(self.background_opacity),
            repr(self.display_alignment),
            repr(self.timed_texts)
        )
    )
