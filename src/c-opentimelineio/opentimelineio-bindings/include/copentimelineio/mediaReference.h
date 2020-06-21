#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct MediaReference;
    typedef struct MediaReference MediaReference;

    MediaReference* MediaReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata);
    TimeRange* MediaReference_available_range(MediaReference* self);
    void       MediaReference_set_available_range(
              MediaReference* self, TimeRange* available_range);
    _Bool       MediaReference_is_missing_reference(MediaReference* self);
    const char* MediaReference_name(MediaReference* self);
    void        MediaReference_set_name(MediaReference* self, const char* name);
    AnyDictionary* MediaReference_metadata(MediaReference* self);
    _Bool          MediaReference_possibly_delete(MediaReference* self);
    _Bool          MediaReference_to_json_file(
                 MediaReference*  self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* MediaReference_to_json_string(
        MediaReference* self, OTIOErrorStatus* error_status, int indent);
    _Bool MediaReference_is_equivalent_to(
        MediaReference* self, SerializableObject* other);
    MediaReference*
                MediaReference_clone(MediaReference* self, OTIOErrorStatus* error_status);
    const char* MediaReference_schema_name(MediaReference* self);
    int         MediaReference_schema_version(MediaReference* self);
#ifdef __cplusplus
}
#endif
