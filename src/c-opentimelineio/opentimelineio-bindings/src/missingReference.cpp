#include "copentimelineio/missingReference.h"
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/missingReference.h>

#ifdef __cplusplus
extern "C"
{
#endif
    MissingReference* MissingReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(available_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(available_range));
        }
        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        std::string name_str = std::string();
        if(name != NULL) name_str = name;
        return reinterpret_cast<MissingReference*>(
            new OTIO_NS::MissingReference(
                name_str, timeRangeOptional, metadataDictionary));
    }
    _Bool MissingReference_is_missing_reference(MissingReference* self)
    {
        return reinterpret_cast<OTIO_NS::MissingReference*>(self)
            ->is_missing_reference();
    }
    TimeRange* MissingReference_available_range(MissingReference* self)
    {
        return MediaReference_available_range((MediaReference*) self);
    }
    void MissingReference_set_available_range(
        MissingReference* self, TimeRange* available_range)
    {
        MediaReference_set_available_range(
            (MediaReference*) self, available_range);
    }
    const char* MissingReference_name(MissingReference* self)
    {
        return MediaReference_name((MediaReference*) self);
    }
    void MissingReference_set_name(MissingReference* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* MissingReference_metadata(MissingReference* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool MissingReference_possibly_delete(MissingReference* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool MissingReference_to_json_file(
        MissingReference* self,
        const char*       file_name,
        OTIOErrorStatus*  error_status,
        int               indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* MissingReference_to_json_string(
        MissingReference* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool MissingReference_is_equivalent_to(
        MissingReference* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    MissingReference* MissingReference_clone(
        MissingReference* self, OTIOErrorStatus* error_status)
    {
        return (MissingReference*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* MissingReference_schema_name(MissingReference* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int MissingReference_schema_version(MissingReference* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
