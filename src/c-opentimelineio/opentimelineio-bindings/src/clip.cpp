#include "copentimelineio/clip.h"
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
        return reinterpret_cast<Clip*>(new OTIO_NS::Clip(
            name,
            reinterpret_cast<OTIO_NS::MediaReference*>(media_reference),
            timeRangeOptional,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
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
#ifdef __cplusplus
}
#endif
