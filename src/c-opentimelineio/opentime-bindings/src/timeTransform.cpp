#include "copentime/timeTransform.h"
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>

#ifdef __cplusplus
extern "C"
{
#endif
    TimeTransform* TimeTransform_create()
    {
        return reinterpret_cast<TimeTransform*>(new opentime::TimeTransform());
    }
    TimeTransform* TimeTransform_create_with_offset_scale_rate(
        RationalTime* offset, double scale, double rate)
    {
        return reinterpret_cast<TimeTransform*>(new opentime::TimeTransform(
            *reinterpret_cast<opentime::RationalTime*>(offset), scale, rate));
    }
    RationalTime* TimeTransform_offset(TimeTransform* self)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeTransform*>(self)->offset();
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    double TimeTransform_scale(TimeTransform* self)
    {
        return reinterpret_cast<opentime::TimeTransform*>(self)->scale();
    }
    double TimeTransform_rate(TimeTransform* self)
    {
        return reinterpret_cast<opentime::TimeTransform*>(self)->rate();
    }
    TimeRange*
    TimeTransform_applied_to_time_range(TimeTransform* self, TimeRange* other)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<opentime::TimeTransform*>(self)->applied_to(
                *reinterpret_cast<opentime::TimeRange*>(other));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeTransform* TimeTransform_applied_to_time_transform(
        TimeTransform* self, TimeTransform* other)
    {
        opentime::TimeTransform obj =
            reinterpret_cast<opentime::TimeTransform*>(self)->applied_to(
                *reinterpret_cast<opentime::TimeTransform*>(other));
        return reinterpret_cast<TimeTransform*>(
            new opentime::TimeTransform(obj));
    }
    RationalTime* TimeTransform_applied_to_rational_time(
        TimeTransform* self, RationalTime* other)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeTransform*>(self)->applied_to(
                *reinterpret_cast<opentime::RationalTime*>(other));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    _Bool TimeTransform_equal(TimeTransform* lhs, TimeTransform* rhs)
    {
        return *reinterpret_cast<opentime::TimeTransform*>(lhs) ==
               *reinterpret_cast<opentime::TimeTransform*>(rhs);
    }
    _Bool TimeTransform_not_equal(TimeTransform* lhs, TimeTransform* rhs)
    {
        return *reinterpret_cast<opentime::TimeTransform*>(lhs) !=
               *reinterpret_cast<opentime::TimeTransform*>(rhs);
    }
    void TimeTransform_destroy(TimeTransform* self)
    {
        delete reinterpret_cast<opentime::TimeTransform*>(self);
    }
#ifdef __cplusplus
}
#endif
