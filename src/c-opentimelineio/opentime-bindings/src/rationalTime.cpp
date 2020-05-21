#include "copentime/rationalTime.h"
#include <opentime/rationalTime.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    RationalTime* RationalTime_create(double value, double rate)
    {
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(value, rate));
    }
    _Bool RationalTime_is_invalid_time(RationalTime* self)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)
            ->is_invalid_time();
    }
    double RationalTime_value(RationalTime* self)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)->value();
    }
    double RationalTime_rate(RationalTime* self)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)->rate();
    }
    RationalTime* RationalTime_rescaled_to(RationalTime* self, double new_rate)
    {
        opentime::RationalTime obj =
            reinterpret_cast<opentime::RationalTime*>(self)->rescaled_to(
                new_rate);
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    RationalTime*
    RationalTime_rescaled_to_rational_time(RationalTime* self, RationalTime* rt)
    {
        opentime::RationalTime obj =
            reinterpret_cast<opentime::RationalTime*>(self)->rescaled_to(
                *reinterpret_cast<opentime::RationalTime*>(rt));
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    double
    RationalTime_value_rescaled_to_rate(RationalTime* self, double new_rate)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)
            ->value_rescaled_to(new_rate);
    }
    double RationalTime_value_rescaled_to_rational_time(
        RationalTime* self, RationalTime* rt)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)
            ->value_rescaled_to(*reinterpret_cast<opentime::RationalTime*>(rt));
    }
    _Bool RationalTime_almost_equal(
        RationalTime* self, RationalTime* other, double delta)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)->almost_equal(
            *reinterpret_cast<opentime::RationalTime*>(other), delta);
    }
    RationalTime* RationalTime_duration_from_start_end_time(
        RationalTime* start_time, RationalTime* end_time_exclusive)
    {
        opentime::RationalTime obj =
            opentime::RationalTime::duration_from_start_end_time(
                *reinterpret_cast<opentime::RationalTime*>(start_time),
                *reinterpret_cast<opentime::RationalTime*>(end_time_exclusive));
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    _Bool RationalTime_is_valid_timecode_rate(double rate)
    {
        return opentime::RationalTime::is_valid_timecode_rate(rate);
    }
    RationalTime* RationalTime_from_frames(double frame, double rate)
    {
        opentime::RationalTime obj =
            opentime::RationalTime::from_frames(frame, rate);
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    RationalTime* RationalTime_from_seconds(double seconds)
    {
        opentime::RationalTime obj =
            opentime::RationalTime::from_seconds(seconds);
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    RationalTime* RationalTime_from_timecode(
        const char* timecode, double rate, OpenTimeErrorStatus* error_status)
    {
        opentime::RationalTime obj = opentime::RationalTime::from_timecode(
            timecode,
            rate,
            reinterpret_cast<opentime::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    RationalTime* RationalTime_from_time_string(
        const char* time_string, double rate, OpenTimeErrorStatus* error_status)
    {
        opentime::RationalTime obj = opentime::RationalTime::from_time_string(
            time_string,
            rate,
            reinterpret_cast<opentime::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    int RationalTime_to_frames(RationalTime* self)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)->to_frames();
    }
    int RationalTime_to_frames_with_rate(RationalTime* self, double rate)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)->to_frames(rate);
    }
    double RationalTime_to_seconds(RationalTime* self)
    {
        return reinterpret_cast<opentime::RationalTime*>(self)->to_seconds();
    }
    const char* RationalTime_to_timecode(
        RationalTime*            self,
        double                   rate,
        OpenTime_IsDropFrameRate drop_frame,
        OpenTimeErrorStatus*     error_status)
    {
        std::string returnStr =
            reinterpret_cast<opentime::RationalTime*>(self)->to_timecode(
                rate,
                static_cast<opentime::IsDropFrameRate>(drop_frame),
                reinterpret_cast<opentime::ErrorStatus*>(error_status));
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    const char* RationalTime_to_timecode_auto(
        RationalTime* self, OpenTimeErrorStatus* error_status)
    {
        std::string returnStr =
            reinterpret_cast<opentime::RationalTime*>(self)->to_timecode(
                reinterpret_cast<opentime::ErrorStatus*>(error_status));
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    const char* RationalTime_to_time_string(RationalTime* self)
    {
        std::string returnStr =
            reinterpret_cast<opentime::RationalTime*>(self)->to_time_string();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }

    RationalTime* RationalTime_add(RationalTime* lhs, RationalTime* rhs)
    {
        opentime::RationalTime obj =
            *reinterpret_cast<opentime::RationalTime*>(lhs) +
            *reinterpret_cast<opentime::RationalTime*>(rhs);
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    RationalTime* RationalTime_subtract(RationalTime* lhs, RationalTime* rhs)
    {
        opentime::RationalTime obj =
            *reinterpret_cast<opentime::RationalTime*>(lhs) -
            *reinterpret_cast<opentime::RationalTime*>(rhs);
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    RationalTime* RationalTime_compare(RationalTime* lhs, RationalTime* rhs)
    {
        opentime::RationalTime obj =
            *reinterpret_cast<opentime::RationalTime*>(rhs) -
            *reinterpret_cast<opentime::RationalTime*>(lhs);
        return reinterpret_cast<RationalTime*>(new opentime::RationalTime(obj));
    }
    _Bool RationalTime_equal(RationalTime* lhs, RationalTime* rhs)
    {
        return *reinterpret_cast<opentime::RationalTime*>(rhs) ==
               *reinterpret_cast<opentime::RationalTime*>(lhs);
    }
    _Bool RationalTime_not_equal(RationalTime* lhs, RationalTime* rhs)
    {
        return *reinterpret_cast<opentime::RationalTime*>(rhs) !=
               *reinterpret_cast<opentime::RationalTime*>(lhs);
    }

    void RationalTime_destroy(RationalTime* self)
    {
        delete reinterpret_cast<opentime::RationalTime*>(self);
    }
#ifdef __cplusplus
}
#endif
