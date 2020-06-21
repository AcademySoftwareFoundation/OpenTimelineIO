#pragma once

#include "anyDictionary.h"
#include "errorStatus.h"
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
    const char* LinearTimeWarp_effect_name(LinearTimeWarp* self);
    void        LinearTimeWarp_set_effect_name(
               LinearTimeWarp* self, const char* effect_name);
    const char* LinearTimeWarp_name(LinearTimeWarp* self);
    void        LinearTimeWarp_set_name(LinearTimeWarp* self, const char* name);
    AnyDictionary* LinearTimeWarp_metadata(LinearTimeWarp* self);
    _Bool          LinearTimeWarp_possibly_delete(LinearTimeWarp* self);
    _Bool          LinearTimeWarp_to_json_file(
                 LinearTimeWarp*  self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* LinearTimeWarp_to_json_string(
        LinearTimeWarp* self, OTIOErrorStatus* error_status, int indent);
    _Bool LinearTimeWarp_is_equivalent_to(
        LinearTimeWarp* self, SerializableObject* other);
    LinearTimeWarp*
                LinearTimeWarp_clone(LinearTimeWarp* self, OTIOErrorStatus* error_status);
    const char* LinearTimeWarp_schema_name(LinearTimeWarp* self);
    int         LinearTimeWarp_schema_version(LinearTimeWarp* self);
#ifdef __cplusplus
}
#endif
