#include "opentime/rationalTime.h"
#include "opentime/stringPrintf.h"
#include <array>
#include <algorithm>
#include <ciso646>
#include <cmath>
#include <vector>

namespace opentime { namespace OPENTIME_VERSION  {
    
RationalTime RationalTime::_invalid_time {0, RationalTime::_invalid_rate};

static constexpr std::array<double, 4> dropframe_timecode_rates
{{
    // 23.976,
    // 23.98,
    // 23.97,
    // 24000.0/1001.0,
    29.97,
    30000.0/1001.0,
    59.94,
    60000.0/1001.0,
}};

// currently unused:
/*
static constexpr std::array<double, 10> non_dropframe_timecode_rates
{{  1,
    12,
    23.976,
    23.98,
    24,
    25,
    30,
    48,
    50,
    60
}};
*/

static constexpr std::array<double, 16> valid_timecode_rates
{{  
    1.0,
    12.0,
    23.97,
    23.976,
    23.98,
    24000.0/1001.0,
    24.0,
    25.0,
    29.97,
    30000.0/1001.0,
    30.0,
    48.0,
    50.0,
    59.94,
    60000.0/1001.0,
    60.0
}};

bool RationalTime::is_valid_timecode_rate(double fps) {
    auto b = valid_timecode_rates.begin(),
         e = valid_timecode_rates.end();
    return std::find(b, e, fps) != e;
}

static bool is_dropframe_rate(double rate) {
    auto b = dropframe_timecode_rates.begin(),
         e = dropframe_timecode_rates.end();
    return std::find(b, e, rate) != e;
}

RationalTime
RationalTime::from_timecode(std::string const& timecode, double rate, ErrorStatus* error_status) {
    if (!RationalTime::is_valid_timecode_rate(rate)) {
        *error_status = ErrorStatus {ErrorStatus::INVALID_TIMECODE_RATE};
        return RationalTime::_invalid_time;
    }

    bool rate_is_dropframe = is_dropframe_rate(rate);

    if (timecode.find(';') != std::string::npos) {
        if (!rate_is_dropframe) {
            *error_status = ErrorStatus(ErrorStatus::NON_DROPFRAME_RATE,
                                        string_printf("Timecode '%s' indicates drop frame rate due "
                                                      "to the ';' frame divider. "
                                                      "Passed in rate %g is of non-drop-frame-rate.",
                                                      timecode.c_str(), rate));
            return RationalTime::_invalid_time;
        }
    } else {
        rate_is_dropframe = false;
    }

    std::vector<std::string> fields {"","","",""};
    int hours, minutes, seconds, frames;

    try {
        // split the fields
        unsigned int last_pos = 0;
        for (unsigned int i = 0; i < 4; i++) {
            fields[i] = timecode.substr(last_pos, 2);
            last_pos = last_pos+3;
        }

        hours   = std::stoi(fields[0]);
        minutes = std::stoi(fields[1]);
        seconds = std::stoi(fields[2]);
        frames  = std::stoi(fields[3]);
    } catch(std::exception e) {
        *error_status = ErrorStatus(ErrorStatus::INVALID_TIMECODE_STRING,
                                    string_printf("Input timecode '%s' is an invalid timecode",
                                                  timecode.c_str()));
        return RationalTime::_invalid_time;
    }

    const int nominal_fps = static_cast<int>(std::ceil(rate));

    if (frames >= nominal_fps) {
        *error_status = ErrorStatus(ErrorStatus::TIMECODE_RATE_MISMATCH,
                                    string_printf("Frame rate mismatch.  Timecode '%s' has "
                                                  "frames beyond %f", timecode.c_str(),
                                                  nominal_fps - 1));
        return RationalTime::_invalid_time;
    }

    int dropframes = 0;
    if (rate_is_dropframe) {
        if ((rate == 29.97) or (rate == 30000/1001.0)) {
            dropframes = 2;
        }
        else if ((rate == 59.94) or (rate == 60000/1001.0)) {
            dropframes = 4;
        }
    }

    // to use for drop frame compensation
    int total_minutes = hours * 60 + minutes;

    // convert to frames
    const int value = (
        ((total_minutes * 60) + seconds) * nominal_fps 
        + frames
        - (
            dropframes 
            * (total_minutes - static_cast<int>(std::floor(total_minutes/10)))
          )
    );

    return RationalTime {double(value), rate};
}

RationalTime
RationalTime::from_time_string(std::string const& time_string, double rate, ErrorStatus* error_status) {
    if (!RationalTime::is_valid_timecode_rate(rate)) {
        *error_status = ErrorStatus(ErrorStatus::INVALID_TIMECODE_RATE);
        return RationalTime::_invalid_time;
    }

    std::vector<std::string> fields(3, std::string());

    // split the fields
    int last_pos = 0;

    for (int i = 0; i < 2; i++) {
        fields[i] = time_string.substr(last_pos, 2);
        last_pos = last_pos+3;
    }

    fields[2] = time_string.substr(last_pos, time_string.length());

    double hours, minutes, seconds;
    
    try {
        hours   = std::stod(fields[0]);
        minutes = std::stod(fields[1]);
        seconds = std::stod(fields[2]);
    } catch(std::exception e) {
        *error_status = ErrorStatus(ErrorStatus::INVALID_TIME_STRING,
                                    string_printf("Input time string '%s' is an invalid time string",
                                                  time_string.c_str()));
        return RationalTime::_invalid_time;
    }

    return from_seconds(seconds + minutes * 60 + hours * 60 * 60).rescaled_to(rate);
}

std::string
RationalTime::to_timecode(
        double rate,
        IsDropFrameRate drop_frame,
        ErrorStatus* error_status
) const {

    *error_status = ErrorStatus();

    double frames_in_target_rate = this->value_rescaled_to(rate);
    
    if (frames_in_target_rate < 0) {
        *error_status = ErrorStatus(ErrorStatus::NEGATIVE_VALUE);
        return std::string();
    }
        
    if (!is_valid_timecode_rate(rate)) {
        *error_status = ErrorStatus(ErrorStatus::INVALID_TIMECODE_RATE);
        return std::string();
    }

    bool rate_is_dropframe = is_dropframe_rate(rate);
    if (drop_frame == IsDropFrameRate::ForceYes and not rate_is_dropframe) {
        *error_status = ErrorStatus(
                ErrorStatus::INVALID_RATE_FOR_DROP_FRAME_TIMECODE
        );
        return std::string();
    }

    if (drop_frame != IsDropFrameRate::InferFromRate) {
        if (drop_frame == IsDropFrameRate::ForceYes) {
            rate_is_dropframe = true;
        }
        else {
            rate_is_dropframe = false;
        }
    }

    // extra math for dropframes stuff
    int dropframes = 0;
    char div = ':';
    if (!rate_is_dropframe)
    {
        if (std::round(rate) == 24) {
            rate = 24.0;
        }
    }
    else {
        if ((rate == 29.97) or (rate == 30000/1001.0)) {
            dropframes = 2;
        }
        else if(rate == 59.94) {
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
    int frames_per_minute = static_cast<int>(
            (std::round(rate) * 60) - dropframes);

    // If the number of frames is more than 24 hours, roll over clock
    double value = std::fmod(frames_in_target_rate, frames_per_24_hours);

    if (rate_is_dropframe) {
        int ten_minute_chunks = static_cast<int>(std::floor(value/frames_per_10_minutes));
        int frames_over_ten_minutes = static_cast<int>(std::fmod(value, frames_per_10_minutes));

        if (frames_over_ten_minutes > dropframes) {
            value += (dropframes * 9 * ten_minute_chunks) +
                dropframes * std::floor((frames_over_ten_minutes - dropframes) / frames_per_minute);
        }
        else {
            value += dropframes * 9 * ten_minute_chunks;
        }
    }

    int nominal_fps = static_cast<int>(std::ceil(rate));

    // compute the fields
    int frames = static_cast<int>(std::fmod(value, nominal_fps));
    int seconds_total = static_cast<int>(std::floor(value / nominal_fps));
    int seconds = static_cast<int>(std::fmod(seconds_total, 60));
    int minutes = static_cast<int>(std::fmod(std::floor(seconds_total / 60), 60));
    int hours = static_cast<int>(std::floor(std::floor(seconds_total / 60) / 60));

    return string_printf("%02d:%02d:%02d%c%02d", hours, minutes, seconds, div, frames);
}

std::string
RationalTime::to_time_string() const {
    double total_seconds = to_seconds();
    bool is_negative = false;

    // We always want to compute with positive numbers to get the right string
    // result and return the string at the end with a '-'. This provides
    // compatibility with ffmpeg, which allows negative time strings.
    if (std::signbit(total_seconds)) {
        total_seconds = abs(total_seconds);
        is_negative = true;
    }

    // @TODO: fun fact, this will print the wrong values for numbers at a
    // certain number of decimal places, if you just std::cerr << total_seconds

    // reformat in time string
    constexpr double time_units_per_minute = 60.0;
    constexpr double time_units_per_hour = time_units_per_minute * 60.0;
    constexpr double time_units_per_day = time_units_per_hour * 24.0;

    double hour_units = std::fmod((double)total_seconds, time_units_per_day);

    int hours = static_cast<int>(std::floor(hour_units / time_units_per_hour));
    double minute_units = std::fmod(hour_units, time_units_per_hour);

    int minutes = static_cast<int>(std::floor(minute_units / time_units_per_minute));
    double seconds = std::fmod(minute_units, time_units_per_minute);

    // split the seconds string apart
    double fractpart, intpart;

    fractpart = modf(seconds, &intpart);

    // clamp to 2 digits and zero-pad
    std::string seconds_str = string_printf("%02d", (int)intpart);

    // get the fractional component (with enough digits of resolution)
    std::string microseconds_str = string_printf("%.7g", fractpart);

    // trim leading 0
    microseconds_str = microseconds_str.substr(1);

    // enforce the minimum string of '.0'
    if (microseconds_str.length() == 0) {
        microseconds_str = std::string(".0");
    }
    else {
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
            microseconds_str.c_str()
    );
}

} }

