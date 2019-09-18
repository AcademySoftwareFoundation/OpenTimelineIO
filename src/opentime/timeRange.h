#pragma once

#include "opentime/version.h"
#include "opentime/rationalTime.h"
#include <algorithm>
#include <string>

namespace opentime { namespace OPENTIME_VERSION {
    
class TimeRange {
public:
    explicit TimeRange() : _start_time {}, _duration {} {}

    explicit TimeRange(RationalTime start_time)
    : _start_time {start_time}, _duration { RationalTime {0, start_time.rate()} } {}

    explicit TimeRange(RationalTime start_time, RationalTime duration)
    : _start_time {start_time}, _duration {duration} {}

    TimeRange(TimeRange const&) = default;
    TimeRange& operator= (TimeRange const&) = default;

    RationalTime const& start_time() const {
        return _start_time;
    }

    RationalTime const& duration() const {
        return _duration;
    }

    RationalTime end_time_inclusive() const {
        RationalTime et = end_time_exclusive();
            
        if ((et - _start_time.rescaled_to(_duration))._value > 1) {
            return _duration._value != floor(_duration._value) ? et._floor() :
                                                                 et - RationalTime(1, _duration._rate);
        }
        else {
            return _start_time;
        }
    }

    RationalTime end_time_exclusive() const {
        return _duration + _start_time.rescaled_to(_duration);
    }

    TimeRange duration_extended_by(RationalTime other) const {
        return TimeRange {_start_time, _duration + other};
    }

    TimeRange extended_by(TimeRange other) const {
        RationalTime new_start_time {std::min(_start_time, other._start_time)},
                     new_end_time {std::max(end_time_exclusive(), other.end_time_exclusive())};

        return TimeRange {new_start_time,
                          RationalTime::duration_from_start_end_time(new_start_time, new_end_time)};
    }

    RationalTime clamped(RationalTime other) const {
        return std::min(std::max(other, _start_time), end_time_inclusive());
    }

    TimeRange clamped(TimeRange other) const {
        TimeRange r {std::max(other._start_time, _start_time), other._duration};
        RationalTime end {std::min(r.end_time_exclusive(), end_time_exclusive())};
        return TimeRange {r._start_time, end - r._start_time};
    }

    bool contains(RationalTime other) const {
        return _start_time <= other && other < end_time_exclusive();
    }

    bool contains(TimeRange other) const {
        return _start_time <= other._start_time && end_time_exclusive() >= other.end_time_exclusive();
    }

    bool overlaps(RationalTime other) const {
        return contains(other);
    }

    bool overlaps(TimeRange other) const {
        return _start_time < other.end_time_exclusive() && other._start_time < end_time_exclusive();
    }

    friend bool operator== (TimeRange lhs, TimeRange rhs) {
        return lhs._start_time == rhs._start_time && lhs._duration == rhs._duration;
    }
    
    friend bool operator!= (TimeRange lhs, TimeRange rhs) {
        return !(lhs == rhs);
    }

    static TimeRange range_from_start_end_time(RationalTime start_time, RationalTime end_time_exclusive) {
        return TimeRange {start_time, RationalTime::duration_from_start_end_time(start_time, end_time_exclusive)};
    }

private:
    RationalTime _start_time, _duration;
    friend class TimeTransform;
};

} }

