#include "copentimelineio/stack.h"
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/stack.h>

typedef std::vector<OTIO_NS::Effect*>           EffectVectorDef;
typedef std::vector<OTIO_NS::Effect*>::iterator EffectVectorIteratorDef;
typedef std::vector<OTIO_NS::Marker*>           MarkerVectorDef;
typedef std::vector<OTIO_NS::Marker*>::iterator MarkerVectorIteratorDef;

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
        return reinterpret_cast<Stack*>(new OTIO_NS::Stack(
            name,
            timeRangeOptional,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata),
            *reinterpret_cast<EffectVectorDef*>(effects),
            *reinterpret_cast<MarkerVectorDef*>(markers)));
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
    /*map* Stack_range_of_all_children(Stack* self, ErrorStatus* error_status)
    {
        return reinterpret_cast<map*>(
            reinterpret_cast<OTIO_NS::Stack*>(self)->range_of_all_children(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status)));
    }*/
#ifdef __cplusplus
}
#endif
