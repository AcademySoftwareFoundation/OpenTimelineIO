#pragma once

#include "anyDictionary.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    extern const char* TransitionType_SMPTE_Dissolve;
    extern const char* TransitionType_Custom;

    struct Transition;
    typedef struct Transition Transition;

    Transition* Transition_create(
        const char*    name,
        const char*    transition_type,
        RationalTime*  in_offset,
        RationalTime*  out_offset,
        AnyDictionary* metadata);
    _Bool       Transition_overlapping(Transition* self);
    const char* Transition_transition_type(Transition* self);
    void        Transition_set_transition_type(
               Transition* self, const char* transition_type);
    RationalTime* Transition_in_offset(Transition* self);
    void Transition_set_in_offset(Transition* self, RationalTime* in_offset);
    RationalTime* Transition_out_offset(Transition* self);
    void Transition_set_out_offset(Transition* self, RationalTime* out_offset);
    RationalTime*
    Transition_duration(Transition* self, OTIOErrorStatus* error_status);
    TimeRange*
               Transition_range_in_parent(Transition* self, OTIOErrorStatus* error_status);
    TimeRange* Transition_trimmed_range_in_parent(
        Transition* self, OTIOErrorStatus* error_status);
#ifdef __cplusplus
}
#endif
