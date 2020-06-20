#include "copentimelineio/clip.h"
#include <copentimelineio/composable.h>
#include <copentimelineio/item.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/mediaReference.h>

#ifdef __cplusplus
extern "C"
{
#endif
    Clip* Clip_create(
        const char*     name,
        MediaReference* media_reference,
        TimeRange*      source_range,
        AnyDictionary*  metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(source_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(source_range));
        }

        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);
        return reinterpret_cast<Clip*>(new OTIO_NS::Clip(
            name_str,
            reinterpret_cast<OTIO_NS::MediaReference*>(media_reference),
            timeRangeOptional,
            metadataDictionary));
    }
    void Clip_set_media_reference(Clip* self, MediaReference* media_reference)
    {
        reinterpret_cast<OTIO_NS::Clip*>(self)->set_media_reference(
            reinterpret_cast<OTIO_NS::MediaReference*>(media_reference));
    }
    MediaReference* Clip_media_reference(Clip* self)
    {
        return reinterpret_cast<MediaReference*>(
            reinterpret_cast<OTIO_NS::Clip*>(self)->media_reference());
    }
    TimeRange* Clip_available_range(Clip* self, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Clip*>(self)->available_range(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Clip_source_range(Clip* self)
    {
        return Item_source_range((Item*) self);
    }
    void Clip_set_source_range(Clip* self, TimeRange* source_range)
    {
        Item_set_source_range((Item*) self, source_range);
    }
    EffectRetainerVector* Clip_effects(Clip* self)
    {
        return Item_effects((Item*) self);
    }
    MarkerRetainerVector* Clip_markers(Clip* self)
    {
        return Item_markers((Item*) self);
    }
    RationalTime* Clip_duration(Clip* self, OTIOErrorStatus* error_status)
    {
        return Item_duration((Item*) self, error_status);
    }
    TimeRange* Clip_trimmed_range(Clip* self, OTIOErrorStatus* error_status)
    {
        return Item_trimmed_range((Item*) self, error_status);
    }
    TimeRange* Clip_visible_range(Clip* self, OTIOErrorStatus* error_status)
    {
        return Item_visible_range((Item*) self, error_status);
    }
    TimeRange*
    Clip_trimmed_range_in_parent(Clip* self, OTIOErrorStatus* error_status)
    {
        return Item_trimmed_range_in_parent((Item*) self, error_status);
    }
    TimeRange* Clip_range_in_parent(Clip* self, OTIOErrorStatus* error_status)
    {
        return Item_range_in_parent((Item*) self, error_status);
    }
    RationalTime* Clip_transformed_time(
        Clip*            self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status)
    {
        return Item_transformed_time((Item*) self, time, to_item, error_status);
    }
    TimeRange* Clip_transformed_time_range(
        Clip*            self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status)
    {
        return Item_transformed_time_range(
            (Item*) self, time_range, to_item, error_status);
    }
    _Bool Clip_visible(Clip* self) { return Item_visible((Item*) self); }
    _Bool Clip_overlapping(Clip* self)
    {
        return Item_overlapping((Item*) self);
    }
    Composition* Clip_parent(Clip* self)
    {
        return Composable_parent((Composable*) self);
    }
    const char* Clip_name(Clip* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    AnyDictionary* Clip_metadata(Clip* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    void Clip_set_name(Clip* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    _Bool Clip_possibly_delete(Clip* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool Clip_to_json_file(
        Clip*            self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char*
    Clip_to_json_string(Clip* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool Clip_is_equivalent_to(Clip* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, (SerializableObject*) other);
    }
    Clip* Clip_clone(Clip* self, OTIOErrorStatus* error_status)
    {
        return (Clip*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* Clip_schema_name(Clip* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int Clip_schema_version(Clip* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
