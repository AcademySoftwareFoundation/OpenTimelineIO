#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include "effectVector.h"
#include "errorStatus.h"
#include "mapComposableTimeRange.h"
#include "markerVector.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Stack;
    typedef struct Stack Stack;

    Stack* Stack_create(
        const char*    name,
        TimeRange*     source_range,
        AnyDictionary* metadata,
        EffectVector*  effects,
        MarkerVector*  markers);
    TimeRange* Stack_range_of_child_at_index(
        Stack* self, int index, OTIOErrorStatus* error_status);
    TimeRange* Stack_trimmed_range_of_child_at_index(
        Stack* self, int index, OTIOErrorStatus* error_status);
    TimeRange*
    Stack_available_range(Stack* self, OTIOErrorStatus* error_status);
    MapComposableTimeRange*
    Stack_range_of_all_children(Stack* self, OTIOErrorStatus* error_status);
#ifdef __cplusplus
}
#endif
