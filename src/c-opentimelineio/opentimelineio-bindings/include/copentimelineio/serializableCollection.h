#pragma once

#include "anyDictionary.h"
#include "errorStatus.h"
#include "serializableObjectRetainerVector.h"
#include "serializableObjectVector.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct SerializableCollection;
    typedef struct SerializableCollection SerializableCollection;
    SerializableCollection*               SerializableCollection_create(
                      const char*               name,
                      SerializableObjectVector* children,
                      AnyDictionary*            metadata);
    SerializableObjectRetainerVector*
         SerializableCollection_children(SerializableCollection* self);
    void SerializableCollection_set_children(
        SerializableCollection* self, SerializableObjectVector* children);
    void SerializableCollection_clear_children(SerializableCollection* self);
    void SerializableCollection_insert_child(
        SerializableCollection* self, int index, SerializableObject* child);
    _Bool SerializableCollection_set_child(
        SerializableCollection* self,
        int                     index,
        SerializableObject*     child,
        OTIOErrorStatus*        error_status);
    _Bool SerializableCollection_remove_child(
        SerializableCollection* self, int index, OTIOErrorStatus* error_status);
    const char* SerializableCollection_name(SerializableCollection* self);
    void        SerializableCollection_set_name(
               SerializableCollection* self, const char* name);
    AnyDictionary*
          SerializableCollection_metadata(SerializableCollection* self);
    _Bool SerializableCollection_possibly_delete(SerializableCollection* self);
    _Bool SerializableCollection_to_json_file(
        SerializableCollection* self,
        const char*             file_name,
        OTIOErrorStatus*        error_status,
        int                     indent);
    const char* SerializableCollection_to_json_string(
        SerializableCollection* self,
        OTIOErrorStatus*        error_status,
        int                     indent);
    _Bool SerializableCollection_is_equivalent_to(
        SerializableCollection* self, SerializableObject* other);
    SerializableCollection* SerializableCollection_clone(
        SerializableCollection* self, OTIOErrorStatus* error_status);
    const char*
        SerializableCollection_schema_name(SerializableCollection* self);
    int SerializableCollection_schema_version(SerializableCollection* self);
#ifdef __cplusplus
}
#endif
