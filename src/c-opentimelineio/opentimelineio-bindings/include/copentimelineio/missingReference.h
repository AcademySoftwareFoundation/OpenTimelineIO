#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct MissingReference;
    typedef struct MissingReference MissingReference;

    MissingReference* MissingReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata);
    _Bool      MissingReference_is_missing_reference(MissingReference* self);
    TimeRange* MissingReference_available_range(MissingReference* self);
    void       MissingReference_set_available_range(
              MissingReference* self, TimeRange* available_range);
    const char* MissingReference_name(MissingReference* self);
    void MissingReference_set_name(MissingReference* self, const char* name);
    AnyDictionary* MissingReference_metadata(MissingReference* self);
    _Bool          MissingReference_possibly_delete(MissingReference* self);
    _Bool          MissingReference_to_json_file(
                 MissingReference* self,
                 const char*       file_name,
                 OTIOErrorStatus*  error_status,
                 int               indent);
    const char* MissingReference_to_json_string(
        MissingReference* self, OTIOErrorStatus* error_status, int indent);
    _Bool MissingReference_is_equivalent_to(
        MissingReference* self, SerializableObject* other);
    MissingReference* MissingReference_clone(
        MissingReference* self, OTIOErrorStatus* error_status);
    const char* MissingReference_schema_name(MissingReference* self);
    int         MissingReference_schema_version(MissingReference* self);
#ifdef __cplusplus
}
#endif
