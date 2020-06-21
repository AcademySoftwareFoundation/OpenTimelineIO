#include "copentimelineio/stack.h"
#include <copentimelineio/composition.h>
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
    const char* Stack_composition_kind(Stack* self)
    {
        return Composition_composition_kind((Composition*) self);
    }
    ComposableRetainerVector* Stack_children(Stack* self)
    {
        return Composition_children((Composition*) self);
    }
    void Stack_clear_children(Stack* self)
    {
        Composition_clear_children((Composition*) self);
    }
    _Bool Stack_set_children(
        Stack* self, ComposableVector* children, OTIOErrorStatus* error_status)
    {
        return Composition_set_children(
            (Composition*) self, children, error_status);
    }
    _Bool Stack_insert_child(
        Stack*           self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status)
    {
        return Composition_insert_child(
            (Composition*) self, index, child, error_status);
    }
    _Bool Stack_set_child(
        Stack*           self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status)
    {
        return Composition_set_child(
            (Composition*) self, index, child, error_status);
    }
    _Bool
    Stack_remove_child(Stack* self, int index, OTIOErrorStatus* error_status)
    {
        return Composition_remove_child(
            (Composition*) self, index, error_status);
    }
    _Bool Stack_append_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status)
    {
        return Composition_append_child(
            (Composition*) self, child, error_status);
    }
    _Bool Stack_is_parent_of(Stack* self, Composable* other)
    {
        return Composition_is_parent_of((Composition*) self, other);
    }
    OptionalPairRationalTime* Stack_handles_of_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status)
    {
        return Composition_handles_of_child(
            (Composition*) self, child, error_status);
    }
    TimeRange* Stack_range_of_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status)
    {
        return Composition_range_of_child(
            (Composition*) self, child, error_status);
    }
    TimeRange* Stack_trimmed_range_of_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status)
    {
        return Composition_trimmed_range_of_child(
            (Composition*) self, child, error_status);
    }
    TimeRange* Stack_trim_child_range(Stack* self, TimeRange* child_range)
    {
        return Composition_trim_child_range((Composition*) self, child_range);
    }
    _Bool Stack_has_child(Stack* self, Composable* child)
    {
        return Composition_has_child((Composition*) self, child);
    }
    _Bool Stack_visible(Stack* self)
    {
        return Composition_visible((Composition*) self);
    }
    _Bool Stack_overlapping(Stack* self)
    {
        return Composition_overlapping((Composition*) self);
    }
    TimeRange* Stack_source_range(Stack* self)
    {
        return Composition_source_range((Composition*) self);
    }
    void Stack_set_source_range(Stack* self, TimeRange* source_range)
    {
        Composition_set_source_range((Composition*) self, source_range);
    }
    EffectRetainerVector* Stack_effects(Stack* self)
    {
        return Composition_effects((Composition*) self);
    }
    MarkerRetainerVector* Stack_markers(Stack* self)
    {
        return Composition_markers((Composition*) self);
    }
    RationalTime* Stack_duration(Stack* self, OTIOErrorStatus* error_status)
    {
        return Composition_duration((Composition*) self, error_status);
    }
    TimeRange* Stack_trimmed_range(Stack* self, OTIOErrorStatus* error_status)
    {
        return Composition_trimmed_range((Composition*) self, error_status);
    }
    TimeRange* Stack_visible_range(Stack* self, OTIOErrorStatus* error_status)
    {
        return Composition_visible_range((Composition*) self, error_status);
    }
    TimeRange*
    Stack_trimmed_range_in_parent(Stack* self, OTIOErrorStatus* error_status)
    {
        return Composition_trimmed_range_in_parent(
            (Composition*) self, error_status);
    }
    TimeRange* Stack_range_in_parent(Stack* self, OTIOErrorStatus* error_status)
    {
        return Composition_range_in_parent((Composition*) self, error_status);
    }
    RationalTime* Stack_transformed_time(
        Stack*           self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status)
    {
        return Composition_transformed_time(
            (Composition*) self, time, to_item, error_status);
    }
    TimeRange* Stack_transformed_time_range(
        Stack*           self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status)
    {
        return Composition_transformed_time_range(
            (Composition*) self, time_range, to_item, error_status);
    }
    Composition* Stack_parent(Stack* self)
    {
        return Composition_parent((Composition*) self);
    }
    const char* Stack_name(Stack* self)
    {
        return Composition_name((Composition*) self);
    }
    AnyDictionary* Stack_metadata(Stack* self)
    {
        return Composition_metadata((Composition*) self);
    }
    void Stack_set_name(Stack* self, const char* name)
    {
        Composition_set_name((Composition*) self, name);
    }
    _Bool Stack_possibly_delete(Stack* self)
    {
        return Composition_possibly_delete((Composition*) self);
    }
    _Bool Stack_to_json_file(
        Stack*           self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return Composition_to_json_file(
            (Composition*) self, file_name, error_status, indent);
    }
    const char*
    Stack_to_json_string(Stack* self, OTIOErrorStatus* error_status, int indent)
    {
        return Composition_to_json_string(
            (Composition*) self, error_status, indent);
    }
    _Bool Stack_is_equivalent_to(Stack* self, SerializableObject* other)
    {
        return Composition_is_equivalent_to((Composition*) self, other);
    }
    Stack* Stack_clone(Stack* self, OTIOErrorStatus* error_status)
    {
        return (Stack*) Composition_clone((Composition*) self, error_status);
    }
    const char* Stack_schema_name(Stack* self)
    {
        return Composition_schema_name((Composition*) self);
    }
    int Stack_schema_version(Stack* self)
    {
        return Composition_schema_version((Composition*) self);
    }
#ifdef __cplusplus
}
#endif
