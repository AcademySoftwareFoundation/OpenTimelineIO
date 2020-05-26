#pragma once

#include "anyDictionary.h"

#ifdef __cplusplus
extern "C"
{
#endif
    struct SerializableObjectWithMetadata;
    typedef struct SerializableObjectWithMetadata
                                    SerializableObjectWithMetadata;
    SerializableObjectWithMetadata* SerializableObjectWithMetadata_create(
        const char* name, AnyDictionary* metadata);
    const char*
         SerializableObjectWithMetadata_name(SerializableObjectWithMetadata* self);
    void SerializableObjectWithMetadata_set_name(
        SerializableObjectWithMetadata* self, const char* name);
    AnyDictionary* SerializableObjectWithMetadata_metadata(
        SerializableObjectWithMetadata* self);
#ifdef __cplusplus
}
#endif
