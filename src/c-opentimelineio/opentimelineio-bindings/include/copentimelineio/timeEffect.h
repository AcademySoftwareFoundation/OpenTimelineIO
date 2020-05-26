#pragma once

#include "copentimelineio/anyDictionary.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct TimeEffect;
    typedef struct TimeEffect TimeEffect;

    TimeEffect* TimeEffect_create(
        const char* name, const char* effect_name, AnyDictionary* metadata);
#ifdef __cplusplus
}
#endif
