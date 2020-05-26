#include "copentimelineio/serializableObject.h"
#include <opentimelineio/serializableObject.h>
#include <string.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>
    SerializableObjectRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    RetainerSerializableObject*
    RetainerSerializableObject_create(SerializableObject* obj)
    {
        return reinterpret_cast<RetainerSerializableObject*>(
            new SerializableObjectRetainer(
                reinterpret_cast<OTIO_NS::SerializableObject*>(obj)));
    }
    SerializableObject*
    RetainerSerializableObject_take_value(RetainerSerializableObject* self)
    {
        return reinterpret_cast<SerializableObject*>(
            reinterpret_cast<SerializableObjectRetainer*>(self)->take_value());
    }
    void
    RetainerSerializableObject_managed_destroy(RetainerSerializableObject* self)
    {
        delete reinterpret_cast<SerializableObjectRetainer*>(self);
    }
    SerializableObject* SerializableObject_create()
    {
        return reinterpret_cast<SerializableObject*>(
            new OTIO_NS::SerializableObject());
    }
    _Bool SerializableObject_possibly_delete(SerializableObject* self)
    {
        return reinterpret_cast<OTIO_NS::SerializableObject*>(self)
            ->possibly_delete();
    }
    _Bool SerializableObject_to_json_file(
        SerializableObject* self,
        const char*         file_name,
        OTIOErrorStatus*    error_status,
        int                 indent)
    {
        return reinterpret_cast<OTIO_NS::SerializableObject*>(self)
            ->to_json_file(
                file_name,
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status),
                indent);
    }
    const char* SerializableObject_to_json_string(
        SerializableObject* self, OTIOErrorStatus* error_status, int indent)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::SerializableObject*>(self)
                ->to_json_string(
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status),
                    indent);
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    SerializableObject* SerializableObject_from_json_file(
        const char* file_name, OTIOErrorStatus* error_status)
    {
        OTIO_NS::SerializableObject* obj =
            OTIO_NS::SerializableObject::from_json_file(
                file_name,
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<SerializableObject*>(obj);
    }
    SerializableObject* SerializableObject_from_json_string(
        const char* input, OTIOErrorStatus* error_status)
    {
        OTIO_NS::SerializableObject* obj =
            OTIO_NS::SerializableObject::from_json_string(
                input, reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<SerializableObject*>(obj);
    }
    _Bool SerializableObject_is_equivalent_to(
        SerializableObject* self, SerializableObject* other)
    {
        return reinterpret_cast<OTIO_NS::SerializableObject*>(self)
            ->is_equivalent_to(
                *reinterpret_cast<OTIO_NS::SerializableObject*>(other));
    }
    SerializableObject* SerializableObject_clone(
        SerializableObject* self, OTIOErrorStatus* error_status)
    {
        OTIO_NS::SerializableObject* obj =
            reinterpret_cast<OTIO_NS::SerializableObject*>(self)->clone(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<SerializableObject*>(obj);
    }
    /*AnyDictionary* SerializableObject_dynamic_fields(SerializableObject* self)
    {
        return reinterpret_cast<AnyDictionary*>(
            reinterpret_cast<OTIO_NS::SerializableObject*>(self)
                ->dynamic_fields());
    }*/
    _Bool SerializableObject_is_unknown_schema(SerializableObject* self)
    {
        return reinterpret_cast<OTIO_NS::SerializableObject*>(self)
            ->is_unknown_schema();
    }
    const char* SerializableObject_schema_name(SerializableObject* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::SerializableObject*>(self)->schema_name();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    int SerializableObject_schema_version(SerializableObject* self)
    {
        return reinterpret_cast<OTIO_NS::SerializableObject*>(self)
            ->schema_version();
    }
#ifdef __cplusplus
}
#endif
