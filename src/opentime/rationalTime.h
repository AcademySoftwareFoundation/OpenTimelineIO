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
    explicit RationalTime(double value = 0, double rate = 1) : _value {value}, _rate {rate} {}
    RationalTime(RationalTime && rh) { _value = rh._value; _rate = rh._rate; }
    RationalTime(RationalTime const& rh) { _value = rh._value; _rate = rh._rate; }
    RationalTime& operator= (RationalTime const& rh) { _value = rh._value; _rate = rh._rate; return *this; }
    RationalTime& operator= (RationalTime && rh) { _value = rh._value; _rate = rh._rate; return *this; }
    ~RationalTime() = default;

    bool is_invalid_time() const { return _rate <= 0; }
    double value() const { return _value; }
    double rate() const { return _rate; }
    
    void set_value(double v) { _value = v; }
    void set_rate(double r) { _rate = r; }
    
    RationalTime floor() const {
        return RationalTime { std::floor(_value), _rate };
    }

    RationalTime floor(double rate) const {
        return rescaled_to(rate).floor();
    }
    
    RationalTime ceil() const {
        return RationalTime { std::ceil(_value), _rate };
    }

    RationalTime ceil(double rate) const {
        return rescaled_to(rate).ceil();
    }

    RationalTime round_nearest() const {
        return RationalTime(_value + 0.5 / _rate, _rate).floor();
    }
    
    RationalTime round_nearest(double rate) const {
        return rescaled_to(rate).round_nearest();
    }
    
    RationalTime incr() const {
        RationalTime result = floor();
        return RationalTime(result._value + 1, result._rate);
    }

    RationalTime decr() const {
        RationalTime result = floor();
        return RationalTime(result._value - 1, result._rate);
    }

    RationalTime incr(double rate) const {
        return rescaled_to(rate).incr();
    }

    RationalTime decr(double rate) const {
        return rescaled_to(rate).decr();
    }

    RationalTime rescaled_to(double new_rate) const {
        return RationalTime {value_rescaled_to(new_rate), new_rate};
    }

    RationalTime rescaled_to(const RationalTime& rt) const {
        return RationalTime {value_rescaled_to(rt._rate), rt._rate};
    }

    double value_rescaled_to(double new_rate) const {
        return new_rate == _rate ? _value : (_value * new_rate) / _rate;
    }
    
    double value_rescaled_to(const RationalTime& rt) const {
        return value_rescaled_to(rt._rate);
    }

    bool almost_equal(const RationalTime& other, double delta = 0) const {
        return fabs(value_rescaled_to(other._rate) - other._value) <= delta;
    }

    static RationalTime
    duration_from_start_end_time(const RationalTime& start_time, const RationalTime& end_time_exclusive) {
        return start_time._rate == end_time_exclusive._rate ?
            RationalTime {end_time_exclusive._value - start_time._value, start_time._rate} :
            RationalTime {end_time_exclusive.value_rescaled_to(start_time) - start_time._value,
                          start_time._rate};
    }

    static bool is_valid_timecode_rate(double rate);
    
    static RationalTime from_frames(double frame, double rate) {
        return RationalTime{static_cast<double>(static_cast<int>(frame)), rate};
    }

    static RationalTime from_seconds(double seconds) {
        return RationalTime{seconds, 1};
    }

    static RationalTime from_quicktime_timecode(std::string const& timecode, ErrorStatus *error_status);
    static RationalTime from_smpte_timecode(std::string const& timecode, double rate, ErrorStatus *error_status);

    static RationalTime from_timecode(std::string const& timecode, double rate, ErrorStatus *error_status);
    static RationalTime from_time_string(std::string const& time_string, double rate, ErrorStatus *error_status);

    int to_frames() const {
        return int(_value);
    }
    
    int to_frames(double rate) const {
        return static_cast<int>(value_rescaled_to(rate));
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
    
    std::string to_quicktime_timecode(ErrorStatus *error_status) const;

    std::string to_time_string() const;

    RationalTime const& operator+= (const RationalTime& other) {
        if (_rate < other._rate) {
            _value = other._value + value_rescaled_to(other._rate);
            _rate = other._rate;
        }
        else {
            _value += other.value_rescaled_to(_rate);
        }
        return *this;
    }

    RationalTime const& operator-= (const RationalTime& other) {
        if (_rate < other._rate) {
            _value = value_rescaled_to(other._rate) - other._value;
            _rate = other._rate;
        }
        else {
            _value -= other.value_rescaled_to(_rate);
        }
        return *this;
    }

    friend RationalTime operator+ (const RationalTime& lhs, const RationalTime& rhs) {
        return (lhs._rate < rhs._rate) ? RationalTime {lhs.value_rescaled_to(rhs._rate) + rhs._value, rhs._rate} :
                                         RationalTime {rhs.value_rescaled_to(lhs._rate) + lhs._value, lhs._rate};
    }
        
    friend RationalTime operator- (const RationalTime& lhs, const RationalTime& rhs) {
        return (lhs._rate < rhs._rate) ? RationalTime {lhs.value_rescaled_to(rhs._rate) - rhs._value, rhs._rate} :
                                         RationalTime {lhs._value - rhs.value_rescaled_to(lhs._rate), lhs._rate};
    }

    friend RationalTime operator- (const RationalTime& lhs) {
        return RationalTime {-lhs._value, lhs._rate};
    }

    friend bool operator> (const RationalTime& lhs, const RationalTime& rhs) {
         return (lhs._value / lhs._rate) > (rhs._value / rhs._rate);
    }

    friend bool operator>= (const RationalTime& lhs, const RationalTime& rhs) {
        return (lhs._value / lhs._rate) >= (rhs._value / rhs._rate);
    }

    friend bool operator< (const RationalTime& lhs, const RationalTime& rhs) {
        return !(lhs >= rhs);
    }

    friend bool operator<= (const RationalTime& lhs, const RationalTime& rhs) {
        return !(lhs > rhs);
    }

    friend bool operator== (const RationalTime& lhs, const RationalTime& rhs) {
        return lhs.value_rescaled_to(rhs._rate) == rhs._value;
    }

    friend bool operator!= (const RationalTime& lhs, const RationalTime& rhs) {
        return !(lhs == rhs);
    }

    friend RationalTime operator * (const RationalTime& lhs, float rhs) {
        return RationalTime(lhs._value * rhs, lhs._rate);
    }
    friend RationalTime operator * (const RationalTime& lhs, double rhs) {
        return RationalTime(lhs._value * rhs, lhs._rate);
    }

    friend RationalTime operator * (float lhs, const RationalTime& rhs) {
        return RationalTime(rhs._value * lhs, rhs._rate);
    }
    friend RationalTime operator * (double lhs, const RationalTime& rhs) {
        return RationalTime(rhs._value * lhs, rhs._rate);
    }

private:
    static RationalTime _from_timecode(std::string const& timecode, double rate,
                                       bool is_drop_frame,
                                       ErrorStatus *error_status);

    friend class TimeTransform;
    friend class TimeRange;

    static RationalTime _invalid_time;
    static double _invalid_rate;

    double _value, _rate;
};

} }


