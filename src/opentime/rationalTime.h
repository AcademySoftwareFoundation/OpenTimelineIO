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

/// @brief This enumeration provides options for drop frame timecode.
enum IsDropFrameRate : int
{
    InferFromRate = -1,
    ForceNo       = 0,
    ForceYes      = 1,
};

/// @brief Returns the absolute value.
///
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

/// @brief This class represents a measure of time defined by a value and rate.
class RationalTime
{
public:
    /// @brief Construct a new time with an optional value and rate.
    explicit constexpr RationalTime(double value = 0, double rate = 1) noexcept
        : _value{ value }
        , _rate{ rate }
    {}

    /// @brief Returns true if the time is invalid.
    ///
    /// The time is considered invalid if the value or rate are a NaN value,
    /// or if the rate is less than or equal to zero.
    bool is_invalid_time() const noexcept
    {
        return (std::isnan(_rate) || std::isnan(_value)) ? true : (_rate <= 0);
    }

    /// @brief Returns the time value.
    constexpr double value() const noexcept { return _value; }

    /// @brief Returns the time rate.
    constexpr double rate() const noexcept { return _rate; }

    /// @brief Returns the time converted to a new rate.
    constexpr RationalTime rescaled_to(double new_rate) const noexcept
    {
        return RationalTime{ value_rescaled_to(new_rate), new_rate };
    }

    /// @brief Returns the time converted to a new rate.
    constexpr RationalTime rescaled_to(RationalTime rt) const noexcept
    {
        return RationalTime{ value_rescaled_to(rt._rate), rt._rate };
    }

    /// @brief Returns the time value converted to a new rate.
    constexpr double value_rescaled_to(double new_rate) const noexcept
    {
        return new_rate == _rate ? _value : (_value * new_rate) / _rate;
    }

    /// @brief Returns the time value converted to a new rate.
    constexpr double value_rescaled_to(RationalTime rt) const noexcept
    {
        return value_rescaled_to(rt._rate);
    }

    /// @brief Returns whether time is almost equal to another time.
    ///
    /// @param other The other time for comparison.
    /// @param delta The tolerance used for the comparison.
    constexpr bool
    almost_equal(RationalTime other, double delta = 0) const noexcept
    {
        return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
    }

    /// @brief Returns whether the value and rate are equal to another time.
    ///
    /// This is different from the operator "==" that rescales the time before
    /// comparison.
    constexpr bool strictly_equal(RationalTime other) const noexcept
    {
        return _value == other._value && _rate == other._rate;
    }

    /// @brief Returns a time with the largest integer value not greater than
    /// this value.
    RationalTime floor() const
    {
        return RationalTime{ std::floor(_value), _rate };
    }

    /// @brief Returns a time with the smallest integer value not less than
    /// this value.
    RationalTime ceil() const
    {
        return RationalTime{ std::ceil(_value), _rate };
    }

    /// @brief Returns a time with the nearest integer value to this value.
    RationalTime round() const
    {
        return RationalTime{ std::round(_value), _rate };
    }

    /// @brief Compute the duration of samples from first to last (excluding
    /// last).
    ///
    /// Note that this is not the same as distance.
    ///
    /// For example, the duration of a clip from frame 10 to frame 15 is 5
    /// frames. The result will be in the rate of start time.
    ///
    /// @param start_time The start time.
    /// @param end_time_exclusive The exclusive end time.
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

    /// @brief Compute the duration of samples from first to last (including
    /// last).
    ///
    /// Note that this is not the same as distance.
    ///
    /// For example, the duration of a clip from frame 10 to frame 15 is 6
    /// frames. Result will be in the rate of start time.
    ///
    /// @param start_time The start time.
    /// @param end_time_exclusive The inclusive end time.
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

    /// @brief Returns true if the rate is valid for use with timecode.
    static bool is_valid_timecode_rate(double rate);

    /// @brief Returns the first valid timecode rate that has the least
    /// difference from rate.
    static double nearest_valid_timecode_rate(double rate);

    /// @brief Convert a frame number and rate into a time.
    static constexpr RationalTime
    from_frames(double frame, double rate) noexcept
    {
        return RationalTime{ double(int(frame)), rate };
    }

    /// @brief Convert a value in seconds and rate into a time.
    static constexpr RationalTime
    from_seconds(double seconds, double rate) noexcept
    {
        return RationalTime{ seconds, 1 }.rescaled_to(rate);
    }

    /// @brief Convert a value in seconds into a time.
    static constexpr RationalTime from_seconds(double seconds) noexcept
    {
        return RationalTime{ seconds, 1 };
    }

    /// @brief Convert a timecode string ("HH:MM:SS;FRAME") into a time.
    ///
    /// @param timecode The timecode string.
    /// @param rate The timecode rate.
    /// @param error_status Optional error status.
    static RationalTime from_timecode(
        std::string const& timecode,
        double             rate,
        ErrorStatus*       error_status = nullptr);

    /// @brief Parse a string in the form "hours:minutes:seconds".
    ///
    /// The string may have a leading negative sign.
    ///
    /// Seconds may have up to microsecond precision.
    ///
    /// @param time_string The time string.
    /// @param rate The time rate.
    /// @param error_status Optional error status.
    static RationalTime from_time_string(
        std::string const& time_string,
        double             rate,
        ErrorStatus*       error_status = nullptr);

    /// @brief Returns the frame number based on the current rate.
    constexpr int to_frames() const noexcept { return int(_value); }

    /// @brief Returns the frame number based on the given rate.
    constexpr int to_frames(double rate) const noexcept
    {
        return int(value_rescaled_to(rate));
    }

    /// @brief Returns the value in seconds.
    constexpr double to_seconds() const noexcept
    {
        return value_rescaled_to(1);
    }

    /// @brief Convert to timecode (e.g., "HH:MM:SS;FRAME").
    ///
    /// @param rate The timecode rate.
    /// @param drop_frame Whether to use drop frame timecode.
    /// @param error_status Optional error status.
    std::string to_timecode(
        double          rate,
        IsDropFrameRate drop_frame,
        ErrorStatus*    error_status = nullptr) const;

    /// @brief Convert to timecode (e.g., "HH:MM:SS;FRAME").
    std::string to_timecode(ErrorStatus* error_status = nullptr) const
    {
        return to_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
    }

    /// @brief Convert to the nearest timecode (e.g., "HH:MM:SS;FRAME").
    ///
    /// @param rate The timecode rate.
    /// @param drop_frame Whether to use drop frame timecode.
    /// @param error_status Optional error status.
    std::string to_nearest_timecode(
        double          rate,
        IsDropFrameRate drop_frame,
        ErrorStatus*    error_status = nullptr) const;

    /// @brief Convert to the nearest timecode (e.g., "HH:MM:SS;FRAME").
    std::string to_nearest_timecode(ErrorStatus* error_status = nullptr) const
    {
        return to_nearest_timecode(
            _rate,
            IsDropFrameRate::InferFromRate,
            error_status);
    }

    /// @brief Return a string in the form "hours:minutes:seconds".
    ///
    /// Seconds may have up to microsecond precision.
    ///
    /// @return The time string, which may have a leading negative sign.
    std::string to_time_string() const;

    /// @brief Add a time to this time.
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

    /// @brief Subtract a time from this time.
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

    /// @brief Return the addition of two times.
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

    /// @brief Return the subtraction of two times.
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

    /// @brief Return the negative of this time.
    friend constexpr RationalTime operator-(RationalTime lhs) noexcept
    {
        return RationalTime{ -lhs._value, lhs._rate };
    }

    /// @brief Return whether a time is greater than another time.
    friend constexpr bool operator>(RationalTime lhs, RationalTime rhs) noexcept
    {
        return (lhs._value / lhs._rate) > (rhs._value / rhs._rate);
    }

    /// @brief Return whether a time is greater or equal to another time.
    friend constexpr bool
    operator>=(RationalTime lhs, RationalTime rhs) noexcept
    {
        return (lhs._value / lhs._rate) >= (rhs._value / rhs._rate);
    }

    /// @brief Return whether a time is less than another time.
    friend constexpr bool operator<(RationalTime lhs, RationalTime rhs) noexcept
    {
        return !(lhs >= rhs);
    }

    /// @brief Return whether a time is less than or equal to another time.
    friend constexpr bool
    operator<=(RationalTime lhs, RationalTime rhs) noexcept
    {
        return !(lhs > rhs);
    }

    /// @brief Return whether two times are equal.
    ///
    /// Note that the right hand side time is rescaled to the rate of the
    /// left hand side time. To compare two times without scaling, use
    /// strictly_equal().
    ///
    /// @param lhs Left hand side time.
    /// @param lhs Right hand side time.
    friend constexpr bool
    operator==(RationalTime lhs, RationalTime rhs) noexcept
    {
        return lhs.value_rescaled_to(rhs._rate) == rhs._value;
    }

    /// @brief Return whether two times are not equal.
    ///
    /// Note that the right hand side time is rescaled to the rate of the
    /// left hand side time. To compare two times without scaling, use
    /// strictly_equal().
    ///
    /// @param lhs Left hand side time.
    /// @param lhs Right hand side time.
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
