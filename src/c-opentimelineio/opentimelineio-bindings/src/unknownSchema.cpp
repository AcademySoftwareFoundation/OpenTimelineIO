#include "copentimelineio/unknownSchema.h"
#include <copentimelineio/serializableObject.h>
#include <opentimelineio/unknownSchema.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    UnknownSchema* UnknownSchema_create(
        const char* original_schema_name, int original_schema_version)
    {
        return reinterpret_cast<UnknownSchema*>(new OTIO_NS::UnknownSchema(
            original_schema_name, original_schema_version));
    }
    const char* UnknownSchema_original_schema_name(UnknownSchema* self)
    {
        std::string returnStr = reinterpret_cast<OTIO_NS::UnknownSchema*>(self)
                                    ->original_schema_name();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    int UnknownSchema_original_schema_version(UnknownSchema* self)
    {
        return reinterpret_cast<OTIO_NS::UnknownSchema*>(self)
            ->original_schema_version();
    }
    _Bool UnknownSchema_is_unknown_schema(UnknownSchema* self)
    {
        return reinterpret_cast<OTIO_NS::UnknownSchema*>(self)
            ->is_unknown_schema();
    }
    _Bool UnknownSchema_possibly_delete(UnknownSchema* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool UnknownSchema_to_json_file(
        UnknownSchema*   self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* UnknownSchema_to_json_string(
        UnknownSchema* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool UnknownSchema_is_equivalent_to(
        UnknownSchema* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    UnknownSchema*
    UnknownSchema_clone(UnknownSchema* self, OTIOErrorStatus* error_status)
    {
        return (UnknownSchema*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* UnknownSchema_schema_name(UnknownSchema* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int UnknownSchema_schema_version(UnknownSchema* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
