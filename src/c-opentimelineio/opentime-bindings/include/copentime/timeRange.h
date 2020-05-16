#pragma once
#include "rationalTime.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct TimeRange;
    typedef struct TimeRange TimeRange;
    TimeRange*               TimeRange_create();
    TimeRange* TimeRange_create_with_start_time(RationalTime* start_time);
    TimeRange* TimeRange_create_with_start_time_and_duration(
        RationalTime* start_time, RationalTime* duration);
    RationalTime* TimeRange_start_time(TimeRange* self);
    RationalTime* TimeRange_duration(TimeRange* self);
    RationalTime* TimeRange_end_time_inclusive(TimeRange* self);
    RationalTime* TimeRange_end_time_exclusive(TimeRange* self);
    TimeRange*
               TimeRange_duration_extended_by(TimeRange* self, RationalTime* other);
    TimeRange* TimeRange_extended_by(TimeRange* self, TimeRange* other);
    RationalTime*
    TimeRange_clamped_with_rational_time(TimeRange* self, RationalTime* other);
    TimeRange*
    TimeRange_clamped_with_time_range(TimeRange* self, TimeRange* other);
    _Bool
          TimeRange_contains_rational_time(TimeRange* self, RationalTime* other);
    _Bool TimeRange_contains_time_range(TimeRange* self, TimeRange* other);
    _Bool
               TimeRange_overlaps_rational_time(TimeRange* self, RationalTime* other);
    _Bool      TimeRange_overlaps_time_range(TimeRange* self, TimeRange* other);
    _Bool      TimeRange_equal(TimeRange* lhs, TimeRange* rhs);
    _Bool      TimeRange_not_equal(TimeRange* lhs, TimeRange* rhs);
    TimeRange* TimeRange_range_from_start_end_time(
        RationalTime* start_time, RationalTime* end_time_exclusive);
    void TimeRange_destroy(TimeRange* self);
#ifdef __cplusplus
}
#endif
