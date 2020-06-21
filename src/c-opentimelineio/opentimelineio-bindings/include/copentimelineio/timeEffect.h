#pragma once

#include "copentimelineio/anyDictionary.h"
#include "errorStatus.h"
#include "serializableObject.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct TimeEffect;
    typedef struct TimeEffect TimeEffect;

    TimeEffect* TimeEffect_create(
        const char* name, const char* effect_name, AnyDictionary* metadata);
    const char* TimeEffect_effect_name(TimeEffect* self);
    void TimeEffect_set_effect_name(TimeEffect* self, const char* effect_name);
    const char*    TimeEffect_name(TimeEffect* self);
    void           TimeEffect_set_name(TimeEffect* self, const char* name);
    AnyDictionary* TimeEffect_metadata(TimeEffect* self);
    _Bool          TimeEffect_possibly_delete(TimeEffect* self);
    _Bool          TimeEffect_to_json_file(
                 TimeEffect*      self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* TimeEffect_to_json_string(
        TimeEffect* self, OTIOErrorStatus* error_status, int indent);
    _Bool
    TimeEffect_is_equivalent_to(TimeEffect* self, SerializableObject* other);
    TimeEffect*
                TimeEffect_clone(TimeEffect* self, OTIOErrorStatus* error_status);
    const char* TimeEffect_schema_name(TimeEffect* self);
    int         TimeEffect_schema_version(TimeEffect* self);
#ifdef __cplusplus
}
#endif
