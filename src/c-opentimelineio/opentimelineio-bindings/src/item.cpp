#include "copentimelineio/item.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/item.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/serializableObject.h>

typedef std::vector<OTIO_NS::Effect*>           EffectVectorDef;
typedef std::vector<OTIO_NS::Effect*>::iterator EffectVectorIteratorDef;
typedef std::vector<OTIO_NS::Marker*>           MarkerVectorDef;
typedef std::vector<OTIO_NS::Marker*>::iterator MarkerVectorIteratorDef;
typedef std::vector<OTIO_NS::Effect::Retainer<OTIO_NS::Effect>>
    EffectRetainerVectorDef;
typedef std::vector<OTIO_NS::Effect::Retainer<OTIO_NS::Effect>>::iterator
    EffectRetainerVectorIteratorDef;
typedef std::vector<OTIO_NS::Marker::Retainer<OTIO_NS::Marker>>
    MarkerRetainerVectorDef;
typedef std::vector<OTIO_NS::Marker::Retainer<OTIO_NS::Marker>>::iterator
    MarkerRetainerVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    Item* Item_create(
        const char*    name,
        TimeRange*     source_range,
        AnyDictionary* metadata,
        EffectVector*  effects,
        MarkerVector*  markers)
    {
        nonstd::optional<OTIO_NS::TimeRange> source_range_optional =
            nonstd::nullopt;
        if(source_range)
            source_range_optional = nonstd::optional<OTIO_NS::TimeRange>(
                *reinterpret_cast<OTIO_NS::TimeRange*>(source_range));
        return reinterpret_cast<Item*>(new OTIO_NS::Item(
            name,
            source_range_optional,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata),
            *reinterpret_cast<EffectVectorDef*>(effects),
            *reinterpret_cast<MarkerVectorDef*>(markers)));
    }
    _Bool Item_visible(Item* self)
    {
        reinterpret_cast<OTIO_NS::Item*>(self)->visible();
    }
    _Bool Item_overlapping(Item* self)
    {
        reinterpret_cast<OTIO_NS::Item*>(self)->overlapping();
    }
    TimeRange* Item_source_range(Item* self)
    {
        nonstd::optional<OTIO_NS::TimeRange> timeRangeOptional =
            reinterpret_cast<OTIO_NS::Item*>(self)->source_range();
        if(timeRangeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<TimeRange*>(
            new OTIO_NS::TimeRange(timeRangeOptional.value()));
    }
    void Item_set_source_range(Item* self, TimeRange* source_range)
    {
        nonstd::optional<OTIO_NS::TimeRange> timeRangeOptional;
        if(source_range == NULL)
            timeRangeOptional = nonstd::nullopt;
        else
        {
            timeRangeOptional = nonstd::optional<OTIO_NS::TimeRange>(
                *reinterpret_cast<OTIO_NS::TimeRange*>(source_range));
        }
        reinterpret_cast<OTIO_NS::Item*>(self)->set_source_range(
            timeRangeOptional);
    }
    EffectRetainerVector* Item_effects(Item* self)
    {
        EffectRetainerVectorDef effectRetainerVector =
            reinterpret_cast<OTIO_NS::Item*>(self)->effects();
        return reinterpret_cast<EffectRetainerVector*>(
            new EffectRetainerVectorDef(effectRetainerVector));
    }
    MarkerRetainerVector* Item_markers(Item* self)
    {
        MarkerRetainerVectorDef markerRetainerVector =
            reinterpret_cast<OTIO_NS::Item*>(self)->markers();
        return reinterpret_cast<MarkerRetainerVector*>(
            new MarkerRetainerVectorDef(markerRetainerVector));
    }
    RationalTime* Item_duration(Item* self, OTIOErrorStatus* error_status)
    {
        OTIO_NS::RationalTime rationalTime =
            reinterpret_cast<OTIO_NS::Item*>(self)->duration(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(
            new OTIO_NS::RationalTime(rationalTime));
    }
    TimeRange* Item_available_range(Item* self, OTIOErrorStatus* error_status)
    {
        OTIO_NS::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Item*>(self)->available_range(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new OTIO_NS::TimeRange(timeRange));
    }
    TimeRange* Item_trimmed_range(Item* self, OTIOErrorStatus* error_status)
    {
        OTIO_NS::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Item*>(self)->trimmed_range(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new OTIO_NS::TimeRange(timeRange));
    }
    TimeRange* Item_visible_range(Item* self, OTIOErrorStatus* error_status)
    {
        OTIO_NS::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Item*>(self)->visible_range(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new OTIO_NS::TimeRange(timeRange));
    }
    TimeRange*
    Item_trimmed_range_in_parent(Item* self, OTIOErrorStatus* error_status)
    {
        nonstd::optional<OTIO_NS::TimeRange> timeRangeOptional =
            reinterpret_cast<OTIO_NS::Item*>(self)->trimmed_range_in_parent(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        if(timeRangeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<TimeRange*>(
            new OTIO_NS::TimeRange(timeRangeOptional.value()));
    }
    TimeRange* Item_range_in_parent(Item* self, OTIOErrorStatus* error_status)
    {
        OTIO_NS::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Item*>(self)->range_in_parent(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new OTIO_NS::TimeRange(timeRange));
    }
    RationalTime* Item_transformed_time(
        Item*            self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status)
    {
        OTIO_NS::RationalTime rationalTime =
            reinterpret_cast<OTIO_NS::Item*>(self)->transformed_time(
                *reinterpret_cast<OTIO_NS::RationalTime*>(time),
                reinterpret_cast<OTIO_NS::Item*>(to_item),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(
            new OTIO_NS::RationalTime(rationalTime));
    }
    TimeRange* Item_transformed_time_range(
        Item*            self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status)
    {
        OTIO_NS::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Item*>(self)->transformed_time_range(
                *reinterpret_cast<OTIO_NS::TimeRange*>(time_range),
                reinterpret_cast<OTIO_NS::Item*>(to_item),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new OTIO_NS::TimeRange(timeRange));
    }
#ifdef __cplusplus
}
#endif