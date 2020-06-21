#include "copentimelineio/mediaReference.h"
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/mediaReference.h>

#ifdef __cplusplus
extern "C"
{
#endif
    MediaReference* MediaReference_create(
        const char* name, TimeRange* available_range, AnyDictionary* metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(available_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(available_range));
        }

        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<MediaReference*>(new OTIO_NS::MediaReference(
            name_str, timeRangeOptional, metadataDictionary));
    }
    TimeRange* MediaReference_available_range(MediaReference* self)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            reinterpret_cast<OTIO_NS::MediaReference*>(self)->available_range();
        if(timeRangeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<TimeRange*>(
            new opentime::TimeRange(timeRangeOptional.value()));
    }
    void MediaReference_set_available_range(
        MediaReference* self, TimeRange* available_range)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(available_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(available_range));
        }
        reinterpret_cast<OTIO_NS::MediaReference*>(self)->set_available_range(
            timeRangeOptional);
    }
    _Bool MediaReference_is_missing_reference(MediaReference* self)
    {
        return reinterpret_cast<OTIO_NS::MediaReference*>(self)
            ->is_missing_reference();
    }
    const char* MediaReference_name(MediaReference* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void MediaReference_set_name(MediaReference* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* MediaReference_metadata(MediaReference* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool MediaReference_possibly_delete(MediaReference* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool MediaReference_to_json_file(
        MediaReference*  self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* MediaReference_to_json_string(
        MediaReference* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool MediaReference_is_equivalent_to(
        MediaReference* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    MediaReference*
    MediaReference_clone(MediaReference* self, OTIOErrorStatus* error_status)
    {
        return (MediaReference*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* MediaReference_schema_name(MediaReference* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int MediaReference_schema_version(MediaReference* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
