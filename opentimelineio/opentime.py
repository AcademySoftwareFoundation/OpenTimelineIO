#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

"""Library for expressing and transforming time.

NOTE: This module is written specifically with a future port to C in mind.
When ported to C, Time will be a struct and these functions should be very
simple.
"""

import math
import copy
import numbers


VALID_NON_DROPFRAME_TIMECODE_RATES = (
    1,
    12,
    23.976,
    23.98,
    24,
    25,
    30,
    48,
    50,
    60)

VALID_DROPFRAME_TIMECODE_RATES = (
    29.97,
    59.94)

VALID_TIMECODE_RATES = (
    VALID_NON_DROPFRAME_TIMECODE_RATES + VALID_DROPFRAME_TIMECODE_RATES)

_fn_cache = object.__setattr__


class RationalTime(object):
    """ Represents an instantaneous point in time, value * (1/rate) seconds
    from time 0seconds.
    """

    # Locks RationalTime instances to only these attributes
    __slots__ = ['value', 'rate']

    def __init__(self, value=0.0, rate=1.0):
        _fn_cache(self, "value", value)
        _fn_cache(self, "rate", rate)

    def __setattr__(self, key, val):
        """Enforces immutability """
        raise AttributeError("RationalTime is Immutable.")

    def __copy__(self, memodict=None):
        return RationalTime(self.value, self.rate)

    # Always deepcopy, since we want this class to behave like a value type
    __deepcopy__ = __copy__

    def rescaled_to(self, new_rate):
        """Returns the time for this time converted to new_rate"""

        try:
            new_rate = new_rate.rate
        except AttributeError:
            pass

        if self.rate == new_rate:
            return copy.copy(self)

        return RationalTime(
            self.value_rescaled_to(new_rate),
            new_rate
        )

    def value_rescaled_to(self, new_rate):
        """Returns the time value for self converted to new_rate"""

        try:
            new_rate = new_rate.rate
        except AttributeError:
            pass

        if new_rate == self.rate:
            return self.value

        # TODO: This math probably needs some overrun protection
        try:
            return float(self.value) * float(new_rate) / float(self.rate)
        except (AttributeError, TypeError, ValueError):
            raise TypeError(
                "Sorry, RationalTime cannot be rescaled to a value of type "
                "'{}', only RationalTime and numbers are supported.".format(
                    type(new_rate)
                )
            )

    def almost_equal(self, other, delta=0.0):
        try:
            rescaled_value = self.value_rescaled_to(other.rate)
            return abs(rescaled_value - other.value) <= delta

        except AttributeError:
            return False

    def __add__(self, other):
        """Returns a RationalTime object that is the sum of self and other.

        If self and other have differing time rates, the result will have the
        have the rate of the faster time.
        """

        try:
            if self.rate == other.rate:
                return RationalTime(self.value + other.value, self.rate)
        except AttributeError:
            if not isinstance(other, RationalTime):
                raise TypeError(
                    "RationalTime may only be added to other objects of type "
                    "RationalTime, not {}.".format(type(other))
                )
            raise

        if self.rate > other.rate:
            scale = self.rate
            value = self.value + other.value_rescaled_to(scale)
        else:
            scale = other.rate
            value = self.value_rescaled_to(scale) + other.value

        return RationalTime(value, scale)

    # because RationalTime is immutable, += is sugar around +
    __iadd__ = __add__

    def __mul__(self, scale):
        if not isinstance(scale, numbers.Number):
            raise TypeError(
                "RationalTime may only be multiplied by objects of type "
                "{}, not {}.".format(numbers.Number, type(scale))
            )

        return RationalTime(self.value * scale, self.rate)

    __imul__ = __mul__

    def __sub__(self, other):
        """Returns a RationalTime object that is self - other.

        If self and other have differing time rates, the result will have the
        have the rate of the faster time.
        """

        try:
            if self.rate == other.rate:
                return RationalTime(self.value - other.value, self.rate)
        except AttributeError:
            if not isinstance(other, RationalTime):
                raise TypeError(
                    "RationalTime may only be added to other objects of type "
                    "RationalTime, not {}.".format(type(other))
                )
            raise

        if self.rate > other.rate:
            scale = self.rate
            value = self.value - other.value_rescaled_to(scale)
        else:
            scale = other.rate
            value = self.value_rescaled_to(scale) - other.value

        return RationalTime(value=value, rate=scale)

    def _comparable_floats(self, other):
        """Returns a tuple of two floats, (self, other), which are suitable
        for comparison.

        If other is not of a type that can be compared, TypeError is raised
        """
        try:
            return (
                float(self.value) / self.rate,
                float(other.value) / other.rate
            )
        except AttributeError:
            if not isinstance(other, RationalTime):
                raise TypeError(
                    "RationalTime can only be compared to other objects of type "
                    "RationalTime, not {}".format(type(other))
                )
            raise

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
    """Represents a homogenous-coordinates transform matrix of the form:
    | Scale Offset |
    |   0     1    | (Implicit)

    TimeTransform may be composed with other Time Transforms:
    TT*TT => TT
    or on the right with RationalTime or with TimeRange:
    TT*RT => RT
    TT*TR => TR

    Resulting RationalTime/TimeRange will be in the rate of the RT/TR, not the
    TimeTransform.

    TT1 * TT2 =
    | Scale1 * Scale2   Scale1*Offset2 + Offset1 |
    |        0                         1         | (Implicit)
    """

    __slots__ = ['scale', 'offset']

    def __init__(self, scale=1.0, offset=None):
        if not isinstance(scale, numbers.Number):
            raise TypeError(
                "scale must be a {}, not a {}".format(numbers.Number, type(scale))
            )
        _fn_cache(self, "scale", scale)

        if offset is None:
            offset = RationalTime()

        if not isinstance(offset, RationalTime):
            raise TypeError(
                "start_time must be a RationalTime, not "
                "'{}'".format(offset)
            )
        _fn_cache(self, "offset", offset)

    def __setattr__(self, key, val):
        raise AttributeError("TimeTransform is Immutable.")

    def __mul__(self, other):
        if isinstance(other, TimeRange):
            return range_from_start_end_time(
                start_time=self * other.start_time,
                end_time_exclusive=self * other.end_time_exclusive()
            )
        elif isinstance(other, RationalTime):
            # @TODO: This returns a RationalTime in the higher rate, which is
            #        the behavior of the RationalTime + method.  We should
            #        consider this and see if there is a preferred alternative
            #        behavior.
            return (
                other * self.scale
                + self.offset
            )
        elif isinstance(other, TimeTransform):
            return TimeTransform(
                scale=self.scale * other.scale,
                offset=other.offset * self.scale + self.offset
            )
        else:
            raise TypeError(
                "TimeTransform can only be multiplied with a TimeRange, "
                "TimeTransform or RationalTime, not a {}".format(type(other))
            )

    def inverted(self):
        """Return the inverse of this time transform.

        ** assumes that scale is non-zero **

        Because the TimeTransform is a 2x2 matrix of the form:
            | scale offset |
            |   0     1    |

        The inverse is:
            | 1/scale -offset/scale |
            |   0           1       |

        To derive this:
            | A B | * | S O |   | 1 0 |
            | C D |   | 0 1 | = | 0 1 |
            =>
            A*S = 1 => A = 1/S
            A*O + B = 0 => B = -O/S
            C * S = 0 => C = 0
            C * O + D = 1 => D = 1
        """

        if self.scale == 0:
            raise RuntimeError("Cannot invert transform with scale of 0.")

        inv_float_scale = 1 / float(self.scale)

        return TimeTransform(
            scale=inv_float_scale,
            offset=RationalTime(
                (- self.offset.value) * inv_float_scale,
                self.offset.rate
            )
        )

    def __repr__(self):
        return (
            "otio.opentime.TimeTransform(scale={}, offset={})".format(
                repr(self.scale),
                repr(self.offset)
            )
        )

    def __str__(self):
        return (
            "TimeTransform({}, {})".format(
                str(self.scale),
                str(self.offset)
            )
        )

    def __eq__(self, other):
        try:
            return (
                (self.scale, self.offset) ==
                (other.scale, other.offset)
            )
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.scale, self.offset))


class BoundStrategy(object):
    """Different bounding strategies for TimeRange """

    Free = 1
    Clamp = 2


class TimeRange(object):
    """Contains a range of time, starting (and including) start_time and
    lasting duration.value * (1/duration.rate) seconds.

    A 0 duration TimeRange is the same as a RationalTime, and contains only the
    start_time of the TimeRange.
    """

    __slots__ = ['start_time', 'duration']

    def __init__(self, start_time=None, duration=None):
        if not isinstance(start_time, RationalTime) and start_time is not None:
            raise TypeError(
                "start_time must be a RationalTime, not "
                "'{}'".format(start_time)
            )
        if (
                duration is not None and (
                    not isinstance(duration, RationalTime)
                    or duration.value < 0.0
                )
        ):
            raise TypeError(
                "duration must be a RationalTime with value >= 0, not "
                "'{}'".format(duration)
            )

        # if the start time has not been passed in
        if not start_time:
            if duration:
                # ...get the rate from the duration
                start_time = RationalTime(rate=duration.rate)
            else:
                # otherwise use the default
                start_time = RationalTime()
        _fn_cache(self, "start_time", copy.copy(start_time))

        if not duration:
            # ...get the rate from the start_time
            duration = RationalTime(rate=start_time.rate)
        _fn_cache(self, "duration", copy.copy(duration))

    def __setattr__(self, key, val):
        raise AttributeError("TimeRange is Immutable.")

    def __copy__(self, memodict=None):
        # Construct a new one directly to avoid the overhead of deepcopy
        return TimeRange(
            copy.copy(self.start_time),
            copy.copy(self.duration)
        )

    # Always deepcopy, since we want this class to behave like a value type
    __deepcopy__ = __copy__

    def end_time_inclusive(self):
        """The time of the last sample that contains data in the TimeRange.

        If the TimeRange goes from (0, 24) w/ duration (10, 24), this will be
        (9, 24)

        If the TimeRange goes from (0, 24) w/ duration (10.5, 24):
        (10, 24)

        In other words, the last frame with data (however fractional).
        """

        if (
            self.end_time_exclusive() - self.start_time.rescaled_to(self.duration)
        ).value > 1:

            result = (
                self.end_time_exclusive() - RationalTime(1, self.start_time.rate)
            )

            # if the duration's value has a fractional component
            if self.duration.value != math.floor(self.duration.value):
                result = RationalTime(
                    math.floor(self.end_time_exclusive().value),
                    result.rate
                )

            return result
        else:
            return copy.deepcopy(self.start_time)

    def end_time_exclusive(self):
        """"Time of the first sample outside the time range.

        If Start Frame is 10 and duration is 5, then end_time_exclusive is 15,
        even though the last time with data in this range is 14.

        If Start Frame is 10 and duration is 5.5, then end_time_exclusive is
        15.5, even though the last time with data in this range is 15.
        """

        return self.duration + self.start_time.rescaled_to(self.duration)

    def extended_by(self, other):
        """Construct a new TimeRange that is this one extended by another."""

        if not isinstance(other, TimeRange):
            raise TypeError(
                "extended_by requires rtime be a TimeRange, not a '{}'".format(
                    type(other)
                )
            )

        start_time = min(self.start_time, other.start_time)
        new_end_time = max(
            self.end_time_exclusive(),
            other.end_time_exclusive()
        )
        duration = duration_from_start_end_time(start_time, new_end_time)
        return TimeRange(start_time, duration)

    # @TODO: remove?
    def clamped(
        self,
        other,
        start_bound=BoundStrategy.Free,
        end_bound=BoundStrategy.Free
    ):
        """Clamp 'other' (either a RationalTime or a TimeRange), according to
        self.start_time/end_time_exclusive and the bound arguments.
        """

        if isinstance(other, RationalTime):
            if start_bound == BoundStrategy.Clamp:
                other = max(other, self.start_time)
            if end_bound == BoundStrategy.Clamp:
                # @TODO: this should probably be the end_time_inclusive,
                # not exclusive
                other = min(other, self.end_time_exclusive())
            return other
        elif isinstance(other, TimeRange):
            start_time = other.start_time
            end = other.end_time_exclusive()
            if start_bound == BoundStrategy.Clamp:
                start_time = max(other.start_time, self.start_time)
            if end_bound == BoundStrategy.Clamp:
                end = min(self.end_time_exclusive(), end)
            duration = duration_from_start_end_time(start_time, end)
            return TimeRange(start_time, duration)
        else:
            raise TypeError(
                "TimeRange can only be applied to RationalTime objects, not "
                "{}".format(type(other))
            )
        return self

    def contains(self, other):
        """Return true if self completely contains other.

        (RationalTime or TimeRange)
        """

        if isinstance(other, RationalTime):
            return (
                self.start_time <= other and other < self.end_time_exclusive())
        elif isinstance(other, TimeRange):
            return (
                self.start_time <= other.start_time and
                self.end_time_exclusive() >= other.end_time_exclusive()
            )
        raise TypeError(
            "contains only accepts on otio.opentime.RationalTime or "
            "otio.opentime.TimeRange, not {}".format(type(other))
        )

    def overlaps(self, other):
        """Return true if self overlaps any part of other.

        (RationalTime or TimeRange)
        """

        if isinstance(other, RationalTime):
            return self.contains(other)
        elif isinstance(other, TimeRange):
            return (
                (
                    self.start_time < other.end_time_exclusive() and
                    other.start_time < self.end_time_exclusive()
                )
            )
        raise TypeError(
            "overlaps only accepts on otio.opentime.RationalTime or "
            "otio.opentime.TimeRange, not {}".format(type(other))
        )

    def __hash__(self):
        return hash((self.start_time, self.duration))

    def __eq__(self, rhs):
        try:
            return (
                (self.start_time, self.duration) ==
                (rhs.start_time, rhs.duration)
            )
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
    """Turn a frame number and fps into a time object.
    :param frame: (:class:`int`) Frame number.
    :param fps: (:class:`float`) Frame-rate for the (:class:`RationalTime`) instance.

    :return: (:class:`RationalTime`) Instance for the frame and fps provided.
    """

    return RationalTime(int(frame), fps)


def to_frames(time_obj, fps=None):
    """Turn a RationalTime into a frame number."""

    if not fps or time_obj.rate == fps:
        return int(time_obj.value)

    return int(time_obj.value_rescaled_to(fps))


def validate_timecode_rate(rate):
    """Check if rate is of valid type and value.
    Raises (:class:`TypeError` for wrong type of rate.
    Raises (:class:`VaueError`) for invalid rate value.

    :param rate: (:class:`int`) or (:class:`float`) The frame rate in question
    """
    if not isinstance(rate, (int, float)):
        raise TypeError(
            "rate must be <float> or <int> not {t}".format(t=type(rate)))

    if rate not in VALID_TIMECODE_RATES:
        raise ValueError(
            '{rate} is not a valid frame rate, '
            'Please use one of these: {valid}'.format(
                rate=rate,
                valid=VALID_TIMECODE_RATES))


def from_timecode(timecode_str, rate):
    """Convert a timecode string into a RationalTime.

    :param timecode_str: (:class:`str`) A colon-delimited timecode.
    :param rate: (:class:`float`) The frame-rate to calculate timecode in
        terms of.

    :return: (:class:`RationalTime`) Instance for the timecode provided.
    """
    # Validate rate
    validate_timecode_rate(rate)

    # Check if rate is drop frame
    rate_is_dropframe = rate in VALID_DROPFRAME_TIMECODE_RATES

    # Check if timecode indicates drop frame
    if ';' in timecode_str:
        if not rate_is_dropframe:
            raise ValueError(
                'Timecode "{}" indicates drop-frame rate '
                'due to the ";" frame divider. '
                'Passed rate ({}) is of non-drop-frame rate. '
                'Valid drop-frame rates are: {}'.format(
                    timecode_str,
                    rate,
                    VALID_DROPFRAME_TIMECODE_RATES))
        else:
            timecode_str = timecode_str.replace(';', ':')

    hours, minutes, seconds, frames = timecode_str.split(":")

    # Timecode is declared in terms of nominal fps
    nominal_fps = int(math.ceil(rate))

    if int(frames) >= nominal_fps:
        raise ValueError(
            'Frame rate mismatch. Timecode "{}" has frames beyond {}.'.format(
                timecode_str, nominal_fps - 1))

    dropframes = 0
    if rate_is_dropframe:
        if rate == 29.97:
            dropframes = 2

        elif rate == 59.94:
            dropframes = 4

    # To use for drop frame compensation
    total_minutes = int(hours) * 60 + int(minutes)

    # convert to frames
    value = (
        ((total_minutes * 60) + int(seconds)) * nominal_fps + int(frames)) - \
        (dropframes * (total_minutes - (total_minutes // 10)))

    return RationalTime(value, rate)


def to_timecode(time_obj, rate=None):
    """Convert a RationalTime into a timecode string.

    :param time_obj: (:class:`RationalTime`) instance to express as timecode.
    :param rate: (:class:`float`) The frame-rate to calculate timecode in
        terms of. (Default time_obj.rate)

    :return: (:class:`str`) The timecode.
    """
    if time_obj is None:
        return None

    rate = rate or time_obj.rate

    # Validate rate
    validate_timecode_rate(rate)

    # Check if rate is drop frame
    rate_is_dropframe = rate in VALID_DROPFRAME_TIMECODE_RATES

    if not rate_is_dropframe:
        # Check for variantions of ~24 fps and convert to 24 for calculations
        if round(rate) == 24:
            rate = round(rate)

    dropframes = 0
    if rate_is_dropframe:
        if rate == 29.97:
            dropframes = 2

        elif rate == 59.94:
            dropframes = 4

    # Number of frames in an hour
    frames_per_hour = int(round(rate * 60 * 60))
    # Number of frames in a day - timecode rolls over after 24 hours
    frames_per_24_hours = frames_per_hour * 24
    # Number of frames per ten minutes
    frames_per_10_minutes = int(round(rate * 60 * 10))
    # Number of frames per minute is the round of the framerate * 60 minus
    # the number of dropped frames
    frames_per_minute = int(round(rate) * 60) - dropframes

    value = time_obj.value

    if value < 0:
        raise ValueError(
            "Negative values are not supported for converting to timecode.")

    # If frame_number is greater than 24 hrs, next operation will rollover
    # clock
    value %= frames_per_24_hours

    if rate_is_dropframe:
        d = value // frames_per_10_minutes
        m = value % frames_per_10_minutes
        if m > dropframes:
            value += (dropframes * 9 * d) + \
                dropframes * ((m - dropframes) // frames_per_minute)
        else:
            value += dropframes * 9 * d

    nominal_fps = int(math.ceil(rate))

    frames = value % nominal_fps
    seconds = (value // nominal_fps) % 60
    minutes = ((value // nominal_fps) // 60) % 60
    hours = (((value // nominal_fps) // 60) // 60)

    tc = "{HH:02d}:{MM:02d}:{SS:02d}{div}{FF:02d}"

    return tc.format(
        HH=int(hours),
        MM=int(minutes),
        SS=int(seconds),
        div=rate_is_dropframe and ";" or ":",
        FF=int(frames))


def from_time_string(time_str, rate):
    """Convert a time with microseconds string into a RationalTime.

    :param time_str: (:class:`str`) A HH:MM:ss.ms time.
    :param rate: (:class:`float`) The frame-rate to calculate timecode in
        terms of.

    :return: (:class:`RationalTime`) Instance for the timecode provided.
    """

    if ';' in time_str:
        raise ValueError('Drop-Frame timecodes not supported.')

    hours, minutes, seconds = time_str.split(":")
    microseconds = "0"
    if '.' in seconds:
        seconds, microseconds = str(seconds).split('.')
    microseconds = microseconds[0:6]
    seconds = '.'.join([seconds, microseconds])
    time_obj = from_seconds(
        float(seconds) +
        (int(minutes) * 60) +
        (int(hours) * 60 * 60)
    )
    return time_obj.rescaled_to(rate)


def to_time_string(time_obj):
    """
    Convert this timecode to time with microsecond, as formated in FFMPEG

    :return: Number formated string of time
    """
    if time_obj is None:
        return None
    # convert time object to seconds
    seconds = to_seconds(time_obj)

    # reformat in time string
    time_units_per_minute = 60
    time_units_per_hour = time_units_per_minute * 60
    time_units_per_day = time_units_per_hour * 24

    days, hour_units = divmod(seconds, time_units_per_day)
    hours, minute_units = divmod(hour_units, time_units_per_hour)
    minutes, seconds = divmod(minute_units, time_units_per_minute)
    microseconds = "0"
    seconds = str(seconds)
    if '.' in seconds:
        seconds, microseconds = str(seconds).split('.')

    # TODO: There are some rollover policy issues for days and hours,
    #       We need to research these

    return "{hours}:{minutes}:{seconds}.{microseconds}".format(
        hours="{n:0{width}d}".format(n=int(hours), width=2),
        minutes="{n:0{width}d}".format(n=int(minutes), width=2),
        seconds="{n:0{width}d}".format(n=int(seconds), width=2),
        microseconds=microseconds[0:6]
    )


def from_seconds(seconds):
    """Convert a number of seconds into RationalTime"""

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


def duration_from_start_end_time(start_time, end_time_exclusive):
    """Compute duration of samples from first to last. This is not the same as
    distance.  For example, the duration of a clip from frame 10 to frame 15
    is 6 frames.  Result in the rate of start_time.
    """

    # @TODO: what to do when start_time > end_time_exclusive?

    if start_time.rate == end_time_exclusive.rate:
        return RationalTime(
            end_time_exclusive.value - start_time.value,
            start_time.rate
        )
    else:
        return RationalTime(
            (
                end_time_exclusive.value_rescaled_to(start_time)
                - start_time.value
            ),
            start_time.rate
        )


# @TODO: create range from start/end [in,ex]clusive
def range_from_start_end_time(start_time, end_time_exclusive):
    """Create a TimeRange from start and end RationalTimes."""

    return TimeRange(
        start_time,
        duration=duration_from_start_end_time(start_time, end_time_exclusive)
    )
