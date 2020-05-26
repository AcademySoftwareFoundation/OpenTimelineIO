#pragma once
#include "rationalTime.h"
#include "timeRange.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct TimeTransform;
    typedef struct TimeTransform TimeTransform;
    TimeTransform* TimeTransform_create();
    TimeTransform*
                  TimeTransform_create_with_offset_scale_rate(RationalTime* offset, double scale, double rate);
    RationalTime* TimeTransform_offset(TimeTransform* self);
    double        TimeTransform_scale(TimeTransform* self);
    double        TimeTransform_rate(TimeTransform* self);
    TimeRange* TimeTransform_applied_to_time_range(TimeTransform* self, TimeRange* other);
    TimeTransform*
    TimeTransform_applied_to_time_transform(TimeTransform* self, TimeTransform* other);
    RationalTime*
          TimeTransform_applied_to_rational_time(TimeTransform* self, RationalTime* other);
    _Bool TimeTransform_equal(TimeTransform* lhs, TimeTransform* rhs);
    _Bool TimeTransform_not_equal(TimeTransform* lhs, TimeTransform* rhs);
    void  TimeTransform_destroy(TimeTransform* self);
#ifdef __cplusplus
}
#endif
