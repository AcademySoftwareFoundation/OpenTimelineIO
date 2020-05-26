#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct MediaReference;
    typedef struct MediaReference MediaReference;

    MediaReference* MediaReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata);
    TimeRange* MediaReference_available_range(MediaReference* self);
    void       MediaReference_set_available_range(
              MediaReference* self, TimeRange* available_range);
    _Bool MediaReference_is_missing_reference(MediaReference* self);
#ifdef __cplusplus
}
#endif
