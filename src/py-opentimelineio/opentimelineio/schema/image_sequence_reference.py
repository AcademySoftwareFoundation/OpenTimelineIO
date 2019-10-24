from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.ImageSequenceReference)
def __str__(self):
    return (
        'ImageSequenceReference('
        '"{}", "{}", "{}", {}, {}, {}, {}, {}, {})' .format(
            self.target_url_base,
            self.name_prefix,
            self.name_suffix,
            self.start_value,
            self.value_step,
            self.rate,
            self.image_number_zero_padding,
            self.available_range,
            self.metadata,
        )
    )


@add_method(_otio.ImageSequenceReference)
def __repr__(self):
    return (
        'ImageSequenceReference('
        'target_url_base={}, '
        'name_prefix={}, '
        'name_suffix={}, '
        'start_value={}, '
        'value_step={}, '
        'rate={}, '
        'image_number_zero_padding={}, '
        'available_range={}, '
        'metadata={}'
        ')' .format(
            repr(self.target_url_base),
            repr(self.name_prefix),
            repr(self.name_suffix),
            repr(self.start_value),
            repr(self.value_step),
            repr(self.rate),
            repr(self.image_number_zero_padding),
            repr(self.available_range),
            repr(self.metadata),
        )
    )
