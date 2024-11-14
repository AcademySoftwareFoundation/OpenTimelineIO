// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentime/rationalTime.h"
#include "opentime/stringPrintf.h"
#include <algorithm>
#include <array>
#include <ciso646>
#include <cmath>
#include <vector>

namespace opentime { namespace OPENTIME_VERSION {

RationalTime RationalTime::_invalid_time{ 0, RationalTime::_invalid_rate };

static constexpr std::array<double, 2> dropframe_timecode_rates{ {
    30000.0 / 1001.0,
    60000.0 / 1001.0,
} };

// See the official source of these numbers here:
// ST 12-1:2014 - SMPTE Standard - Time and Control Code
// https://ieeexplore.ieee.org/document/7291029
//
static constexpr std::array<double, 11> smpte_timecode_rates{
    { 24000.0 / 1001.0,
      24.0,
      25.0,
      30000.0 / 1001.0,
      30.0,
      48000.0 / 1001.0,
      48.0,
      50.0,
      60000.0 / 1001.0,
      60.0
    }
};

// deprecated in favor of `is_smpte_timecode_rate`
bool
RationalTime::is_valid_timecode_rate(double fps)
{
    return is_smpte_timecode_rate(fps);
}

bool
RationalTime::is_smpte_timecode_rate(double fps)
{
    auto b = smpte_timecode_rates.begin(), e = smpte_timecode_rates.end();
    return std::find(b, e, fps) != e;
}

// deprecated in favor of `is_smpte_timecode_rate`
double
RationalTime::nearest_valid_timecode_rate(double rate)
{
    return nearest_smpte_timecode_rate(rate);
}

double
RationalTime::nearest_smpte_timecode_rate(double rate)
{
    double nearest_rate = 0;
    double min_diff     = std::numeric_limits<double>::max();
    for (auto smpte_rate: smpte_timecode_rates)
    {
        if (smpte_rate == rate)
        {
            return rate;
        }
        auto diff = std::abs(rate - smpte_rate);
        if (diff >= min_diff)
        {
            continue;
        }
        min_diff     = diff;
        nearest_rate = smpte_rate;
    }
    return nearest_rate;
}

static bool
is_dropframe_rate(double rate)
{
    auto b = dropframe_timecode_rates.begin(),
         e = dropframe_timecode_rates.end();
    return std::find(b, e, rate) != e;
}

static bool
parseFloat(
    char const* pCurr,
    char const* pEnd,
    bool        allow_negative,
    double*     result)
{
    if (pCurr >= pEnd || !pCurr)
    {
        *result = 0.0;
        return false;
    }

    double ret  = 0.0;
    double sign = 1.0;

    if (*pCurr == '+')
    {
        ++pCurr;
    }
    else if (*pCurr == '-')
    {
        if (!allow_negative)
        {
            *result = 0.0;
            return false;
        }
        sign = -1.0;
        ++pCurr;
    }

    // get integer part
    //
    // Note that uint64_t is used because overflow is well defined for
    // unsigned integers, but it is undefined behavior for signed integers,
    // and floating point values are couched in the specification with
    // the caveat that an implementation may be IEEE-754 compliant, or only
    // partially compliant.
    //
    uint64_t uintPart = 0;
    while (pCurr < pEnd)
    {
        char c = *pCurr;
        if (c < '0' || c > '9')
        {
            break;
        }
        uint64_t accumulated = uintPart * 10 + c - '0';
        if (accumulated < uintPart)
        {
            // if there are too many digits, resulting in an overflow, fail
            *result = 0.0;
            return false;
        }
        uintPart = accumulated;
        ++pCurr;
    }

    ret = static_cast<double>(uintPart);
    if (uintPart != static_cast<uint64_t>(ret))
    {
        // if the double cannot be casted precisely back to uint64_t, fail
        // A double has 15 digits of precision, but a uint64_t can encode more.
        *result = 0.0;
        return false;
    }

    // check for end of string or delimiter
    if (pCurr == pEnd || *pCurr == '\0')
    {
        *result = sign * ret;
        return true;
    }

    // if the next character is not a decimal point, the string is malformed.
    if (*pCurr != '.')
    {
        *result = 0.0; // zero consistent with earlier error condition
        return false;
    }

    ++pCurr; // skip decimal

    double position_scale = 0.1;
    while (pCurr < pEnd)
    {
        char c = *pCurr;
        if (c < '0' || c > '9')
        {
            break;
        }
        ret = ret + static_cast<double>(c - '0') * position_scale;
        ++pCurr;
        position_scale *= 0.1;
    }

    *result = sign * ret;
    return true;
}

RationalTime
RationalTime::from_timecode(
    std::string const& timecode,
    double             rate,
    ErrorStatus*       error_status)
{
    if (!RationalTime::is_smpte_timecode_rate(rate))
    {
        if (error_status)
        {
            *error_status = ErrorStatus{ ErrorStatus::INVALID_TIMECODE_RATE };
        }
        return RationalTime::_invalid_time;
    }

    bool rate_is_dropframe = is_dropframe_rate(rate);

    if (timecode.find(';') != std::string::npos)
    {
        if (!rate_is_dropframe)
        {
            if (error_status)
            {
                *error_status = ErrorStatus(
                    ErrorStatus::INVALID_RATE_FOR_DROP_FRAME_TIMECODE,
                    string_printf(
                        "Timecode '%s' indicates drop frame rate due "
                        "to the ';' frame divider. "
                        "Passed in rate %g is not a valid drop frame rate.",
                        timecode.c_str(),
                        rate));
            }
            return RationalTime::_invalid_time;
        }
    }
    else
    {
        rate_is_dropframe = false;
    }

    std::vector<std::string> fields{ "", "", "", "" };
    int                      hours, minutes, seconds, frames;

    try
    {
        // split the fields
        unsigned int last_pos = 0;
        for (unsigned int i = 0; i < 4; i++)
        {
            fields[i] = timecode.substr(last_pos, 2);
            last_pos  = last_pos + 3;
        }

        hours   = std::stoi(fields[0]);
        minutes = std::stoi(fields[1]);
        seconds = std::stoi(fields[2]);
        frames  = std::stoi(fields[3]);
    }
    catch (std::exception const&)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::INVALID_TIMECODE_STRING,
                string_printf(
                    "Input timecode '%s' is an invalid timecode",
                    timecode.c_str()));
        }
        return RationalTime::_invalid_time;
    }

    const int nominal_fps = static_cast<int>(std::ceil(rate));

    if (frames >= nominal_fps)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::TIMECODE_RATE_MISMATCH,
                string_printf(
                    "Frame rate mismatch.  Timecode '%s' has "
                    "frames beyond %d",
                    timecode.c_str(),
                    nominal_fps - 1));
        }
        return RationalTime::_invalid_time;
    }

    int dropframes = 0;
    if (rate_is_dropframe)
    {
        if ((rate == 29.97) or (rate == 30000 / 1001.0))
        {
            dropframes = 2;
        }
        else if ((rate == 59.94) or (rate == 60000 / 1001.0))
        {
            dropframes = 4;
        }
    }

    // to use for drop frame compensation
    int total_minutes = hours * 60 + minutes;

    // convert to frames
    const int value =
        (((total_minutes * 60) + seconds) * nominal_fps + frames
         - (dropframes
            * (total_minutes
               - static_cast<int>(std::floor(total_minutes / 10)))));

    return RationalTime{ double(value), rate };
}

static void
set_error(
    std::string const&   time_string,
    ErrorStatus::Outcome code,
    ErrorStatus*         err)
{
    if (err)
    {
        *err = ErrorStatus(
            code,
            string_printf(
                "Error: '%s' - %s",
                time_string.c_str(),
                ErrorStatus::outcome_to_string(code).c_str()));
    }
}

RationalTime
RationalTime::from_time_string(
    std::string const& time_string,
    double             rate,
    ErrorStatus*       error_status)
{
    if (!RationalTime::is_smpte_timecode_rate(rate))
    {
        set_error(
            time_string,
            ErrorStatus::INVALID_TIMECODE_RATE,
            error_status);
        return RationalTime::_invalid_time;
    }

    const char* start          = time_string.data();
    const char* end            = start + time_string.length();
    char*       current        = const_cast<char*>(end);
    char*       parse_end      = current;
    char*       prev_parse_end = current;

    double power[3] = {
        1.0,   // seconds
        60.0,  // minutes
        3600.0 // hours
    };

    double accumulator = 0.0;
    int    radix       = 0;
    while (start <= current)
    {
        if (*current == ':')
        {
            parse_end = current + 1;
            char c    = *parse_end;
            if (c != '\0' && c != ':')
            {
                if (c < '0' || c > '9')
                {
                    set_error(
                        time_string,
                        ErrorStatus::INVALID_TIME_STRING,
                        error_status);
                    return RationalTime::_invalid_time;
                }
                double val = 0.0;
                if (!parseFloat(parse_end, prev_parse_end + 1, false, &val))
                {
                    set_error(
                        time_string,
                        ErrorStatus::INVALID_TIME_STRING,
                        error_status);
                    return RationalTime::_invalid_time;
                }
                prev_parse_end = nullptr;
                if (radix < 2 && val >= 60.0)
                {
                    set_error(
                        time_string,
                        ErrorStatus::INVALID_TIME_STRING,
                        error_status);
                    return RationalTime::_invalid_time;
                }
                accumulator += val * power[radix];
            }
            ++radix;
            if (radix == sizeof(power) / sizeof(power[0]))
            {
                set_error(
                    time_string,
                    ErrorStatus::INVALID_TIME_STRING,
                    error_status);
                return RationalTime::_invalid_time;
            }
        }
        else if (
            current < prev_parse_end && (*current < '0' || *current > '9')
            && *current != '.')
        {
            set_error(
                time_string,
                ErrorStatus::INVALID_TIME_STRING,
                error_status);
            return RationalTime::_invalid_time;
        }

        if (start == current)
        {
            if (prev_parse_end)
            {
                double val = 0.0;
                if (!parseFloat(start, prev_parse_end + 1, true, &val))
                {
                    set_error(
                        time_string,
                        ErrorStatus::INVALID_TIME_STRING,
                        error_status);
                    return RationalTime::_invalid_time;
                }
                accumulator += val * power[radix];
            }
            break;
        }
        --current;
        if (!prev_parse_end)
        {
            prev_parse_end = current;
        }
    }

    return from_seconds(accumulator).rescaled_to(rate);
}

std::string
RationalTime::to_timecode(
    double          rate,
    IsDropFrameRate drop_frame,
    ErrorStatus*    error_status) const
{
    if (error_status)
    {
        *error_status = ErrorStatus();
    }

    double frames_in_target_rate = this->value_rescaled_to(rate);

    if (frames_in_target_rate < 0)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(ErrorStatus::NEGATIVE_VALUE);
        }
        return std::string();
    }

    double nearest_smpte_rate = nearest_smpte_timecode_rate(rate);
    if (abs(nearest_smpte_rate - rate) > 0.1)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(ErrorStatus::INVALID_TIMECODE_RATE);
        }
        return std::string();
    }

    // Let's assume this is the rate instead of the given rate.
    rate = nearest_smpte_rate;

    bool rate_is_dropframe = is_dropframe_rate(rate);
    if (drop_frame == IsDropFrameRate::ForceYes and not rate_is_dropframe)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::INVALID_RATE_FOR_DROP_FRAME_TIMECODE);
        }
        return std::string();
    }

    if (drop_frame != IsDropFrameRate::InferFromRate)
    {
        if (drop_frame == IsDropFrameRate::ForceYes)
        {
            rate_is_dropframe = true;
        }
        else
        {
            rate_is_dropframe = false;
        }
    }

    // extra math for dropframes stuff
    int  dropframes = 0;
    char div        = ':';
    if (!rate_is_dropframe)
    {
        if (std::round(rate) == 24)
        {
            rate = 24.0;
        }
    }
    else
    {
        if (rate == 30000 / 1001.0)
        {
            dropframes = 2;
        }
        else if (rate == 60000 / 1001.0)
        {
            dropframes = 4;
        }
        div = ';';
    }

    // Number of frames in an hour
    int frames_per_hour = static_cast<int>(std::round(rate * 60 * 60));
    // Number of frames in a day - timecode rolls over after 24 hours
    int frames_per_24_hours = frames_per_hour * 24;
    // Number of frames per ten minutes
    int frames_per_10_minutes = static_cast<int>(std::round(rate * 60 * 10));
    // Number of frames per minute is the round of the framerate * 60 minus
    // the number of dropped frames
    int frames_per_minute =
        static_cast<int>((std::round(rate) * 60) - dropframes);

    // If the number of frames is more than 24 hours, roll over clock
    double value = std::fmod(frames_in_target_rate, frames_per_24_hours);

    if (rate_is_dropframe)
    {
        int ten_minute_chunks =
            static_cast<int>(std::floor(value / frames_per_10_minutes));
        int frames_over_ten_minutes =
            static_cast<int>(std::fmod(value, frames_per_10_minutes));

        if (frames_over_ten_minutes > dropframes)
        {
            value += (dropframes * 9 * ten_minute_chunks)
                     + dropframes
                           * std::floor(
                               (frames_over_ten_minutes - dropframes)
                               / frames_per_minute);
        }
        else
        {
            value += dropframes * 9 * ten_minute_chunks;
        }
    }

    int nominal_fps = static_cast<int>(std::ceil(rate));

    // compute the fields
    int frames        = static_cast<int>(std::fmod(value, nominal_fps));
    int seconds_total = static_cast<int>(std::floor(value / nominal_fps));
    int seconds       = static_cast<int>(std::fmod(seconds_total, 60));
    int minutes =
        static_cast<int>(std::fmod(std::floor(seconds_total / 60), 60));
    int hours =
        static_cast<int>(std::floor(std::floor(seconds_total / 60) / 60));

    return string_printf(
        "%02d:%02d:%02d%c%02d",
        hours,
        minutes,
        seconds,
        div,
        frames);
}

std::string
RationalTime::to_nearest_timecode(
    double          rate,
    IsDropFrameRate drop_frame,
    ErrorStatus*    error_status) const
{
    std::string result = to_timecode(rate, drop_frame, error_status);

    if (error_status)
    {
        *error_status = ErrorStatus();

        double nearest_rate = nearest_smpte_timecode_rate(rate);

        return to_timecode(nearest_rate, drop_frame, error_status);
    }

    return result;
}

std::string
RationalTime::to_time_string() const
{
    double total_seconds = to_seconds();
    bool   is_negative   = false;

    // We always want to compute with positive numbers to get the right string
    // result and return the string at the end with a '-'. This provides
    // compatibility with ffmpeg, which allows negative time strings.
    if (std::signbit(total_seconds))
    {
        total_seconds = fabs(total_seconds);
        is_negative   = true;
    }

    // @TODO: fun fact, this will print the wrong values for numbers at a
    // certain number of decimal places, if you just std::cerr << total_seconds

    // reformat in time string
    constexpr double time_units_per_minute = 60.0;
    constexpr double time_units_per_hour   = time_units_per_minute * 60.0;
    constexpr double time_units_per_day    = time_units_per_hour * 24.0;

    double hour_units = std::fmod((double) total_seconds, time_units_per_day);

    int hours = static_cast<int>(std::floor(hour_units / time_units_per_hour));
    double minute_units = std::fmod(hour_units, time_units_per_hour);

    int minutes =
        static_cast<int>(std::floor(minute_units / time_units_per_minute));
    double seconds = std::fmod(minute_units, time_units_per_minute);

    // split the seconds string apart
    double fractpart, intpart;

    fractpart = modf(seconds, &intpart);

    // clamp to 2 digits and zero-pad
    std::string seconds_str = string_printf("%02d", (int) intpart);

    // get the fractional component (with enough digits of resolution)
    std::string microseconds_str = string_printf("%.7g", fractpart);

    // trim leading 0
    microseconds_str = microseconds_str.substr(1);

    // enforce the minimum string of '.0'
    if (microseconds_str.length() == 0)
    {
        microseconds_str = std::string(".0");
    }
    else
    {
        // ...and the string size
        microseconds_str.resize(7, '\0');
    }

    // if the initial time value was negative, return the string with a '-'
    // sign
    std::string sign = is_negative ? "-" : "";

    return string_printf(
        // decimal should already be in the microseconds_str
        "%s%02d:%02d:%s%s",
        sign.c_str(),
        hours,
        minutes,
        seconds_str.c_str(),
        microseconds_str.c_str());
}

}} // namespace opentime::OPENTIME_VERSION
