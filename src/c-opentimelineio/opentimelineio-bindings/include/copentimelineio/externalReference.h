#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct ExternalReference;
    typedef struct ExternalReference ExternalReference;
    ExternalReference*               ExternalReference_create(
                      const char*    target_url,
                      TimeRange*     available_range,
                      AnyDictionary* metadata);
    const char* ExternalReference_target_url(ExternalReference* self);
    void        ExternalReference_set_target_url(
               ExternalReference* self, const char* target_url);
    TimeRange* ExternalReference_available_range(ExternalReference* self);
    void       ExternalReference_set_available_range(
              ExternalReference* self, TimeRange* available_range);
    _Bool       ExternalReference_is_missing_reference(ExternalReference* self);
    const char* ExternalReference_name(ExternalReference* self);
    void ExternalReference_set_name(ExternalReference* self, const char* name);
    AnyDictionary* ExternalReference_metadata(ExternalReference* self);
    _Bool          ExternalReference_possibly_delete(ExternalReference* self);
    _Bool          ExternalReference_to_json_file(
                 ExternalReference* self,
                 const char*        file_name,
                 OTIOErrorStatus*   error_status,
                 int                indent);
    const char* ExternalReference_to_json_string(
        ExternalReference* self, OTIOErrorStatus* error_status, int indent);
    _Bool ExternalReference_is_equivalent_to(
        ExternalReference* self, SerializableObject* other);
    ExternalReference* ExternalReference_clone(
        ExternalReference* self, OTIOErrorStatus* error_status);
    const char* ExternalReference_schema_name(ExternalReference* self);
    int         ExternalReference_schema_version(ExternalReference* self);
#ifdef __cplusplus
}
#endif
