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

        return reinterpret_cast<Item*>(new OTIO_NS::Item(
            name_str,
            source_range_optional,
            metadataDictionary,
            effectsVector,
            markersVector));
    }
    _Bool Item_visible(Item* self)
    {
        return reinterpret_cast<OTIO_NS::Item*>(self)->visible();
    }
    _Bool Item_overlapping(Item* self)
    {
        return reinterpret_cast<OTIO_NS::Item*>(self)->overlapping();
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
    Composition* Item_parent(Item* self)
    {
        return Composable_parent((Composable*) self);
    }
    const char* Item_name(Item* self)
    {
        return Composable_name((Composable*) self);
    }
    AnyDictionary* Item_metadata(Item* self)
    {
        return Composable_metadata((Composable*) self);
    }
    void Item_set_name(Item* self, const char* name)
    {
        return Composable_set_name((Composable*) self, name);
    }
    _Bool Item_possibly_delete(Item* self)
    {
        return Composable_possibly_delete((Composable*) self);
    }
    _Bool Item_to_json_file(
        Item*            self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return Composable_to_json_file(
            (Composable*) self, file_name, error_status, indent);
    }
    const char*
    Item_to_json_string(Item* self, OTIOErrorStatus* error_status, int indent)
    {
        return Composable_to_json_string(
            (Composable*) self, error_status, indent);
    }
    _Bool Item_is_equivalent_to(Item* self, SerializableObject* other)
    {
        return Composable_is_equivalent_to((Composable*) self, other);
    }
    Item* Item_clone(Item* self, OTIOErrorStatus* error_status)
    {
        return (Item*) Composable_clone((Composable*) self, error_status);
    }
    const char* Item_schema_name(Item* self)
    {
        return Composable_schema_name((Composable*) self);
    }
    int Item_schema_version(Item* self)
    {
        return Composable_schema_version((Composable*) self);
    }
#ifdef __cplusplus
}
#endif