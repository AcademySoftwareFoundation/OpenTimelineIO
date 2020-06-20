#include "copentimelineio/externalReference.h"
#include <copentimelineio/errorStatus.h>
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/externalReference.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    ExternalReference* ExternalReference_create(
        const char*    target_url,
        TimeRange*     available_range,
        AnyDictionary* metadata)
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

        std::string target_url_str = std::string();
        if(target_url != NULL) target_url_str = target_url;
        return reinterpret_cast<ExternalReference*>(
            new OTIO_NS::ExternalReference(
                target_url_str, timeRangeOptional, metadataDictionary));
    }
    const char* ExternalReference_target_url(ExternalReference* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::ExternalReference*>(self)->target_url();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void ExternalReference_set_target_url(
        ExternalReference* self, const char* target_url)
    {
        reinterpret_cast<OTIO_NS::ExternalReference*>(self)->set_target_url(
            target_url);
    }
    TimeRange* ExternalReference_available_range(ExternalReference* self)
    {
        return MediaReference_available_range((MediaReference*) self);
    }
    void ExternalReference_set_available_range(
        ExternalReference* self, TimeRange* available_range)
    {
        MediaReference_set_available_range(
            (MediaReference*) self, available_range);
    }
    _Bool ExternalReference_is_missing_reference(ExternalReference* self)
    {
        return MediaReference_is_missing_reference((MediaReference*) self);
    }
    const char* ExternalReference_name(ExternalReference* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void ExternalReference_set_name(ExternalReference* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* ExternalReference_metadata(ExternalReference* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool ExternalReference_possibly_delete(ExternalReference* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool ExternalReference_to_json_file(
        ExternalReference* self,
        const char*        file_name,
        OTIOErrorStatus*   error_status,
        int                indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* ExternalReference_to_json_string(
        ExternalReference* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool ExternalReference_is_equivalent_to(
        ExternalReference* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    ExternalReference* ExternalReference_clone(
        ExternalReference* self, OTIOErrorStatus* error_status)
    {
        return (ExternalReference*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* ExternalReference_schema_name(ExternalReference* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int ExternalReference_schema_version(ExternalReference* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
