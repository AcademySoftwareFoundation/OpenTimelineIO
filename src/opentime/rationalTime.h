// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/errorStatus.h"
#include "opentime/version.h"
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

/// This enumeration provides options for drop frame timecode.
enum IsDropFrameRate : int
{
    InferFromRate = -1,
    ForceNo       = 0,
    ForceYes      = 1,
};

/// Returns the absolute value.
/// \todo Document why this function is used instead of "std::fabs()".
constexpr double
fabs(double val) noexcept
{
    union
    {
        double   f;
        uint64_t i;
    } bits = { val };
    bits.i &= std::numeric_limits<uint64_t>::max() / 2;
    return bits.f;
}

/// The RationalTime class represents a measure of time of "value/rate" seconds.
class RationalTime
{
public:
    explicit constexpr RationalTime(double value = 0, double rate = 1) noexcept
        : _value{ value }
        , _rate{ rate }
    {}

    /// Returns true if the time is invalid. The time is considered invalid if
    /// the value or the rate are a NaN value or if the rate is less than or
    /// equal to zero.
    bool is_invalid_time() const noexcept
    {
        return (std::isnan(_rate) || std::isnan(_value)) ? true : (_rate <= 0);
    }

    /// Returns the time value.
    constexpr double value() const noexcept { return _value; }

    /// Returns the time rate.
    constexpr double rate() const noexcept { return _rate; }

    /// Returns the time converted to a new rate.
    constexpr RationalTime rescaled_to(double new_rate) const noexcept
    {
        return RationalTime{ value_rescaled_to(new_rate), new_rate };
    }

    /// Returns the time converted to a new rate.
    constexpr RationalTime rescaled_to(RationalTime rt) const noexcept
    {
        return RationalTime{ value_rescaled_to(rt._rate), rt._rate };
    }

    /// Returns the time value converted to a new rate.
    constexpr double value_rescaled_to(double new_rate) const noexcept
    {
        return new_rate == _rate ? _value : (_value * new_rate) / _rate;
    }

    /// Returns the time value converted to a new rate.
    constexpr double value_rescaled_to(RationalTime rt) const noexcept
    {
        return value_rescaled_to(rt._rate);
    }

    /// Returns whether time is almost equal to another time, with a
    /// tolerance of delta.
    constexpr bool
    almost_equal(RationalTime other, double delta = 0) const noexcept
    {
        return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
    }

    /// Returns whether the value and rate are equal to another time. This
    /// is different from the operator "==" that rescales the time before
    /// comparison.
    constexpr bool strictly_equal(RationalTime other) const noexcept
    {
        return _value == other._value && _rate == other._rate;
    }

    /// Returns a time with the largest integer value not greater than
    /// this value.
    RationalTime floor() const
    {
        return RationalTime{ std::floor(_value), _rate };
    }

    /// Returns a time with the smallest integer value not less than
    /// this value.
    RationalTime ceil() const
    {
        return RationalTime{ std::ceil(_value), _rate };
    }

    /// Returns a time with the nearest integer value to this value.
    RationalTime round() const
    {
        return RationalTime{ std::round(_value), _rate };
    }

    /// Compute the duration of samples from first to last (excluding last).
    /// This is not the same as distance.
    ///
    /// For example, the duration of a clip from frame 10 to frame 15 is 5
    /// frames. Result will be in the rate of start time.
    static constexpr RationalTime duration_from_start_end_time(
        RationalTime start_time,
        RationalTime end_time_exclusive) noexcept
    {
        return start_time._rate == end_time_exclusive._rate
                   ? RationalTime{ end_time_exclusive._value
                                       - start_time._value,
                                   start_time._rate }
                   : RationalTime{ end_time_exclusive.value_rescaled_to(
                                       start_time)
                                       - start_time._value,
                                   start_time._rate };
    }

    /// Compute the duration of samples from first to last (including last).
    /// This is not the same as distance.
    ///
    /// For example, the duration of a clip from frame 10 to frame 15 is 6
    /// frames. Result will be in the rate of start time.
    static constexpr RationalTime duration_from_start_end_time_inclusive(
        RationalTime start_time,
        RationalTime end_time_inclusive) noexcept
    {
        return start_time._rate == end_time_inclusive._rate
                   ? RationalTime{ end_time_inclusive._value - start_time._value
                                       + 1,
                                   start_time._rate }
                   : RationalTime{ end_time_inclusive.value_rescaled_to(
                                       start_time)
                                       - start_time._value + 1,
                                   start_time._rate };
    }

    /// Returns true if the rate is valid for use with timecode.
    static bool is_valid_timecode_rate(double rate);

    /// Returns the first valid timecode rate that has the least difference
    /// from rate.
    static double nearest_valid_timecode_rate(double rate);

    /// Convert a frame number and rate into a time.
    static constexpr RationalTime
    from_frames(double frame, double rate) noexcept
    {
        return RationalTime{ double(int(frame)), rate };
    }

    /// Convert a value in seconds and rate into a time.
    static constexpr RationalTime
    from_seconds(double seconds, double rate) noexcept
    {
        return RationalTime{ seconds, 1 }.rescaled_to(rate);
    }

    /// Convert a value in seconds into a time.
    static constexpr RationalTime from_seconds(double seconds) noexcept
    {
        return RationalTime{ seconds, 1 };
    }

    /// Convert a timecode string ("HH:MM:SS;FRAME") into a time.
    static RationalTime from_timecode(
        std::string const& timecode,
        double             rate,
        ErrorStatus*       error_status = nullptr);

    /// Parse a string in the form "hours:minutes:seconds", which may have a
    /// leading negative sign. Seconds may have up to microsecond precision.
    static RationalTime from_time_string(
        std::string const& time_string,
        double             rate,
        ErrorStatus*       error_status = nullptr);

    /// Returns the frame number based on the current rate.
    constexpr int to_frames() const noexcept { return int(_value); }

    /// Returns the frame number based on the given rate.
    constexpr int to_frames(double rate) const noexcept
    {
        return int(value_rescaled_to(rate));
    }

    /// Returns the value in seconds.
    constexpr double to_seconds() const noexcept
    {
        return value_rescaled_to(1);
    }

    /// Convert to timecode (e.g., "HH:MM:SS;FRAME").
    std::string to_timecode(
        double          rate,
        IsDropFrameRate drop_frame,
        ErrorStatus*    error_status = nullptr) const;

    /// Convert to timecode (e.g., "HH:MM:SS;FRAME").
    std::string to_timecode(ErrorStatus* error_status = nullptr) const
    {
        return to_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
    }

    /// Convert to the nearest timecode (e.g., "HH:MM:SS;FRAME").
    std::string to_nearest_timecode(
        double          rate,
        IsDropFrameRate drop_frame,
        ErrorStatus*    error_status = nullptr) const;

    /// Convert to the nearest timecode (e.g., "HH:MM:SS;FRAME").
    std::string to_nearest_timecode(ErrorStatus* error_status = nullptr) const
    {
        return to_nearest_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
    }

    /// Produce a string in the form "hours:minutes:seconds", which may have a
    /// leading negative sign. Seconds may have up to microsecond precision.
    std::string to_time_string() const;

    constexpr RationalTime const& operator+=(RationalTime other) noexcept
    {
        if (_rate < other._rate)
        {
            _value = other._value + value_rescaled_to(other._rate);
            _rate  = other._rate;
        }
        else
        {
            _value += other.value_rescaled_to(_rate);
        }
        return *this;
    }

    constexpr RationalTime const& operator-=(RationalTime other) noexcept
    {
        if (_rate < other._rate)
        {
            _value = value_rescaled_to(other._rate) - other._value;
            _rate  = other._rate;
        }
        else
        {
            _value -= other.value_rescaled_to(_rate);
        }
        return *this;
    }

    friend constexpr RationalTime
    operator+(RationalTime lhs, RationalTime rhs) noexcept
    {
        return (lhs._rate < rhs._rate)
                   ? RationalTime{ lhs.value_rescaled_to(rhs._rate)
                                       + rhs._value,
                                   rhs._rate }
                   : RationalTime{ rhs.value_rescaled_to(lhs._rate)
                                       + lhs._value,
                                   lhs._rate };
    }

    friend constexpr RationalTime
    operator-(RationalTime lhs, RationalTime rhs) noexcept
    {
        return (lhs._rate < rhs._rate)
                   ? RationalTime{ lhs.value_rescaled_to(rhs._rate)
                                       - rhs._value,
                                   rhs._rate }
                   : RationalTime{ lhs._value
                                       - rhs.value_rescaled_to(lhs._rate),
                                   lhs._rate };
    }

    friend constexpr RationalTime operator-(RationalTime lhs) noexcept
    {
        return RationalTime{ -lhs._value, lhs._rate };
    }

    friend constexpr bool operator>(RationalTime lhs, RationalTime rhs) noexcept
    {
        return (lhs._value / lhs._rate) > (rhs._value / rhs._rate);
    }

    friend constexpr bool
    operator>=(RationalTime lhs, RationalTime rhs) noexcept
    {
        return (lhs._value / lhs._rate) >= (rhs._value / rhs._rate);
    }

    friend constexpr bool operator<(RationalTime lhs, RationalTime rhs) noexcept
    {
        return !(lhs >= rhs);
    }

    friend constexpr bool
    operator<=(RationalTime lhs, RationalTime rhs) noexcept
    {
        return !(lhs > rhs);
    }

    friend constexpr bool
    operator==(RationalTime lhs, RationalTime rhs) noexcept
    {
        return lhs.value_rescaled_to(rhs._rate) == rhs._value;
    }

    friend constexpr bool
    operator!=(RationalTime lhs, RationalTime rhs) noexcept
    {
        return !(lhs == rhs);
    }

private:
    static RationalTime     _invalid_time;
    static constexpr double _invalid_rate = -1;

    friend class TimeTransform;
    friend class TimeRange;

    double _value, _rate;
};

}} // namespace opentime::OPENTIME_VERSION
