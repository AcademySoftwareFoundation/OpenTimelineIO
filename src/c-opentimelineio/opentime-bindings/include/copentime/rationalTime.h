#pragma once

#include "copentime/errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct RationalTime;
    typedef struct RationalTime RationalTime;

    typedef enum
    {
        OpenTime_IsDropFrameRate_InferFromRate = -1,
        OpenTime_IsDropFrameRate_ForceNo       = 0,
        OpenTime_IsDropFrameRate_ForceYes      = 1,
    } OpenTime_IsDropFrameRate_;
    typedef int   OpenTime_IsDropFrameRate;
    RationalTime* RationalTime_create(double value, double rate);
    _Bool         RationalTime_is_invalid_time(RationalTime* self);
    double        RationalTime_value(RationalTime* self);
    double        RationalTime_rate(RationalTime* self);
    RationalTime* RationalTime_rescaled_to(RationalTime* self, double new_rate);
    RationalTime* RationalTime_rescaled_to_rational_time(
        RationalTime* self, RationalTime* rt);
    double
           RationalTime_value_rescaled_to_rate(RationalTime* self, double new_rate);
    double RationalTime_value_rescaled_to_rational_time(
        RationalTime* self, RationalTime* rt);
    _Bool RationalTime_almost_equal(
        RationalTime* self, RationalTime* other, double delta);
    RationalTime* RationalTime_duration_from_start_end_time(
        RationalTime* start_time, RationalTime* end_time_exclusive);
    _Bool         RationalTime_is_valid_timecode_rate(double rate);
    RationalTime* RationalTime_from_frames(double frame, double rate);
    RationalTime* RationalTime_from_seconds(double seconds);
    RationalTime* RationalTime_from_timecode(
        const char* timecode, double rate, OpenTimeErrorStatus* error_status);
    RationalTime* RationalTime_from_time_string(
        const char* time_string, double rate, OpenTimeErrorStatus* error_status);
    int    RationalTime_to_frames(RationalTime* self);
    int    RationalTime_to_frames_with_rate(RationalTime* self, double rate);
    double RationalTime_to_seconds(RationalTime* self);
    const char* RationalTime_to_timecode(
        RationalTime*        self,
        double               rate,
        OpenTime_IsDropFrameRate drop_frame,
        OpenTimeErrorStatus*         error_status);
    const char* RationalTime_to_timecode_auto(
        RationalTime* self, OpenTimeErrorStatus* error_status);
    const char*   RationalTime_to_time_string(RationalTime* self);
    RationalTime* RationalTime_add(RationalTime* lhs, RationalTime* rhs);
    RationalTime* RationalTime_subtract(RationalTime* lhs, RationalTime* rhs);
    RationalTime* RationalTime_compare(RationalTime* lhs, RationalTime* rhs);
    _Bool         RationalTime_equal(RationalTime* lhs, RationalTime* rhs);
    _Bool         RationalTime_not_equal(RationalTime* lhs, RationalTime* rhs);
    void          RationalTime_destroy(RationalTime* self);
#ifdef __cplusplus
}
#endif
