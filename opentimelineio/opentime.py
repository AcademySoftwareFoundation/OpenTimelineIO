"""
Library for expressing and transforming time.

Defaults to 24 fps, but allows the caller to specify an override.

NOTE: This module is written specifically with a future port to C in mind.
When ported to C, Time will be a struct and these functions should be very
simple.
"""


class RationalTime(object):

    """ Represents a point in time.   Has a value and scale.  """

    def __init__(self, value=0, rate=1):
        self.value = value
        self.rate = rate

    def rescaled_to(self, new_rate):
        """ returns the time for this time converted to new_rate """

        if isinstance(new_rate, RationalTime):
            new_rate = new_rate.rate

        return RationalTime(
            self.value_rescaled_to(new_rate),
            new_rate
        )

    def value_rescaled_to(self, new_rate):
        """ returns the time value for self converted to new_rate """

        if new_rate == self.rate:
            return self.value

        if isinstance(new_rate, RationalTime):
            new_rate = new_rate.rate

        # TODO: This math probably needs some overrun protection
        # TODO: Don't we want to enforce integers here?
        try:
            return (float(self.value) * float(new_rate)) / float(self.rate)
        except (TypeError, ValueError):
            raise TypeError(
                "Sorry, RationalTime cannot be rescaled to a value of type "
                "'{}', only RationalTime and numbers are supported.".format(
                    type(new_rate)
                )
            )

    def __iadd__(self, other):
        if not isinstance(other, RationalTime):
            raise TypeError(
                "RationalTime may only be added to other objects of type "
                "RationalTime, not {}.".format(type(other))
            )

        if self.rate == other.rate:
            self.value += other.value
            return self

        if self.rate > other.rate:
            scale = self.rate
            value = (self.value + other.value_rescaled_to(scale))
        else:
            scale = other.rate
            value = (self.value_rescaled_to(scale) + other.value)

        self.value = value
        self.rate = scale

        return self

    def __add__(self, other):
        if not isinstance(other, RationalTime):
            raise TypeError(
                "RationalTime may only be added to other objects of type "
                "RationalTime, not {}.".format(type(other))
            )
        if self.rate == other.rate:
            return RationalTime(self.value + other.value, self.rate)
        elif self.rate > other.rate:
            scale = self.rate
            value = (self.value + other.value_rescaled_to(scale))
        else:
            scale = other.rate
            value = (self.value_rescaled_to(scale) + other.value)
        return RationalTime(value=value, rate=scale)

    def __sub__(self, other):
        if self.rate > other.rate:
            scale = self.rate
            value = (self.value - other.value_rescaled_to(scale))
        else:
            scale = other.rate
            value = (self.value_rescaled_to(scale) - other.value)
        return RationalTime(value=value, rate=scale)

    def _comparable_floats(self, other):
        """
        returns a tuple of two floats, (self, other), which are suitable
        for comparison.

        If other is not of a type that can be compared, TypeError is raised
        """
        if not isinstance(other, RationalTime):
            raise TypeError(
                "RationalTime can only be compared to other objects of type "
                "RationalTime, not {}".format(type(other))
            )
        return (
            float(self.value) / self.rate,
            float(other.value) / other.rate
        )

    def __gt__(self, other):
        f_self, f_other = self._comparable_floats(other)
        return f_self > f_other

    def __lt__(self, other):
        f_self, f_other = self._comparable_floats(other)
        return f_self < f_other

    def __le__(self, other):
        f_self, f_other = self._comparable_floats(other)
        return f_self <= f_other

    def __ge__(self, other):
        f_self, f_other = self._comparable_floats(other)
        return f_self >= f_other

    def __repr__(self):
        return (
            "otio.opentime.RationalTime(value={value},"
            " rate={rate})".format(
                value=repr(self.value),
                rate=repr(self.rate),
            )
        )

    def __str__(self):
        return "RationalTime({}, {})".format(
            str(self.value),
            str(self.rate)
        )

    def __eq__(self, other):
        try:
            return self.value_rescaled_to(other.rate) == other.value
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.value, self.rate))


class TimeTransform(object):

    """ 1D Transform for RationalTime.  Has offset and scale.  """

    def __init__(self, offset=RationalTime(), scale=1.0, rate=None):
        self.offset = offset
        self.scale = scale
        self.rate = rate

    def applied_to(self, other):
        if isinstance(other, TimeRange):
            return range_from_start_end_time(
                start_time=self.applied_to(other.start_time),
                end_time=self.applied_to(other.end_time())
            )

        target_rate = self.rate if self.rate is not None else other.rate
        if isinstance(other, TimeTransform):
            return TimeTransform(
                offset=self.offset + other.offset,
                scale=self.scale * other.scale,
                rate=target_rate
            )
        elif isinstance(other, RationalTime):
            result = RationalTime(0, other.rate)
            result.value = other.value * self.scale
            result = result + self.offset
            if target_rate is not None:
                result = result.rescaled_to(target_rate)

            return result
        else:
            raise TypeError(
                "TimeTransform can only be applied to a TimeTransform or "
                "RationalTime, not a {}".format(type(other))
            )

    def __repr__(self):
        return (
            "otio.opentime.TimeTransform(offset={}, scale={}, rate={})".format(
                repr(self.offset),
                repr(self.scale),
                repr(self.rate)
            )
        )

    def __str__(self):
        return (
            "TimeTransform({}, {}, {})".format(
                str(self.offset),
                str(self.scale),
                str(self.rate)
            )
        )

    def __eq__(self, other):
        try:
            return (
                (self.offset, self.scale, self.rate) ==
                (other.offset, other.scale, self.rate)
            )
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.offset, self.scale, self.rate))


class BoundStrategy(object):

    """ Different bounding strategies for TimeRange """
    Free = 1
    Clamp = 2


class TimeRange(object):

    """ Contains a range of time, [start_time, end_time()).

    end_time is computed, duration is stored.
    """

    def __init__(self, start_time=RationalTime(), duration=RationalTime()):
        self.start_time = start_time
        self.duration = duration

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, val):
        if not isinstance(val, RationalTime) or val.value < 0.0:
            raise TypeError(
                "duration must be a RationalTime with value >= 0, not "
                "'{}'".format(val)
            )
        self._duration = val

    def end_time(self):
        """" Compute and return the end point of the time range (inclusive).

        The end point of a range of frames is the FINAL frame, not the frame
        after.  This means that it is self.start_time + self.duration - 1
        """

        return self.start_time + self.duration

    def extended_by(self, other):
        """
        Extend the bounds by another TimeRange or RationalTime (without
        changing the start_bound or end_bound).
        """

        result = TimeRange(self.start_time, self.duration)
        end = self.end_time()
        if isinstance(other, RationalTime):
            result.start_time = min(other, self.start_time)
            end = max(other, end)
            result.duration = duration_from_start_end_time(
                result.start_time, end)
        elif isinstance(other, TimeRange):
            result.start_time = min(self.start_time, other.start_time)
            result.duration = max(self.duration, other.duration)
        else:
            raise TypeError(
                "extended_by requires rtime be a RationalTime or TimeRange, "
                "not a '{}'".format(type(other)))
        return result

    def clamped(
        self,
        other,
        start_bound=BoundStrategy.Free,
        end_bound=BoundStrategy.Free
    ):
        """
        Apply the range to either a RationalTime or a TimeRange.  If applied to
        a TimeRange, the resulting TimeRange will have the same boundary policy
        as other. (in other words, _not_ the same as self).
        """

        if isinstance(other, RationalTime):
            test_point = other
            if start_bound == BoundStrategy.Clamp:
                test_point = max(other, self.start_time)
            if end_bound == BoundStrategy.Clamp:
                test_point = min(test_point, self.end_time())
            return test_point
        elif isinstance(other, TimeRange):
            test_range = other
            end = test_range.end_time()
            if start_bound == BoundStrategy.Clamp:
                test_range.start_time = max(other.start_time, self.start_time)
            if end_bound == BoundStrategy.Clamp:
                end = min(test_range.end_time(), self.end_time())
                test_range.duration = end - test_range.start_time
            return test_range
        else:
            raise TypeError(
                "TimeRange can only be applied to RationalTime objects, not "
                "{}".format(type(other))
            )
        return self

    def contains(self, other):
        """
        Return true if self completely contains other.
        (RationalTime or TimeRange)
        """

        if isinstance(other, RationalTime):
            return (self.start_time <= other and other < self.end_time())
        elif isinstance(other, TimeRange):
            return (
                self.start_time <= other.start_time and
                self.end_time() >= other.end_time()
            )
        raise TypeError(
            "contains only accepts on otio.opentime.RationalTime or "
            "otio.opentime.TimeRange, not {}".format(type(other))
        )

    def overlaps(self, other):
        """
        Return true if self overlaps any part of other.
        (RationalTime or TimeRange)
        """

        if isinstance(other, RationalTime):
            return self.contains(other)
        elif isinstance(other, TimeRange):
            return (
                (
                    self.start_time < other.start_time and
                    self.end_time() > other.start_time) or
                (
                    self.end_time() > other.end_time() and
                    self.start_time < other.end_time()
                ) or
                (
                    self.start_time > other.start_time and
                    self.end_time() < other.end_time()
                )
            )
        raise TypeError(
            "overlaps only accepts on otio.opentime.RationalTime or "
            "otio.opentime.TimeRange, not {}".format(type(other))
        )

    def range_eq(self, other):
        """
        Only compare the time boundaries, not the bound policies, unlike
        __eq__.
        """
        try:
            return (
                self.start_time == other.start_time and
                self.duration == other.duration
            )
        except AttributeError:
            return False

    def __hash__(self):
        return hash(
            (self.start_time, self.duration)
        )

    def __eq__(self, rhs):
        try:
            return (self.start_time, self.duration) == (
                rhs.start_time, rhs.duration)
        except AttributeError:
            return False

    def __ne__(self, rhs):
        return not (self == rhs)

    def __repr__(self):
        return (
            "otio.opentime.TimeRange(start_time={}, duration={})".format(
                repr(self.start_time),
                repr(self.duration),
            )
        )

    def __str__(self):
        return (
            "TimeRange({}, {})".format(
                str(self.start_time),
                str(self.duration),
            )
        )


def from_frames(frame, fps):
    """
    Turn a frame number and fps into a time object.

    For any integer fps value, the rate will be the fps.
    For any common non-integer fps value (e.g. 29.97, 23.98) the time scale
    will be 600.
    """
    if int(fps) == fps:
        return RationalTime(frame, int(fps))
    elif int(fps * 600) == fps * 600:
        return RationalTime(frame * 600 / fps, 600)
    raise ValueError(
        "Non-standard frames per second ({}) not supported.".format(fps)
    )


def to_frames(time_obj, fps=None):
    """ Turn a RationalTime into a frame number.  """

    if not fps or time_obj.rate == fps:
        return time_obj.value

    # @TODO: should also do frame snapping here

    return time_obj.value_rescaled_to(fps)


def from_timecode(timecode_str, rate=24.0):
    """ Convert a timecode string into a RationalTime. """

    hours, minutes, seconds, frames = timecode_str.split(":")

    value = (
        (
            # convert to frames
            ((int(hours) * 60 + int(minutes)) * 60) + int(seconds)
        ) * 24.0 + int(frames)
    )

    return RationalTime(value, rate)


def to_timecode(time_obj):
    """ Convert a RationalTime into a timecode string.  """

    if time_obj is None:
        return None

    (total_seconds, frames) = divmod(time_obj.value, time_obj.rate)
    (total_minutes, seconds) = divmod(total_seconds, 60)
    (hours, minutes) = divmod(total_minutes, 60)

    channels = (hours, minutes, seconds, frames)

    return ":".join(
        ["{n:0{width}d}".format(n=int(n), width=2) for n in channels]
    )


def from_seconds(seconds):
    """ Convert a number of seconds into RationalTime """
    # Note: in the future we may consider adding a preferred rate arg
    time_obj = RationalTime(value=seconds, rate=1)

    return time_obj


def to_seconds(time_obj):
    """ Convert a RationalTime into float seconds """
    return time_obj.value_rescaled_to(1)


def from_footage(footage):
    raise NotImplementedError


def to_footage(time_obj):
    raise NotImplementedError


def duration_from_start_end_time(start_time, end_time):
    """
    Compute duration of samples from first to last. This is not the same as
    distance.  For example, the duration of a clip from frame 10 to frame 15
    is 6 frames.  Result in the rate of start_time.
    """

    if start_time.rate == end_time.rate:
        return RationalTime(
            end_time.value - start_time.value,
            start_time.rate
        )
    else:
        return RationalTime(
            end_time.value_rescaled_to(start_time) - start_time.value,
            start_time.rate
        )


def range_from_start_end_time(start_time, end_time):
    return TimeRange(
        start_time,
        duration=duration_from_start_end_time(start_time, end_time)
    )
