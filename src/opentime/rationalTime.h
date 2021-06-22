#pragma once

#include "opentime/version.h"
#include "opentime/errorStatus.h"
#include <cmath>
#include <string>

namespace opentime { namespace OPENTIME_VERSION  {

enum IsDropFrameRate : int {
    InferFromRate = -1,
    ForceNo = 0,
    ForceYes = 1,
};
    
    
class RationalTime {
public:
    explicit RationalTime(double value = 0, double rate = 1);
    RationalTime(RationalTime const&) = default;
    RationalTime& operator= (RationalTime const&) = default;

    bool is_invalid_time() const;
    
    double value() const;
    double rate() const;

    RationalTime rescaled_to(double new_rate) const;
    RationalTime rescaled_to(RationalTime rt) const;

    double value_rescaled_to(double new_rate) const;
    double value_rescaled_to(RationalTime rt) const;

    bool almost_equal(RationalTime other, double delta = 0) const;

    static RationalTime
    duration_from_start_end_time(RationalTime start_time, RationalTime end_time_exclusive);

    static RationalTime
    duration_from_start_end_time_inclusive(RationalTime start_time, RationalTime end_time_inclusive);

    static bool is_valid_timecode_rate(double rate);
    
    static RationalTime from_frames(double frame, double rate);

    static RationalTime from_seconds(double seconds);

    static RationalTime from_timecode(std::string const& timecode, double rate, ErrorStatus *error_status);
    static RationalTime from_time_string(std::string const& time_string, double rate, ErrorStatus *error_status);

    int to_frames() const;

    int to_frames(double rate) const;

    double to_seconds() const;
    
    std::string to_timecode(
            double rate,
            IsDropFrameRate drop_frame,
            ErrorStatus *error_status
    ) const;

    std::string to_timecode(ErrorStatus *error_status) const;
    
    std::string to_time_string() const;

    RationalTime const& operator+= (RationalTime other);
    RationalTime const& operator-= (RationalTime other);

    friend RationalTime operator+ (RationalTime lhs, RationalTime rhs);
    friend RationalTime operator- (RationalTime lhs, RationalTime rhs);
    friend RationalTime operator- (RationalTime lhs);

    friend bool operator> (RationalTime lhs, RationalTime rhs);
    friend bool operator>= (RationalTime lhs, RationalTime rhs);
    friend bool operator< (RationalTime lhs, RationalTime rhs);
    friend bool operator<= (RationalTime lhs, RationalTime rhs);
    friend bool operator== (RationalTime lhs, RationalTime rhs);

    friend bool operator!= (RationalTime lhs, RationalTime rhs);

private:
    static RationalTime _invalid_time;
    static constexpr double _invalid_rate = -1;
    
    RationalTime _floor() const;

    friend class TimeTransform;
    friend class TimeRange;

    double _value, _rate;
};

inline RationalTime::RationalTime(double value, double rate)
    : _value {value}, _rate {rate} {}

inline bool RationalTime::is_invalid_time() const {
    if(std::isnan(_rate) || std::isnan(_value)) {
        return true;
    }

    return _rate <= 0;
}

inline double RationalTime::value() const {
    return _value;
}

inline double RationalTime::rate() const {
    return _rate;
}

inline RationalTime RationalTime::rescaled_to(double new_rate) const {
    return RationalTime {value_rescaled_to(new_rate), new_rate};
}

inline RationalTime RationalTime::rescaled_to(RationalTime rt) const {
    return RationalTime {value_rescaled_to(rt._rate), rt._rate};
}

inline double RationalTime::value_rescaled_to(double new_rate) const {
    return new_rate == _rate ? _value : (_value * new_rate) / _rate;
}

inline double RationalTime::value_rescaled_to(RationalTime rt) const {
    return value_rescaled_to(rt._rate);
}

inline bool RationalTime::almost_equal(RationalTime other, double delta) const {
    return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
}

inline RationalTime
RationalTime::duration_from_start_end_time(RationalTime start_time, RationalTime end_time_exclusive) {
    return start_time._rate == end_time_exclusive._rate ?
        RationalTime {end_time_exclusive._value - start_time._value, start_time._rate} :
        RationalTime {end_time_exclusive.value_rescaled_to(start_time) - start_time._value,
                      start_time._rate};
}

inline RationalTime
RationalTime::duration_from_start_end_time_inclusive(RationalTime start_time, RationalTime end_time_inclusive) {
    return start_time._rate == end_time_inclusive._rate ?
        RationalTime {end_time_inclusive._value - start_time._value + 1, start_time._rate} :
        RationalTime {end_time_inclusive.value_rescaled_to(start_time) - start_time._value + 1,
                      start_time._rate};
}

inline RationalTime RationalTime::from_frames(double frame, double rate) {
    return RationalTime{double(int(frame)), rate};
}

inline RationalTime RationalTime::from_seconds(double seconds) {
    return RationalTime{seconds, 1};
}

inline int RationalTime::to_frames() const {
    return int(_value);
}

inline int RationalTime::to_frames(double rate) const {
    return int(value_rescaled_to(rate));
}

inline double RationalTime::to_seconds() const {
    return value_rescaled_to(1);
}

inline std::string RationalTime::to_timecode(ErrorStatus *error_status) const {
    return to_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
}

inline RationalTime const& RationalTime::operator+= (RationalTime other) {
    if (_rate < other._rate) {
        _value = other._value + value_rescaled_to(other._rate);
        _rate = other._rate;
    }
    else {
        _value += other.value_rescaled_to(_rate);
    }
    return *this;
}

inline RationalTime const& RationalTime::operator-= (RationalTime other) {
    if (_rate < other._rate) {
        _value = value_rescaled_to(other._rate) - other._value;
        _rate = other._rate;
    }
    else {
        _value -= other.value_rescaled_to(_rate);
    }
    return *this;
}

inline RationalTime operator+ (RationalTime lhs, RationalTime rhs) {
    return (lhs._rate < rhs._rate) ? RationalTime {lhs.value_rescaled_to(rhs._rate) + rhs._value, rhs._rate} :
                                     RationalTime {rhs.value_rescaled_to(lhs._rate) + lhs._value, lhs._rate};
}
    
inline RationalTime operator- (RationalTime lhs, RationalTime rhs) {
    return (lhs._rate < rhs._rate) ? RationalTime {lhs.value_rescaled_to(rhs._rate) - rhs._value, rhs._rate} :
                                     RationalTime {lhs._value - rhs.value_rescaled_to(lhs._rate), lhs._rate};
}

inline RationalTime operator- (RationalTime lhs) {
    return RationalTime {-lhs._value, lhs._rate};
}

inline bool operator> (RationalTime lhs, RationalTime rhs) {
     return (lhs._value / lhs._rate) > (rhs._value / rhs._rate);
}

inline bool operator>= (RationalTime lhs, RationalTime rhs) {
    return (lhs._value / lhs._rate) >= (rhs._value / rhs._rate);
}

inline bool operator< (RationalTime lhs, RationalTime rhs) {
    return !(lhs >= rhs);
}

inline bool operator<= (RationalTime lhs, RationalTime rhs) {
    return !(lhs > rhs);
}

inline bool operator== (RationalTime lhs, RationalTime rhs) {
    return lhs.value_rescaled_to(rhs._rate) == rhs._value;
}

inline bool operator!= (RationalTime lhs, RationalTime rhs) {
    return !(lhs == rhs);
}

inline RationalTime RationalTime::_floor() const {
    return RationalTime {floor(_value), _rate};
}

} }


