#include "copentimelineio/timeline.h"
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/timeline.h>
#include <opentimelineio/track.h>
#include <vector>

typedef std::vector<OTIO_NS::Track*>           TrackVectorDef;
typedef std::vector<OTIO_NS::Track*>::iterator TrackVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    Timeline* Timeline_create(
        const char*    name,
        RationalTime*  global_start_time,
        AnyDictionary* metadata)
    {
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            nonstd::nullopt;
        if(global_start_time != NULL)
        {
            rationalTimeOptional = nonstd::optional<opentime::RationalTime>(
                *reinterpret_cast<opentime::RationalTime*>(global_start_time));
        }
        return reinterpret_cast<Timeline*>(new OTIO_NS::Timeline(
            name_str, rationalTimeOptional, metadataDictionary));
    }
    Stack* Timeline_tracks(Timeline* self)
    {
        return reinterpret_cast<Stack*>(
            reinterpret_cast<OTIO_NS::Timeline*>(self)->tracks());
    }
    void Timeline_set_tracks(Timeline* self, Stack* stack)
    {
        reinterpret_cast<OTIO_NS::Timeline*>(self)->set_tracks(
            reinterpret_cast<OTIO_NS::Stack*>(stack));
    }
    RationalTime* Timeline_global_start_time(Timeline* self)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->global_start_time();
        if(rationalTimeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTimeOptional.value()));
    }
    void Timeline_set_global_start_time(
        Timeline* self, RationalTime* global_start_time)
    {
        nonstd::optional<opentime::RationalTime> rationalTimeOptional =
            nonstd::nullopt;
        if(global_start_time != NULL)
        {
            rationalTimeOptional = nonstd::optional<opentime::RationalTime>(
                *reinterpret_cast<opentime::RationalTime*>(global_start_time));
        }
        reinterpret_cast<OTIO_NS::Timeline*>(self)->set_global_start_time(
            rationalTimeOptional);
    }
    RationalTime*
    Timeline_duration(Timeline* self, OTIOErrorStatus* error_status)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->duration(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    TimeRange* Timeline_range_of_child(
        Timeline* self, Composable* child, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->range_of_child(
                reinterpret_cast<OTIO_NS::Composable*>(child),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TrackVector* Timeline_audio_tracks(Timeline* self)
    {
        TrackVectorDef trackVector =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->audio_tracks();
        return reinterpret_cast<TrackVector*>(new TrackVectorDef(trackVector));
    }
    TrackVector* Timeline_video_tracks(Timeline* self)
    {
        TrackVectorDef trackVector =
            reinterpret_cast<OTIO_NS::Timeline*>(self)->video_tracks();
        return reinterpret_cast<TrackVector*>(new TrackVectorDef(trackVector));
    }

    const char* Timeline_name(Timeline* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void Timeline_set_name(Timeline* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* Timeline_metadata(Timeline* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool Timeline_possibly_delete(Timeline* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool Timeline_to_json_file(
        Timeline*        self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* Timeline_to_json_string(
        Timeline* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool Timeline_is_equivalent_to(Timeline* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    Timeline* Timeline_clone(Timeline* self, OTIOErrorStatus* error_status)
    {
        return (Timeline*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* Timeline_schema_name(Timeline* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int Timeline_schema_version(Timeline* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
