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
    explicit RationalTime(double value = 0, double rate = 1)
    : _value {value}, _rate {rate} {}

    RationalTime(RationalTime const&) = default;
    RationalTime& operator= (RationalTime const&) = default;

    bool is_invalid_time() const {
        return _rate <= 0;
    }
    
    double value() const {
        return _value;
    }

    double rate() const {
        return _rate;
    }

    RationalTime rescaled_to(double new_rate) const {
        return RationalTime {value_rescaled_to(new_rate), new_rate};
    }

    RationalTime rescaled_to(RationalTime rt) const {
        return RationalTime {value_rescaled_to(rt._rate), rt._rate};
    }

    double value_rescaled_to(double new_rate) const {
        return new_rate == _rate ? _value : (_value * new_rate) / _rate;
    }
    
    double value_rescaled_to(RationalTime rt) const {
        return value_rescaled_to(rt._rate);
    }

    bool almost_equal(RationalTime other, double delta = 0) const {
        return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
    }

    static RationalTime
    duration_from_start_end_time(RationalTime start_time, RationalTime end_time_exclusive) {
        return start_time._rate == end_time_exclusive._rate ?
            RationalTime {end_time_exclusive._value - start_time._value, start_time._rate} :
            RationalTime {end_time_exclusive.value_rescaled_to(start_time) - start_time._value,
                          start_time._rate};
    }

    static bool is_valid_timecode_rate(double rate);
    
    static RationalTime from_frames(double frame, double rate) {
        return RationalTime{double(int(frame)), rate};
    }

    static RationalTime from_seconds(double seconds) {
        return RationalTime{seconds, 1};
    }

    static RationalTime from_timecode(std::string const& timecode, double rate, ErrorStatus *error_status);
    static RationalTime from_time_string(std::string const& time_string, double rate, ErrorStatus *error_status);

    int to_frames() const {
        return int(_value);
    }

    int to_frames(double rate) const {
        return int(value_rescaled_to(rate));
    }

    double to_seconds() const {
        return value_rescaled_to(1);
    }
    
    std::string to_timecode(
            double rate,
            IsDropFrameRate drop_frame,
            ErrorStatus *error_status
    ) const;

    std::string to_timecode(ErrorStatus *error_status) const {
        return to_timecode(_rate, IsDropFrameRate::InferFromRate, error_status);
    }
    
    std::string to_time_string() const;

    RationalTime const& operator+= (RationalTime other) {
        if (_rate < other._rate) {
            _value = other._value + value_rescaled_to(other._rate);
            _rate = other._rate;
        }
        else {
            _value += other.value_rescaled_to(_rate);
        }
        return *this;
    }

    RationalTime const& operator-= (RationalTime other) {
        if (_rate < other._rate) {
            _value = value_rescaled_to(other._rate) - other._value;
            _rate = other._rate;
        }
        else {
            _value -= other.value_rescaled_to(_rate);
        }
        return *this;
    }

    friend RationalTime operator+ (RationalTime lhs, RationalTime rhs) {
        return (lhs._rate < rhs._rate) ? RationalTime {lhs.value_rescaled_to(rhs._rate) + rhs._value, rhs._rate} :
                                         RationalTime {rhs.value_rescaled_to(lhs._rate) + lhs._value, lhs._rate};
    }
        
    friend RationalTime operator- (RationalTime lhs, RationalTime rhs) {
        return (lhs._rate < rhs._rate) ? RationalTime {lhs.value_rescaled_to(rhs._rate) - rhs._value, rhs._rate} :
                                         RationalTime {lhs._value - rhs.value_rescaled_to(lhs._rate), lhs._rate};
    }

    friend RationalTime operator- (RationalTime lhs) {
        return RationalTime {-lhs._value, lhs._rate};
    }

    friend bool operator> (RationalTime lhs, RationalTime rhs) {
         return (lhs._value / lhs._rate) > (rhs._value / rhs._rate);
    }

    friend bool operator>= (RationalTime lhs, RationalTime rhs) {
        return (lhs._value / lhs._rate) >= (rhs._value / rhs._rate);
    }

    friend bool operator< (RationalTime lhs, RationalTime rhs) {
        return !(lhs >= rhs);
    }

    friend bool operator<= (RationalTime lhs, RationalTime rhs) {
        return !(lhs > rhs);
    }

    friend bool operator== (RationalTime lhs, RationalTime rhs) {
        return lhs.value_rescaled_to(rhs._rate) == rhs._value;
    }

    friend bool operator!= (RationalTime lhs, RationalTime rhs) {
        return !(lhs == rhs);
    }

private:
    static RationalTime _invalid_time;
    static constexpr double _invalid_rate = -1;
    
    RationalTime _floor() const {
        return RationalTime {floor(_value), _rate};
    }

    friend class TimeTransform;
    friend class TimeRange;

    double _value, _rate;
};

} }


