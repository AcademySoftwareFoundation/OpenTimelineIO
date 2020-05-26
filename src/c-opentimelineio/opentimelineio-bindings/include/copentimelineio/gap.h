#pragma once

#include "anyDictionary.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "effectVector.h"
#include "markerVector.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Gap;
    typedef struct Gap Gap;

    Gap* Gap_create_with_source_range(
        TimeRange*     source_range,
        const char*    name,
        EffectVector*  effects,
        MarkerVector*  markers,
        AnyDictionary* metadata);
    Gap* Gap_create_with_duration(
        RationalTime*  duration,
        const char*    name,
        EffectVector*  effects,
        MarkerVector*  markers,
        AnyDictionary* metadata);
    _Bool Gap_visible(Gap* self);
#ifdef __cplusplus
}
#endif
