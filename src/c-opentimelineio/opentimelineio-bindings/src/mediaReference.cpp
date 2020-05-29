#include "copentimelineio/mediaReference.h"
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
#ifdef __cplusplus
}
#endif
