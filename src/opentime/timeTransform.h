#pragma once

#include "opentime/version.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include <string>

namespace opentime { namespace OPENTIME_VERSION {
    
class TimeTransform {
public:
    explicit TimeTransform(RationalTime offset = RationalTime{}, double scale = 1, double rate = -1)
    : _offset {offset}, _scale {scale}, _rate {rate} {}

    RationalTime offset() const {
        return _offset;
    }

    double scale() const {
        return _scale;
    }

    double rate() const {
        return _rate;
    }

    TimeTransform(TimeTransform const&) = default;
    TimeTransform& operator= (TimeTransform const&) = default;

    TimeRange applied_to(TimeRange other) const {
        return TimeRange::range_from_start_end_time(applied_to(other._start_time),
                                                    applied_to(other.end_time_exclusive()));
    }

    TimeTransform applied_to(TimeTransform other) const {
        return TimeTransform {_offset + other._offset, _scale * other._scale,
                              _rate > 0 ? _rate : other._rate};
    }

    RationalTime applied_to(RationalTime other) const {
        RationalTime result { RationalTime {other._value * _scale, other._rate} + _offset };
        double target_rate = _rate > 0 ? _rate : other._rate;
        return target_rate > 0 ? result.rescaled_to(target_rate) : result;
    }
    
    friend bool operator==(TimeTransform lhs, TimeTransform rhs) {
        return lhs._offset == rhs._offset && lhs._scale == rhs._scale && lhs._rate == rhs._rate;
    }
    
    friend bool operator!=(TimeTransform lhs, TimeTransform rhs) {
        return !(lhs == rhs);
    }
    
private:
    RationalTime _offset;
    double _scale;
    double _rate;
};
    
} }
