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


@add_method(_otio.ImageSequenceReference)
def frame_range_for_time_range(self, time_range):
    """
    Returns a :class:`tuple` containing the first and last frame numbers for
    the given time range in the reference.

    Raises ValueError if the provided time range is outside the available
    range.
    """
    return (
        self.frame_for_time(time_range.start_time),
        self.frame_for_time(time_range.end_time_inclusive())
    )


@add_method(_otio.ImageSequenceReference)
def abstract_target_url(self, symbol):
    """
    Generates a target url for a frame where :param:``symbol`` is used in place
    of the frame number. This is often used to generate wildcard target urls.
    """
    if not self.target_url_base.endswith("/"):
        base = self.target_url_base + "/"
    else:
        base = self.target_url_base

    return "{}{}{}{}".format(
        base, self.name_prefix, symbol, self.name_suffix
    )
