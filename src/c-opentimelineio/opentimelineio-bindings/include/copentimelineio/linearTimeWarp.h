#pragma once

#include "anyDictionary.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct LinearTimeWarp;
    typedef struct LinearTimeWarp LinearTimeWarp;

    LinearTimeWarp* LinearTimeWarp_create(
        const char*    name,
        const char*    effect_name,
        double         time_scalar,
        AnyDictionary* metadata);
    double LinearTimeWarp_time_scalar(LinearTimeWarp* self);
    void
    LinearTimeWarp_set_time_scalar(LinearTimeWarp* self, double time_scalar);
#ifdef __cplusplus
}
#endif
