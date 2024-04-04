// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/version.h"
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

class TimeTransform
{
public:
    explicit constexpr TimeTransform(
        RationalTime offset = RationalTime{},
        double       scale  = 1,
        double       rate   = -1) noexcept
        : _offset{ offset }
        , _scale{ scale }
        , _rate{ rate }
    {}

    constexpr RationalTime offset() const noexcept { return _offset; }

    constexpr double scale() const noexcept { return _scale; }

    constexpr double rate() const noexcept { return _rate; }

    constexpr TimeTransform(TimeTransform const&) noexcept  = default;
    constexpr TimeTransform& operator=(TimeTransform const&) noexcept = default;

    constexpr TimeRange applied_to(TimeRange other) const noexcept
    {
        return TimeRange::range_from_start_end_time(
            applied_to(other._start_time),
            applied_to(other.end_time_exclusive()));
    }

    constexpr TimeTransform applied_to(TimeTransform other) const noexcept
    {
        return TimeTransform{ _offset + other._offset,
                              _scale * other._scale,
                              _rate > 0 ? _rate : other._rate };
    }

    constexpr RationalTime applied_to(RationalTime other) const noexcept
    {
        RationalTime result{ RationalTime{ other._value * _scale, other._rate }
                             + _offset };
        double       target_rate = _rate > 0 ? _rate : other._rate;
        return target_rate > 0 ? result.rescaled_to(target_rate) : result;
    }

    friend constexpr bool
    operator==(TimeTransform lhs, TimeTransform rhs) noexcept
    {
        return lhs._offset == rhs._offset && lhs._scale == rhs._scale
               && lhs._rate == rhs._rate;
    }

    friend constexpr bool
    operator!=(TimeTransform lhs, TimeTransform rhs) noexcept
    {
        return !(lhs == rhs);
    }

private:
    RationalTime _offset;
    double       _scale;
    double       _rate;
};

}} // namespace opentime::OPENTIME_VERSION
