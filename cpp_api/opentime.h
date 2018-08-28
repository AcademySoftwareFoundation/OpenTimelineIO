#ifndef OPENTIME_h
#define OPENTIME_h

#include <cstdio>
#include <iostream>

/**
 * Test implementation of opentime in C++
 */

// just to define hashing functions
namespace opentime 
{
    class RationalTime;
    class TimeRange;
}

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
}

namespace opentime 
{

/// type wrappers for rational time
using rt_value_t=double;
using rt_rate_t=double;



/// A point in time, value*rate samples after 0.
class RationalTime
{
public:
    RationalTime(rt_value_t in_value, rt_rate_t in_rate):
        value(in_value),
        rate(in_rate)
    {};
    RationalTime(rt_value_t in_value):
        value(in_value),
        rate(1)
    {};
    RationalTime():
        value(0),
        rate(1)
    {};

    // data
    rt_value_t value;
    rt_rate_t rate;
    
    // methods
    RationalTime 
    rescaled_to(const RationalTime& rt) const
    {
        return this->rescaled_to(rt.rate);
    }

    RationalTime 
    rescaled_to(rt_rate_t new_rate) const
    {
        return RationalTime(
                this->value_rescaled_to(new_rate),
                new_rate
        );
    }

    rt_value_t 
    value_rescaled_to(const RationalTime& rt) const
    {
        return this->value_rescaled_to(rt.rate);
    }

    rt_value_t 
    value_rescaled_to(rt_value_t new_rate) const
    {
        if (new_rate == this->rate)
        {
            return this->value;
        }

        return (this->value * new_rate) / this->rate;
    }


    inline rt_value_t
    _abs_coord() const
    {
        return this->value / this->rate;
    }

    // stringification
    inline std::string
    to_string() const
    {
        return (
                "RationalTime(" 
                + std::to_string(this->value) 
                + ", " 
                + std::to_string(this->rate) 
                + ")"
       );
    }

    inline std::string
    repr() const
    {
        return (
                "otio.opentime.RationalTime(value=" 
                + std::to_string(this->value) 
                + ", " 
                + "rate=" + std::to_string(this->rate) 
                + ")"
       );
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

    // friend std::hash<RationalTime>::operator()(const RationalTime&) const;
    friend std::hash<RationalTime>;
};

RationalTime
from_frames(rt_value_t frame, rt_rate_t fps)
{
    return RationalTime(frame*600 / fps, 600);
}
RationalTime
from_seconds(rt_value_t seconds)
{
    return RationalTime(seconds, 1);
}
rt_value_t
to_seconds(const RationalTime& rt)
{
    return rt.value_rescaled_to(1);
}

RationalTime
from_timecode(const std::string& timecode_str, rt_rate_t rate=24)
{
    std::vector<std::string> fields {"","","",""};

    // split the fields
    int last_pos = 0;
    for (int i=0; i<4; i++)
    {
        fields[i] = timecode_str.substr(last_pos, 2);
        // std::cerr<<fields[i]<< " " << last_pos << " " << std::stoi(fields[i]) << std::endl;
        last_pos = last_pos+3;
    }

    int hours   = std::stoi(fields[0]);
    int minutes = std::stoi(fields[1]);
    int seconds = std::stoi(fields[2]);
    int frames  = std::stoi(fields[3]);

    const int nominal_fps = std::ceil(rate);
    const int value = (
        (
            // convert to frames
            ((hours * 60 + minutes) * 60) + seconds
        ) * nominal_fps + frames
    );

    return RationalTime(value, nominal_fps);
}

std::string
to_timecode(const RationalTime& time_obj, rt_rate_t rate)
{
    // @TODO: Is this the right policy for C++
    if (time_obj.value < 0)
    {
        throw std::invalid_argument("time_obj has a negative value");
    }

    const int nominal_fps = std::ceil(rate);
    const rt_rate_t time_units_per_second = time_obj.rate;
    const rt_rate_t time_units_per_frame = time_units_per_second / nominal_fps;
    const rt_rate_t time_units_per_minute = time_units_per_second * 60.0f;
    const rt_rate_t time_units_per_hour = time_units_per_minute * 60.0f;
    const rt_rate_t time_units_per_day = time_units_per_hour * 24.0f;

    // days
    const int days = std::floor(time_obj.value / time_units_per_day);
    const int hour_units = std::remainder(time_obj.value, time_units_per_day);

    // hours
    const int hours = std::floor(hour_units / time_units_per_hour);
    const int minute_units = std::remainder(hour_units, time_units_per_hour);

    // minutes
    const int minutes = std::floor(minute_units / time_units_per_minute);
    const int second_units = std::remainder(minute_units, time_units_per_minute);
    
    // seconds
    const int seconds = std::floor(second_units / time_units_per_second);
    const int frame_units = std::remainder(second_units, time_units_per_second);

    // frames
    const int frames = std::floor(frame_units / time_units_per_frame);

    // std::cerr << frame << std::endl;


//     snprintf(
//             base,
// ,
//             hours,
//             minutes,
//             seconds,
//             frames
//     );
//
    const char *fmt = "%02d:%02d:%02d:%02d";
    int sz = std::snprintf(nullptr, 0, fmt, hours,minutes,seconds,frames);
    std::vector<char> buf(sz + 1); // note +1 for null terminator
    std::snprintf(&buf[0], buf.size(), fmt, hours,minutes,seconds,frames);

    return &buf[0];

}

RationalTime
duration_from_start_end_time(
        const RationalTime& start_time,
        const RationalTime& end_time_exclusive
)
{
    if (start_time.rate == end_time_exclusive.rate)
    {
        return RationalTime(
            end_time_exclusive.value - start_time.value,
            start_time.rate
        );
    }
    else
    {
        return RationalTime(
                (
                 end_time_exclusive.value_rescaled_to(start_time) 
                 - start_time.value
                ),
                start_time.rate
        );
    }
}

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

    RationalTime
    end_time_inclusive() const
    {
        // std::cerr << "end time inclusive" << std::endl;
        if ((this->end_time_exclusive() - this->start_time.rescaled_to(this->duration)).value > 1)
        {
            // std::cerr << "> 1 branch" << std::endl;
            RationalTime result =  (
                this->end_time_exclusive() - RationalTime(1, this->duration.rate)
            );

            if (this->duration.value != std::floor(this->duration.value))
            {
                // std::cerr << "duration branch" << std::endl;
                result = this->end_time_exclusive();
                result.value = std::floor(result.value);
            }

            return result;
        }
        else
        {
            // std::cerr << "start time" << this->start_time.to_string() << std::endl;
            // std::cerr << "duration" << this->duration.to_string() << std::endl;
            // std::cerr << "exclusive" << this->end_time_exclusive().to_string() << std::endl;
            // std::cerr << "exclusive - duration: " <<  (this->end_time_exclusive() - this->start_time.rescaled_to(this->duration)).value << std::endl;
            return this->start_time;
        }
    }

    RationalTime
    end_time_exclusive() const
    {
        return this->duration + this->start_time.rescaled_to(this->duration);
    }

    bool
    contains(const RationalTime& other) const
    {
        return (
                this->start_time <= other
                and other < this->end_time_exclusive()
       );
    }

    bool
    contains(const TimeRange& other) const
    {
        return (
                this->start_time <= other.start_time and
                this->end_time_exclusive() >= other.end_time_exclusive()
       );
    }

    bool 
    overlaps(const RationalTime& other) const
    {
        return this->contains(other);
    }

    bool 
    overlaps(const TimeRange& other) const
    {
        return ( 
                this->start_time < other.end_time_exclusive()
                and other.start_time < this->end_time_exclusive()
       );
    }


    // stringification
    inline std::string
    to_string() const
    {
        return (
                "TimeRange(" 
                + this->start_time.to_string()
                + ", " 
                + this->duration.to_string()
                + ")"
       );
    }

    inline std::string
    repr() const
    {
        return (
                "otio.opentime.TimeRange(start_time=" 
                + this->start_time.repr()
                + ", " 
                + "duration=" + this->duration.repr()
                + ")"
       );
    }

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
range_from_start_end_time(
        const RationalTime& start_time,
        const RationalTime& end_time_exclusive
)
{
    return TimeRange(
            start_time,
            duration_from_start_end_time(start_time, end_time_exclusive)
    );
}

}; // namespace opentime

// hash function implementation
namespace std 
{
    size_t 
    hash<opentime::RationalTime>::operator()(
            const opentime::RationalTime& rt
    ) const 
    {
            return (
                    (std::hash<opentime::rt_value_t>{}(rt.value)) 
                    ^ ((std::hash<opentime::rt_rate_t>{}(rt.rate)) >> 1)
            );
    }

    size_t 
    hash<opentime::TimeRange>::operator()(
            const opentime::TimeRange &tr
    ) const 
    {
        return (
                (std::hash<opentime::RationalTime>{}(tr.start_time)) 
                ^ ((std::hash<opentime::RationalTime>{}(tr.duration)) >> 1)
        );
    }
};

#endif // OPENTIME_h
