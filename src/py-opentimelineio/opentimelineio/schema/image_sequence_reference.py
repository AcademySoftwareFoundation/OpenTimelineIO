from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.ImageSequenceReference)
def __str__(self):
    return (
        'ImageSequenceReference('
        '"{}", "{}", "{}", {}, {}, {}, {}, {}, {}, {})' .format(
            self.target_url_base,
            self.name_prefix,
            self.name_suffix,
            self.start_frame,
            self.frame_step,
            self.rate,
            self.frame_zero_padding,
            self.missing_frame_policy,
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
        'start_frame={}, '
        'frame_step={}, '
        'rate={}, '
        'frame_zero_padding={}, '
        'missing_frame_policy={}, '
        'available_range={}, '
        'metadata={}'
        ')' .format(
            repr(self.target_url_base),
            repr(self.name_prefix),
            repr(self.name_suffix),
            repr(self.start_frame),
            repr(self.frame_step),
            repr(self.rate),
            repr(self.frame_zero_padding),
            repr(self.missing_frame_policy),
            repr(self.available_range),
            repr(self.metadata),
        )
    )
