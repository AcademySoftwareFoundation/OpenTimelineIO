#pragma once

#include "anyDictionary.h"
#include "composition.h"
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
    const char*    Transition_name(Transition* self);
    AnyDictionary* Transition_metadata(Transition* self);
    Composition*   Transition_parent(Transition* self);
    _Bool          Transition_visible(Transition* self);
    void           Transition_set_name(Transition* self, const char* name);
    _Bool          Transition_possibly_delete(Transition* self);
    _Bool          Transition_to_json_file(
                 Transition*      self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Transition_to_json_string(
        Transition* self, OTIOErrorStatus* error_status, int indent);
    _Bool
    Transition_is_equivalent_to(Transition* self, SerializableObject* other);
    Transition*
                Transition_clone(Transition* self, OTIOErrorStatus* error_status);
    const char* Transition_schema_name(Transition* self);
    int         Transition_schema_version(Transition* self);
#ifdef __cplusplus
}
#endif
