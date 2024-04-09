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

enum IsDropFrameRate : int
{
    InferFromRate = -1,
    ForceNo       = 0,
    ForceYes      = 1,
};

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

class RationalTime
{
public:
    explicit constexpr RationalTime(double value = 0, double rate = 1) noexcept
        : _value{ value }
        , _rate{ rate }
    {}

    bool is_invalid_time() const noexcept
    {
        return (std::isnan(_rate) || std::isnan(_value)) ? true : (_rate <= 0);
    }

    constexpr double value() const noexcept { return _value; }

    constexpr double rate() const noexcept { return _rate; }

    constexpr RationalTime rescaled_to(double new_rate) const noexcept
    {
        return RationalTime{ value_rescaled_to(new_rate), new_rate };
    }

    constexpr RationalTime rescaled_to(RationalTime rt) const noexcept
    {
        return RationalTime{ value_rescaled_to(rt._rate), rt._rate };
    }

    constexpr double value_rescaled_to(double new_rate) const noexcept
    {
        return new_rate == _rate ? _value : (_value * new_rate) / _rate;
    }

    constexpr double value_rescaled_to(RationalTime rt) const noexcept
    {
        return value_rescaled_to(rt._rate);
    }

    constexpr bool
    almost_equal(RationalTime other, double delta = 0) const noexcept
    {
        return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
    }

    // Return whether the value and rate are equal to another RationalTime.
    // This is different from the operator "==" that rescales the time before
    // comparison.
    constexpr bool strictly_equal(RationalTime other) const noexcept
    {
        return _value == other._value && _rate == other._rate;
    }

    // Return a RationalTime with the largest integer value not greater than
    // this value.
    RationalTime floor() const
    {
        return RationalTime{ std::floor(_value), _rate };
    }

    // Return a RationalTime with the smallest integer value not less than
    // this value.
    RationalTime ceil() const
    {
        return RationalTime{ std::ceil(_value), _rate };
    }

    // Return a RationalTime with the nearest integer value to this value.
    RationalTime round() const
    {
        return RationalTime{ std::round(_value), _rate };
    }

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

    static bool is_valid_timecode_rate(double rate);

    static double nearest_valid_timecode_rate(double rate);

    static constexpr RationalTime
    from_frames(double frame, double rate) noexcept
    {
        return RationalTime{ double(int(frame)), rate };
    }

    static constexpr RationalTime
    from_seconds(double seconds, double rate) noexcept
    {
        return RationalTime{ seconds, 1 }.rescaled_to(rate);
    }

    static constexpr RationalTime from_seconds(double seconds) noexcept
    {
        return RationalTime{ seconds, 1 };
    }

    static RationalTime from_timecode(
        std::string const& timecode,
        double             rate,
        ErrorStatus*       error_status = nullptr);

    // parse a string in the form
    // hours:minutes:seconds
    // which may have a leading negative sign. seconds may have up to
    // microsecond precision.
    static RationalTime from_time_string(
        std::string const& time_string,
        double             rate,
        ErrorStatus*       error_status = nullptr);

    constexpr int to_frames() const noexcept { return int(_value); }

    constexpr int to_frames(double rate) const noexcept
    {
        return int(value_rescaled_to(rate));
    }

    constexpr double to_seconds() const noexcept
    {
        return value_rescaled_to(1);
    }

    std::string to_timecode(
        double          rate,
        IsDropFrameRate drop_frame,
        ErrorStatus*    error_status = nullptr) const;

    std::string to_timecode(ErrorStatus* error_status = nullptr) const
    {
        return to_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
    }

    // produce a string in the form
    // hours:minutes:seconds
    // which may have a leading negative sign. seconds may have up to
    // microsecond precision.
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
