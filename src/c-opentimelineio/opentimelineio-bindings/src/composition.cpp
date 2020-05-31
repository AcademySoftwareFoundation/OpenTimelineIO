#include "copentimelineio/composition.h"
#include <map>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/composition.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/marker.h>
#include <string.h>
#include <utility>
#include <vector>

typedef std::vector<OTIO_NS::Marker*>           MarkerVectorDef;
typedef std::vector<OTIO_NS::Marker*>::iterator MarkerVectorIteratorDef;
typedef std::vector<OTIO_NS::Effect*>           EffectVectorDef;
typedef std::vector<OTIO_NS::Effect*>::iterator EffectVectorIteratorDef;
typedef std::map<OTIO_NS::Composable*, opentime::TimeRange>::iterator
                                                            MapIterator;
typedef std::map<OTIO_NS::Composable*, opentime::TimeRange> MapDef;
typedef std::vector<OTIO_NS::Composable::Retainer<OTIO_NS::Composable>>
    ComposableRetainerVectorDef;
typedef std::vector<OTIO_NS::Composable::Retainer<OTIO_NS::Composable>>::
    iterator ComposableRetainerVectorIteratorDef;
typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>
                                                    ComposableRetainer;
typedef std::vector<OTIO_NS::Composable*>           ComposableVectorDef;
typedef std::vector<OTIO_NS::Composable*>::iterator ComposableVectorIteratorDef;
typedef std::pair<
    nonstd::optional<opentime::RationalTime>,
    nonstd::optional<opentime::RationalTime>>
    PairDef;

#ifdef __cplusplus
extern "C"
{
#endif
    Composition* Composition_create(
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

        return reinterpret_cast<Composition*>(new OTIO_NS::Composition(
            name_str,
            timeRangeOptional,
            metadataDictionary,
            effectsVector,
            markersVector));
    }
    const char* Composition_composition_kind(Composition* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::Composition*>(self)->composition_kind();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    ComposableRetainerVector* Composition_children(Composition* self)
    {
        ComposableRetainerVectorDef composableRetainerVector =
            reinterpret_cast<OTIO_NS::Composition*>(self)->children();
        return reinterpret_cast<ComposableRetainerVector*>(
            new ComposableRetainerVectorDef(composableRetainerVector));
    }
    void Composition_clear_children(Composition* self)
    {
        reinterpret_cast<OTIO_NS::Composition*>(self)->clear_children();
    }
    _Bool Composition_set_children(
        Composition*      self,
        ComposableVector* children,
        OTIOErrorStatus*  error_status)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->set_children(
            *reinterpret_cast<ComposableVectorDef*>(children),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool Composition_insert_child(
        Composition*     self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->insert_child(
            index,
            reinterpret_cast<OTIO_NS::Composable*>(child),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool Composition_set_child(
        Composition*     self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->set_child(
            index,
            reinterpret_cast<OTIO_NS::Composable*>(child),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool Composition_remove_child(
        Composition* self, int index, OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->remove_child(
            index, reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool Composition_append_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->append_child(
            reinterpret_cast<OTIO_NS::Composable*>(child),
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool Composition_is_parent_of(Composition* self, Composable* other)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->is_parent_of(
            reinterpret_cast<OTIO_NS::Composable*>(other));
    }
    OptionalPairRationalTime* Composition_handles_of_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status)
    {
        PairDef pairDef =
            reinterpret_cast<OTIO_NS::Composition*>(self)->handles_of_child(
                reinterpret_cast<OTIO_NS::Composable*>(child),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<OptionalPairRationalTime*>(
            new PairDef(pairDef));
    }
    TimeRange* Composition_range_of_child_at_index(
        Composition* self, int index, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Composition*>(self)
                ->range_of_child_at_index(
                    index,
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Composition_trimmed_range_of_child_at_index(
        Composition* self, int index, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Composition*>(self)
                ->trimmed_range_of_child_at_index(
                    index,
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Composition_range_of_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Composition*>(self)->range_of_child(
                reinterpret_cast<OTIO_NS::Composable*>(child),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Composition_trimmed_range_of_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            reinterpret_cast<OTIO_NS::Composition*>(self)
                ->trimmed_range_of_child(
                    reinterpret_cast<OTIO_NS::Composable*>(child),
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        if(timeRangeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<TimeRange*>(
            new opentime::TimeRange(timeRangeOptional.value()));
    }
    TimeRange*
    Composition_trim_child_range(Composition* self, TimeRange* child_range)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            reinterpret_cast<OTIO_NS::Composition*>(self)->trim_child_range(
                *reinterpret_cast<OTIO_NS::TimeRange*>(child_range));
        if(timeRangeOptional == nonstd::nullopt) return NULL;
        return reinterpret_cast<TimeRange*>(
            new opentime::TimeRange(timeRangeOptional.value()));
    }
    _Bool Composition_has_child(Composition* self, Composable* child)
    {
        return reinterpret_cast<OTIO_NS::Composition*>(self)->has_child(
            reinterpret_cast<OTIO_NS::Composable*>(child));
    }
    MapComposableTimeRange* Composition_range_of_all_children(
        Composition* self, OTIOErrorStatus* error_status)
    {
        MapDef mapDef =
            reinterpret_cast<OTIO_NS::Composition*>(self)
                ->range_of_all_children(
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<MapComposableTimeRange*>(new MapDef(mapDef));
    }
#ifdef __cplusplus
}
#endif
