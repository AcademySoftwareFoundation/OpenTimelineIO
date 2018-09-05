#ifndef OPENTIME_h
#define OPENTIME_h

#include <array>
#include <cstdio>
#include <iostream>
#include <cmath>

/** \file opentime.h
 * Test implementation of opentime in C++
 */

// just to define hashing functions
namespace opentime 
{
    class RationalTime;
    class TimeRange;
    class TimeTransform;
}

/// @TODO: Do we need hashing functions for these objects?
namespace std 
{
    template<>
    class hash<opentime::RationalTime> 
    {
        public:
            size_t operator()(const opentime::RationalTime&) const; 
    };

    template<>
    class hash<opentime::TimeRange> 
    {
        public:
            size_t operator()(const opentime::TimeRange&) const;
    };

    template<>
    class hash<opentime::TimeTransform> 
    {
        public:
            size_t operator()(const opentime::TimeTransform&) const;
    };
}

namespace opentime 
{

/// type wrappers for rational time
using rt_value_t=double;
using rt_rate_t=double;

/// ensure that the rate is in one of the valid timecode rate lists
bool validate_timecode_rate(const rt_rate_t rate);

/// A point in time, value*rate samples after 0.
class RationalTime
{
public:
    RationalTime(rt_value_t in_value, rt_rate_t in_rate):
        value(in_value),
        rate(in_rate)
    {}
    RationalTime(rt_value_t in_value):
        value(in_value),
        rate(1)
    {}
    RationalTime():
        value(0),
        rate(1)
    {}

    // data
    rt_value_t value;
    rt_rate_t rate;
    
    // methods
    RationalTime rescaled_to(const RationalTime& rt) const;
    RationalTime rescaled_to(rt_rate_t new_rate) const;

    rt_value_t value_rescaled_to(const RationalTime& rt) const;
    rt_value_t value_rescaled_to(rt_rate_t new_rate) const;

    inline rt_value_t
    _abs_coord() const
    {
        return this->value / this->rate;
    }

    // stringification
    inline std::string to_string() const;
    inline std::string repr() const;
    

    inline bool
    almost_equal(const RationalTime& other, rt_value_t delta) const
    {
        auto rescaled_value = this->value_rescaled_to(other.rate);

        return std::fabs(rescaled_value - other.value) <= delta;
    }


    // operators
    friend inline RationalTime
    operator+(const RationalTime& lhs, const RationalTime& rhs)
    {
        if (lhs.rate == rhs.rate)
        {
            return RationalTime(lhs.value + rhs.value, lhs.rate);
        }
        else
        if (lhs.rate > rhs.rate)
        {
            return RationalTime(
                (lhs.value + rhs.value_rescaled_to(lhs.rate)),
                lhs.rate
            );
        }
        else
        {
            return RationalTime(
                lhs.value_rescaled_to(rhs.rate) + rhs.value,
                rhs.rate
            );
        }
    }

    friend RationalTime&
    operator+=(RationalTime& lhs, const RationalTime& rhs)
    {
        auto tvalue = lhs.value;
        auto scale = lhs.rate;

        if (lhs.rate > rhs.rate)
        {
            scale = lhs.rate;
            tvalue = lhs.value + rhs.value_rescaled_to(scale);
        }
        else
        {
            scale = rhs.rate;
            tvalue = lhs.value_rescaled_to(scale) + rhs.value;
        }

        lhs.value = tvalue;
        lhs.rate = scale;

        return lhs;
    }

    friend inline RationalTime
    operator-(const RationalTime& lhs, const RationalTime& rhs)
    {
        return lhs + RationalTime(-rhs.value, rhs.rate);
    }
    friend inline bool 
    operator<(const RationalTime& lhs, const RationalTime& rhs) 
    { 
        return lhs._abs_coord() < rhs._abs_coord(); 
    }
    friend inline bool 
    operator>(const RationalTime& lhs, const RationalTime& rhs) {
        return rhs < lhs;
    }
    friend inline bool 
    operator<=(const RationalTime& lhs, const RationalTime& rhs) 
    {
        return !(lhs > rhs);

    }
    friend inline bool 
    operator>=(const RationalTime& lhs, const RationalTime& rhs) 
    {
        return !(lhs < rhs);
    }
    friend inline bool 
    operator==(const RationalTime& lhs, const RationalTime& rhs) 
    {
        return lhs.value_rescaled_to(rhs.rate) == rhs.value;
    }
    friend inline bool 
    operator!=(const RationalTime& lhs, const RationalTime& rhs) 
    {
        return !(lhs == rhs);
    }


    inline size_t 
    hash() {
        return std::hash<RationalTime>()(*this);
    }

    inline RationalTime
    copy()
    {
        return RationalTime(this->value, this->rate);
    }

    // friend std::hash<RationalTime>::operator()(const RationalTime&) const;
    friend std::hash<RationalTime>;
};

RationalTime from_frames(rt_value_t frame, rt_rate_t fps);
int to_frames(const RationalTime& time_obj, rt_rate_t fps);
int to_frames(const RationalTime& time_obj);

RationalTime from_seconds(rt_value_t seconds);
rt_value_t to_seconds(const RationalTime& rt);

RationalTime from_timecode(const std::string& timecode_str, rt_rate_t rate=24);
std::string to_timecode(const RationalTime& time_obj, rt_rate_t rate);
std::string to_timecode(const RationalTime& time_obj);

RationalTime
duration_from_start_end_time(
        const RationalTime& start_time,
        const RationalTime& end_time_exclusive);

// TimeRange
class TimeRange
{
public:
    RationalTime start_time;
    RationalTime duration;

    TimeRange(
            const RationalTime& start_time_,
            const RationalTime& duration_
    ):
        start_time(start_time_),
        duration(duration_)
    {
    }

    TimeRange(const RationalTime& start_time_):
        start_time(start_time_),
        duration(RationalTime())
    {
    }
        
    TimeRange():
        start_time(RationalTime()),
        duration(RationalTime())
    {
    }

    RationalTime end_time_inclusive() const;
    RationalTime end_time_exclusive() const;

    bool
    contains(const RationalTime& other) const;

    bool
    contains(const TimeRange& other) const;

    bool 
    overlaps(const RationalTime& other) const;

    bool 
    overlaps(const TimeRange& other) const;

    ///Construct a new TimeRange that is this one extended by another.
    TimeRange
    extended_by(const TimeRange& other);


    // stringification
    inline std::string
    to_string() const;

    inline std::string
    repr() const;

    friend inline bool 
    operator==(const TimeRange& lhs, const TimeRange& rhs) 
    {
        return (
                lhs.start_time == rhs.start_time
                && lhs.duration == rhs.duration
       );
    }
    friend inline bool 
    operator!=(const TimeRange& lhs, const TimeRange& rhs) 
    {
        return !(lhs == rhs);
    }

    inline size_t 
    hash() {
        return std::hash<TimeRange>()(*this);
    }

    // friend std::hash<TimeRange>::operator ()(const TimeRange&) const;
    friend std::hash<TimeRange>;

}; // class TimeRange

TimeRange
range_from_start_end_time( const RationalTime& start_time, const RationalTime& end_time_exclusive);

/** Convert this timecode to time with microseconds, as formatted in FFMPEG.
 */
std::string
to_time_string(const RationalTime& time_obj);

class TimeTransform
{
public:
    RationalTime offset;
    rt_rate_t scale;
    rt_rate_t rate;

    TimeTransform(
            const RationalTime& offset_, rt_rate_t scale_, rt_rate_t rate_) : 
        offset(offset_),
        scale(scale_),
        rate(rate_)
    {} 

    TimeTransform(const RationalTime& offset_, rt_rate_t scale_=1.0) : 
        offset(offset_),
        scale(scale_),
        rate(offset_.rate)
    {} 

    TimeTransform() : 
        offset(RationalTime()),
        scale(1.0),
        rate(24.0)
    {} 

    RationalTime
    applied_to(const RationalTime& other) const;

    TimeRange
    applied_to(const TimeRange& other) const;

    TimeTransform
    applied_to(const TimeTransform& other) const;


    friend inline bool 
    operator==(const TimeTransform& lhs, const TimeTransform& rhs) 
    {
        return (
                lhs.offset == rhs.offset
                && lhs.scale == rhs.scale
                && lhs.rate == rhs.rate
               );
    }

    friend inline bool 
    operator!=(const TimeTransform& lhs, const TimeTransform& rhs) 
    {
        return !(lhs == rhs);
    }


    inline size_t 
    hash() {
        return std::hash<TimeTransform>()(*this);
    }
};


/** Convert a time with microseconds string into a RationalTime.

:param time_str: (:class:`str`) A HH:MM:ss.ms time.
:param rate: (:class:`float`) The frame-rate to calculate timecode in
    terms of.

:return: (:class:`RationalTime`) Instance for the timecode provided.
*/
RationalTime from_time_string(const std::string& time_str, rt_rate_t rate);

}; // namespace opentime


#endif // OPENTIME_h
