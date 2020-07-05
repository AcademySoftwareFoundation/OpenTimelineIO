#pragma once

#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct RetainerSerializableObject;
    typedef struct RetainerSerializableObject RetainerSerializableObject;
    struct SerializableObject;
    typedef struct SerializableObject SerializableObject;
    struct OTIOErrorStatus;
    typedef struct OTIOErrorStatus OTIOErrorStatus;

    RetainerSerializableObject*
    RetainerSerializableObject_create(SerializableObject* obj);
    SerializableObject*
    RetainerSerializableObject_take_value(RetainerSerializableObject* self);
    SerializableObject*
         RetainerSerializableObject_value(RetainerSerializableObject* self);
    void RetainerSerializableObject_managed_destroy(
        RetainerSerializableObject* self);
    SerializableObject* SerializableObject_create();
    _Bool SerializableObject_possibly_delete(SerializableObject* self);
    _Bool SerializableObject_to_json_file(
        SerializableObject* self,
        const char*         file_name,
        OTIOErrorStatus*    error_status,
        int                 indent);
    const char* SerializableObject_to_json_string(
        SerializableObject* self, OTIOErrorStatus* error_status, int indent);
    SerializableObject* SerializableObject_from_json_file(
        const char* file_name, OTIOErrorStatus* error_status);
    SerializableObject* SerializableObject_from_json_string(
        const char* input, OTIOErrorStatus* error_status);
    _Bool SerializableObject_is_equivalent_to(
        SerializableObject* self, SerializableObject* other);
    SerializableObject* SerializableObject_clone(
        SerializableObject* self, OTIOErrorStatus* error_status);
    /*AnyDictionary* SerializableObject_dynamic_fields(SerializableObject* self);*/
    _Bool       SerializableObject_is_unknown_schema(SerializableObject* self);
    const char* SerializableObject_schema_name(SerializableObject* self);
    int         SerializableObject_schema_version(SerializableObject* self);
#ifdef __cplusplus
}
#endif
