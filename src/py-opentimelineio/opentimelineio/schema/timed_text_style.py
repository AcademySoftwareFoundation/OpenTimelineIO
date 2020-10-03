from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.TimedTextStyle)
def __str__(self):
    return (
        'TimedTextStyle('
        '"{}", "{}", "{}", {}, {}, {}, {}, "{}")' .format(
            self.style_id,
            self.text_alignment,
            self.text_color,
            self.text_size,
            self.text_bold,
            self.text_italics,
            self.text_underline,
            self.font_family
        )
    )


@add_method(_otio.TimedTextStyle)
def __repr__(self):
    return (
        'TimedTextStyle('
        'style_id={}, '
        'text_alignment={}, '
        'text_color={}, '
        'text_size={}, '
        'text_bold={}, '
        'text_italics={}, '
        'text_underline={}, '
        'font_family={}'
        ')' .format(
            repr(self.style_id),
            repr(self.text_alignment),
            repr(self.text_color),
            repr(self.text_size),
            repr(self.text_bold),
            repr(self.text_italics),
            repr(self.text_underline),
            repr(self.font_family),
        )
    )