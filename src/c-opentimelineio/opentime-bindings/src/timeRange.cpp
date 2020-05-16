#include "copentime/timeRange.h"
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>

#ifdef __cplusplus
extern "C"
{
#endif
    TimeRange* TimeRange_create()
    {
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange());
    }
    TimeRange* TimeRange_create_with_start_time(RationalTime* start_time)
    {
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(
            *reinterpret_cast<opentime::RationalTime*>(start_time)));
    }
    TimeRange* TimeRange_create_with_start_time_and_duration(
        RationalTime* start_time, RationalTime* duration)
    {
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(
            *reinterpret_cast<opentime::RationalTime*>(start_time),
            *reinterpret_cast<opentime::RationalTime*>(duration)));
    }
    RationalTime* TimeRange_start_time(TimeRange* self)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeRange*>(self)->start_time();
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    RationalTime* TimeRange_duration(TimeRange* self)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeRange*>(self)->duration();
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    RationalTime* TimeRange_end_time_inclusive(TimeRange* self)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeRange*>(self)->end_time_inclusive();
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    RationalTime* TimeRange_end_time_exclusive(TimeRange* self)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeRange*>(self)->end_time_exclusive();
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    TimeRange*
    TimeRange_duration_extended_by(TimeRange* self, RationalTime* other)
    {
        opentime::TimeRange obj =
            reinterpret_cast<opentime::TimeRange*>(self)->duration_extended_by(
                *reinterpret_cast<opentime::RationalTime*>(other));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(obj));
    }
    TimeRange* TimeRange_extended_by(TimeRange* self, TimeRange* other)
    {
        opentime::TimeRange obj =
            reinterpret_cast<opentime::TimeRange*>(self)->extended_by(
                *reinterpret_cast<opentime::TimeRange*>(other));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(obj));
    }
    RationalTime*
    TimeRange_clamped_with_rational_time(TimeRange* self, RationalTime* other)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<opentime::TimeRange*>(self)->clamped(
                *reinterpret_cast<opentime::RationalTime*>(other));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    TimeRange*
    TimeRange_clamped_with_time_range(TimeRange* self, TimeRange* other)
    {
        opentime::TimeRange obj =
            reinterpret_cast<opentime::TimeRange*>(self)->clamped(
                *reinterpret_cast<opentime::TimeRange*>(other));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(obj));
    }
    _Bool TimeRange_contains_rational_time(TimeRange* self, RationalTime* other)
    {
        return reinterpret_cast<opentime::TimeRange*>(self)->contains(
            *reinterpret_cast<opentime::RationalTime*>(other));
    }
    _Bool TimeRange_contains_time_range(TimeRange* self, TimeRange* other)
    {
        return reinterpret_cast<opentime::TimeRange*>(self)->contains(
            *reinterpret_cast<opentime::TimeRange*>(other));
    }
    _Bool TimeRange_overlaps_rational_time(TimeRange* self, RationalTime* other)
    {
        return reinterpret_cast<opentime::TimeRange*>(self)->overlaps(
            *reinterpret_cast<opentime::RationalTime*>(other));
    }
    _Bool TimeRange_overlaps_time_range(TimeRange* self, TimeRange* other)
    {
        return reinterpret_cast<opentime::TimeRange*>(self)->overlaps(
            *reinterpret_cast<opentime::TimeRange*>(other));
    }
    _Bool TimeRange_equal(TimeRange* lhs, TimeRange* rhs)
    {
        return *reinterpret_cast<opentime::TimeRange*>(lhs) ==
               *reinterpret_cast<opentime::TimeRange*>(rhs);
    }
    _Bool TimeRange_not_equal(TimeRange* lhs, TimeRange* rhs)
    {
        return *reinterpret_cast<opentime::TimeRange*>(lhs) !=
               *reinterpret_cast<opentime::TimeRange*>(rhs);
    }
    TimeRange* TimeRange_range_from_start_end_time(
        RationalTime* start_time, RationalTime* end_time_exclusive)
    {
        opentime::TimeRange obj =
            opentime::TimeRange::range_from_start_end_time(
                *reinterpret_cast<opentime::RationalTime*>(start_time),
                *reinterpret_cast<opentime::RationalTime*>(end_time_exclusive));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(obj));
    }
    void TimeRange_destroy(TimeRange* self)
    {
        delete reinterpret_cast<opentime::TimeRange*>(self);
    }
#ifdef __cplusplus
}
#endif
