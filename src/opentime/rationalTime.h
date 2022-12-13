// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/errorStatus.h"
#include "opentime/version.h"
#include <cmath>
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
fabs(double val) noexcept;

class RationalTime
{
public:
    explicit constexpr RationalTime(double value = 0, double rate = 1) noexcept;

    constexpr RationalTime(RationalTime const&) noexcept  = default;
    RationalTime& operator=(RationalTime const&) noexcept = default;

    bool is_invalid_time() const noexcept;

    constexpr double value() const noexcept;

    constexpr double rate() const noexcept;

    constexpr RationalTime rescaled_to(double new_rate) const noexcept;

    constexpr RationalTime rescaled_to(RationalTime rt) const noexcept;

    constexpr double value_rescaled_to(double new_rate) const noexcept;

    constexpr double value_rescaled_to(RationalTime rt) const noexcept;

    constexpr bool
    almost_equal(RationalTime other, double delta = 0) const noexcept;

    static RationalTime constexpr duration_from_start_end_time(
        RationalTime start_time,
        RationalTime end_time_exclusive) noexcept;

    static RationalTime constexpr duration_from_start_end_time_inclusive(
        RationalTime start_time,
        RationalTime end_time_inclusive) noexcept;

    static bool is_valid_timecode_rate(double rate);

    static double nearest_valid_timecode_rate(double rate);

    static constexpr RationalTime
    from_frames(double frame, double rate) noexcept;

    static constexpr RationalTime
    from_seconds(double seconds, double rate) noexcept;

    static constexpr RationalTime from_seconds(double seconds) noexcept;

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

    constexpr int to_frames() const noexcept;

    constexpr int to_frames(double rate) const noexcept;

    constexpr double to_seconds() const noexcept;

    std::string to_timecode(
        double          rate,
        IsDropFrameRate drop_frame,
        ErrorStatus*    error_status = nullptr) const;

    std::string to_timecode(ErrorStatus* error_status = nullptr) const;

    // produce a string in the form
    // hours:minutes:seconds
    // which may have a leading negative sign. seconds may have up to
    // microsecond precision.
    std::string to_time_string() const;

    RationalTime const& operator+=(RationalTime other) noexcept;

    RationalTime const& operator-=(RationalTime other) noexcept;

    friend constexpr RationalTime
    operator+(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr RationalTime
    operator-(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr RationalTime operator-(RationalTime lhs) noexcept;

    friend constexpr bool operator>(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr bool
    operator>=(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr bool operator<(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr bool
    operator<=(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr bool
    operator==(RationalTime lhs, RationalTime rhs) noexcept;

    friend constexpr bool
    operator!=(RationalTime lhs, RationalTime rhs) noexcept;

private:
    static RationalTime     _invalid_time;
    static constexpr double _invalid_rate = -1;

    RationalTime _floor() const noexcept;

    friend class TimeTransform;
    friend class TimeRange;

    double _value, _rate;
};

// Inline functions

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

constexpr RationalTime::RationalTime(double value, double rate) noexcept
    : _value{ value }
    , _rate{ rate }
{}

inline bool RationalTime::is_invalid_time() const noexcept
{
    return (std::isnan(_rate) || std::isnan(_value)) ? true : (_rate <= 0);
}

constexpr double RationalTime::value() const noexcept { return _value; }

constexpr double RationalTime::rate() const noexcept { return _rate; }

constexpr RationalTime RationalTime::rescaled_to(double new_rate) const noexcept
{
    return RationalTime{ value_rescaled_to(new_rate), new_rate };
}

constexpr RationalTime RationalTime::rescaled_to(RationalTime rt) const noexcept
{
    return RationalTime{ value_rescaled_to(rt._rate), rt._rate };
}

constexpr double RationalTime::value_rescaled_to(double new_rate) const noexcept
{
    return new_rate == _rate ? _value : (_value * new_rate) / _rate;
}

constexpr double RationalTime::value_rescaled_to(RationalTime rt) const noexcept
{
    return value_rescaled_to(rt._rate);
}

constexpr bool
RationalTime::almost_equal(RationalTime other, double delta) const noexcept
{
    return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
}

constexpr RationalTime RationalTime::duration_from_start_end_time(
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

constexpr RationalTime RationalTime::duration_from_start_end_time_inclusive(
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

constexpr RationalTime
RationalTime::from_frames(double frame, double rate) noexcept
{
    return RationalTime{ double(int(frame)), rate };
}

constexpr RationalTime
RationalTime::from_seconds(double seconds, double rate) noexcept
{
    return RationalTime{ seconds, 1 }.rescaled_to(rate);
}

constexpr RationalTime RationalTime::from_seconds(double seconds) noexcept
{
    return RationalTime{ seconds, 1 };
}

constexpr int RationalTime::to_frames() const noexcept { return int(_value); }

constexpr int RationalTime::to_frames(double rate) const noexcept
{
    return int(value_rescaled_to(rate));
}

constexpr double RationalTime::to_seconds() const noexcept
{
    return value_rescaled_to(1);
}

inline std::string RationalTime::to_timecode(ErrorStatus* error_status) const
{
    return to_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
}

inline RationalTime const& RationalTime::operator+=(RationalTime other) noexcept
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

inline RationalTime const& RationalTime::operator-=(RationalTime other) noexcept
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

constexpr RationalTime
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

constexpr RationalTime
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

constexpr RationalTime operator-(RationalTime lhs) noexcept
{
    return RationalTime{ -lhs._value, lhs._rate };
}

constexpr bool operator>(RationalTime lhs, RationalTime rhs) noexcept
{
    return (lhs._value / lhs._rate) > (rhs._value / rhs._rate);
}

constexpr bool
operator>=(RationalTime lhs, RationalTime rhs) noexcept
{
    return (lhs._value / lhs._rate) >= (rhs._value / rhs._rate);
}

constexpr bool operator<(RationalTime lhs, RationalTime rhs) noexcept
{
    return !(lhs >= rhs);
}

constexpr bool
operator<=(RationalTime lhs, RationalTime rhs) noexcept
{
    return !(lhs > rhs);
}

constexpr bool
operator==(RationalTime lhs, RationalTime rhs) noexcept
{
    return lhs.value_rescaled_to(rhs._rate) == rhs._value;
}

constexpr bool
operator!=(RationalTime lhs, RationalTime rhs) noexcept
{
    return !(lhs == rhs);
}

inline RationalTime RationalTime::_floor() const noexcept
{
    return RationalTime{ floor(_value), _rate };
}

}} // namespace opentime::OPENTIME_VERSION
