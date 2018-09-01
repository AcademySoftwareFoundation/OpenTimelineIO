#ifndef OPENTIME_h
#define OPENTIME_h

#include <cstdio>
#include <iostream>

#define DEBUG_PRINT(var) \
    std::cerr << #var ": " << var << std::endl;

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



std::array<rt_rate_t, 2> VALID_DROPFRAME_TIMECODE_RATES { 
    29.97,
    59.94
};

std::array<rt_rate_t, 10> VALID_NON_DROPFRAME_TIMECODE_RATES {
    1,
    12,
    23.976,
    23.98,
    24,
    25,
    30,
    48,
    50,
    60
};

#define ARRAY_CONTAINS(arr, value) \
    ( std::find(std::begin(arr), std::end(arr), value) != std::end(arr))

bool
validate_timecode_rate(const rt_rate_t rate)
{
    if (
        not ARRAY_CONTAINS(VALID_DROPFRAME_TIMECODE_RATES, rate) 
        && not ARRAY_CONTAINS(VALID_NON_DROPFRAME_TIMECODE_RATES, rate) 
    )
    {
        throw std::invalid_argument("rate is not a valid non-dropframe timecode rate");
    }

    return true;
}


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
    value_rescaled_to(rt_rate_t new_rate) const
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

    inline bool
    almost_equal(const RationalTime& other, rt_value_t delta) const
    {
        auto rescaled_value = this->value_rescaled_to(other.rate);

        return abs(rescaled_value - other.value) <= delta;
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
    friend RationalTime
    operator+=(RationalTime& lhs, const RationalTime& rhs)
    {
        auto value = lhs.value;
        auto scale = lhs.rate;
        if (lhs.rate == rhs.rate)
        {
            lhs.value += rhs.value;
            return lhs;
        }
        else if (lhs.rate > rhs.rate)
        {
            scale = rhs.rate;
            value = lhs.value + rhs.value_rescaled_to(scale);
        }
        else
        {
            scale = rhs.rate;
            value = lhs.value_rescaled_to(scale) + rhs.value;
        }

        lhs.value = value;
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

RationalTime
from_frames(rt_value_t frame, rt_rate_t fps)
{
    return RationalTime(std::floor(frame), fps);
}
RationalTime
from_seconds(rt_value_t seconds)
{
    return RationalTime(seconds, 1);
}
rt_value_t
to_seconds(const RationalTime& rt)
{
    return rt.value_rescaled_to(1.0);
}

RationalTime
from_timecode(const std::string& timecode_str, rt_rate_t rate=24)
{
    validate_timecode_rate(rate);

    bool rate_is_dropframe = ARRAY_CONTAINS(VALID_DROPFRAME_TIMECODE_RATES, rate);

    std::string clean_timecode_str = timecode_str;

    if (ARRAY_CONTAINS(timecode_str, ';'))
    {
        if (not rate_is_dropframe)
        {
            throw std::invalid_argument(
                    "Timecode '" + timecode_str + "' indicates drop frame rate"
                    "due to the ';' frame divider. "
                    "Passed rate (" + std::to_string(rate) 
                    + ") is of non-drop-frame-rate. "
            );
        }
        else
        {
            clean_timecode_str.replace(timecode_str.find(";"), 1, ":");
        }
    }

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

    if (frames >= nominal_fps)
    {
        throw std::invalid_argument(
                "Frame rate mismatch.  Timecode '"
                +timecode_str+"' has frames beyond " 
                + std::to_string(nominal_fps - 1) 
                + "."
        );
    }

    int dropframes = 0;
    if (rate_is_dropframe)
    {
        if (rate == (rt_rate_t)29.97)
        {
            dropframes = 2;
        }
        else if (rate == (rt_rate_t)59.94)
        {
            dropframes = 4;
        }
    }

    // to use for drop frame compensation
    int total_minutes = hours * 60 + minutes;

    // convert to frames
    const int value = (
        ((total_minutes * 60) + seconds) * nominal_fps 
        + frames
        - (dropframes * (total_minutes - std::floor(total_minutes/10)))
    );

    return RationalTime(value, rate);
}

std::string
to_timecode(const RationalTime& time_obj, rt_rate_t rate)
{
    // @TODO: Is this the right policy for C++
    if (time_obj.value < 0)
    {
        throw std::invalid_argument("time_obj has a negative value");
    }

    validate_timecode_rate(rate);

    bool rate_is_dropframe = ARRAY_CONTAINS(
            VALID_DROPFRAME_TIMECODE_RATES, rate);

    // extra math for dropframes stuff
    int dropframes = 0;
    char div = ':';
    if (not rate_is_dropframe)
    {
        if (std::round(rate) == 24)
        {
            rate = 24.0;
        }
    }
    else
    {
        if (rate == (rt_rate_t)29.97)
        {
            dropframes = 2;
        }
        else if(rate == (rt_rate_t)59.94)
        {
            dropframes = 4;
        }
        div = ';';
    }

    // Number of frames in an hour
    int frames_per_hour = std::round(rate * 60 * 60);
    // Number of frames in a day - timecode rolls over after 24 hours
    int frames_per_24_hours = frames_per_hour * 24;
    // Number of frames per ten minutes
    int frames_per_10_minutes = std::round(rate * 60 * 10);
    // Number of frames per minute is the round of the framerate * 60 minus
    // the number of dropped frames
    int frames_per_minute = (std::round(rate) * 60) - dropframes;

    // If the number of frames is more than 24 hours, roll over clock
    rt_value_t value = std::fmod(time_obj.value, frames_per_24_hours);

    if (rate_is_dropframe)
    {
        int ten_minute_chunks = std::floor(value/frames_per_10_minutes);
        int frames_over_ten_minutes = std::fmod(value, frames_per_10_minutes);

        if (frames_over_ten_minutes > dropframes)
        {
            value += (
                    (dropframes * 9 * ten_minute_chunks) 
                    + dropframes * std::floor(
                        (frames_over_ten_minutes - dropframes) 
                        / frames_per_minute
                    )
            );
        }
        else
        {
            value += dropframes * 9 * ten_minute_chunks;
        }
    }

    const int nominal_fps = std::ceil(rate);

    // compute the fields
    const int frames = std::fmod(value, nominal_fps);
    const int seconds_total = std::floor(value / nominal_fps);
    const int seconds = std::fmod(seconds_total, 60);
    const int minutes = std::fmod(std::floor(seconds_total / 60), 60);
    const int hours = std::floor(std::floor(seconds_total / 60) / 60);

    // print back out to a buffer
    const char *fmt = "%02d:%02d:%02d%c%02d";
    int sz = std::snprintf(
            nullptr, 0, fmt, hours,minutes,seconds,div,frames);
    std::vector<char> buf(sz + 1); // note +1 for null terminator
    std::snprintf(&buf[0], buf.size(), fmt, hours,minutes,seconds,div,frames);

    return &buf[0];
}

// overload for single-argument version
std::string
to_timecode(const RationalTime& time_obj)
{
    return to_timecode(time_obj, time_obj.rate);
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

/** Convert this timecode to time with microseconds, as formatted in FFMPEG.
 */
std::string
to_time_string(const RationalTime& time_obj)
{
    double time_obj_value = time_obj.value;
    double time_obj_rate = time_obj.rate;

    rt_value_t total_seconds = to_seconds(time_obj);
    bool is_wrong = (total_seconds == (double)86400);

    // @TODO: fun fact, this will print the wrong values for numbers at a certain 
    // number of decimal places, if you just std::cerr << total_seconds
    /* DEBUG_PRINT(total_seconds); */

    auto try2 = time_obj.value_rescaled_to(1.0);


    // reformat in time string
    constexpr rt_value_t time_units_per_minute = 60.0;
    constexpr rt_value_t time_units_per_hour = time_units_per_minute * 60.0;
    constexpr rt_value_t time_units_per_day = time_units_per_hour * 24.0;

    // 
    int days = std::floor(total_seconds / time_units_per_day);
    double hour_units = std::fmod((double)total_seconds, time_units_per_day);

    int hours = std::floor(hour_units / time_units_per_hour);
    double minute_units = std::fmod(hour_units, time_units_per_hour);

    int minutes = std::floor(minute_units / time_units_per_minute);
    double seconds = std::fmod(minute_units, time_units_per_minute);


    double fractpart, intpart;
    fractpart = std::modf(seconds, &intpart);

    std::string microseconds = std::to_string(std::floor(fractpart * 1e6));
    std::string str_seconds = std::to_string(intpart);

    const char *fmt = "%02d:%02d:%02d.%06d";
    int sz = std::snprintf(
            nullptr, 0, fmt, hours,minutes,std::stoi(str_seconds),std::stoi(microseconds));
    std::vector<char> buf(sz + 1); // note +1 for null terminator
    std::snprintf(&buf[0], buf.size(), fmt, hours,minutes,std::stoi(str_seconds),std::stoi(microseconds));

    return &buf[0];
}

/** Convert a time with microseconds string into a RationalTime.

:param time_str: (:class:`str`) A HH:MM:ss.ms time.
:param rate: (:class:`float`) The frame-rate to calculate timecode in
    terms of.

:return: (:class:`RationalTime`) Instance for the timecode provided.
*/
RationalTime
from_time_string(const std::string& time_str, rt_rate_t rate)
{
    if (ARRAY_CONTAINS(time_str, ';'))
    {
        throw std::invalid_argument("Drop frame timecode not supported.");
    }


    std::vector<std::string> fields {"","",""};

    // split the fields
    int last_pos = 0;
    for (int i=0; i<2; i++)
    {
        fields[i] = time_str.substr(last_pos, 2);
        last_pos = last_pos+3;
    }
    fields[2] = time_str.substr(last_pos, time_str.length());

    double hours   = std::stod(fields[0]);
    double minutes = std::stod(fields[1]);
    double seconds = std::stod(fields[2]);

    return from_seconds(
        seconds + minutes * 60 + hours * 60 * 60
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
