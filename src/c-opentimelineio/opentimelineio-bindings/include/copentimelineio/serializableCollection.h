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
#ifdef __cplusplus
}
#endif
