#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct MissingReference;
    typedef struct MissingReference MissingReference;

    MissingReference* MissingReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata);
    _Bool MissingReference_is_missing_reference(MissingReference* self);
#ifdef __cplusplus
}
#endif
