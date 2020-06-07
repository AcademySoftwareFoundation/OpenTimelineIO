#include "copentimelineio/stack.h"
#include <map>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/stack.h>

typedef std::vector<OTIO_NS::Effect*>           EffectVectorDef;
typedef std::vector<OTIO_NS::Effect*>::iterator EffectVectorIteratorDef;
typedef std::vector<OTIO_NS::Marker*>           MarkerVectorDef;
typedef std::vector<OTIO_NS::Marker*>::iterator MarkerVectorIteratorDef;
typedef std::map<OTIO_NS::Composable*, opentime::TimeRange> MapDef;
typedef std::map<OTIO_NS::Composable*, opentime::TimeRange>::iterator
    MapIterator;

#ifdef __cplusplus
extern "C"
{
#endif
    Stack* Stack_create(
        const char*    name,
        TimeRange*     source_range,
        AnyDictionary* metadata,
        EffectVector*  effects,
        MarkerVector*  markers)
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
        {
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);
        }

        EffectVectorDef effectsVector = EffectVectorDef();
        if(effects != NULL)
        { effectsVector = *reinterpret_cast<EffectVectorDef*>(effects); }

        MarkerVectorDef markersVector = MarkerVectorDef();
        if(markers != NULL)
        { markersVector = *reinterpret_cast<MarkerVectorDef*>(markers); }

        return reinterpret_cast<Stack*>(new OTIO_NS::Stack(
            name_str,
            timeRangeOptional,
            metadataDictionary,
            effectsVector,
            markersVector));
    }
    TimeRange* Stack_range_of_child_at_index(
        Stack* self, int index, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Stack*>(self)->range_of_child_at_index(
                index, reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Stack_trimmed_range_of_child_at_index(
        Stack* self, int index, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Stack*>(self)
                ->trimmed_range_of_child_at_index(
                    index,
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Stack_available_range(Stack* self, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Stack*>(self)->available_range(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    MapComposableTimeRange*
    Stack_range_of_all_children(Stack* self, OTIOErrorStatus* error_status)
    {
        MapDef mapDef =
            reinterpret_cast<OTIO_NS::Stack*>(self)->range_of_all_children(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<MapComposableTimeRange*>(new MapDef(mapDef));
    }
#ifdef __cplusplus
}
#endif
