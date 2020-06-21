#pragma once

#include "anyDictionary.h"
#include "composable.h"
#include "composableRetainerVector.h"
#include "composableVector.h"
#include "copentime/timeRange.h"
#include "effectRetainerVector.h"
#include "effectVector.h"
#include "errorStatus.h"
#include "item.h"
#include "mapComposableTimeRange.h"
#include "markerRetainerVector.h"
#include "markerVector.h"
#include "optionalPairRationalTime.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Composition;
    typedef struct Composition Composition;
    struct Item;
    typedef struct Item Item;

    Composition* Composition_create(
        const char*    name,
        TimeRange*     source_range,
        AnyDictionary* metadata,
        EffectVector*  effects,
        MarkerVector*  markers);
    const char*               Composition_composition_kind(Composition* self);
    ComposableRetainerVector* Composition_children(Composition* self);
    void                      Composition_clear_children(Composition* self);
    _Bool                     Composition_set_children(
                            Composition*      self,
                            ComposableVector* children,
                            OTIOErrorStatus*  error_status);
    _Bool Composition_insert_child(
        Composition*     self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status);
    _Bool Composition_set_child(
        Composition*     self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status);
    _Bool Composition_remove_child(
        Composition* self, int index, OTIOErrorStatus* error_status);
    _Bool Composition_append_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status);
    _Bool Composition_is_parent_of(Composition* self, Composable* other);
    OptionalPairRationalTime* Composition_handles_of_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Composition_range_of_child_at_index(
        Composition* self, int index, OTIOErrorStatus* error_status);
    TimeRange* Composition_trimmed_range_of_child_at_index(
        Composition* self, int index, OTIOErrorStatus* error_status);
    TimeRange* Composition_range_of_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Composition_trimmed_range_of_child(
        Composition* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange*
          Composition_trim_child_range(Composition* self, TimeRange* child_range);
    _Bool Composition_has_child(Composition* self, Composable* child);
    MapComposableTimeRange* Composition_range_of_all_children(
        Composition* self, OTIOErrorStatus* error_status);

    _Bool      Composition_visible(Composition* self);
    _Bool      Composition_overlapping(Composition* self);
    TimeRange* Composition_source_range(Composition* self);
    void
                          Composition_set_source_range(Composition* self, TimeRange* source_range);
    EffectRetainerVector* Composition_effects(Composition* self);
    MarkerRetainerVector* Composition_markers(Composition* self);
    RationalTime*
               Composition_duration(Composition* self, OTIOErrorStatus* error_status);
    TimeRange* Composition_available_range(
        Composition* self, OTIOErrorStatus* error_status);
    TimeRange*
    Composition_trimmed_range(Composition* self, OTIOErrorStatus* error_status);
    TimeRange*
               Composition_visible_range(Composition* self, OTIOErrorStatus* error_status);
    TimeRange* Composition_trimmed_range_in_parent(
        Composition* self, OTIOErrorStatus* error_status);
    TimeRange* Composition_range_in_parent(
        Composition* self, OTIOErrorStatus* error_status);
    RationalTime* Composition_transformed_time(
        Composition*     self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    TimeRange* Composition_transformed_time_range(
        Composition*     self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    Composition*   Composition_parent(Composition* self);
    const char*    Composition_name(Composition* self);
    AnyDictionary* Composition_metadata(Composition* self);
    void           Composition_set_name(Composition* self, const char* name);
    _Bool          Composition_possibly_delete(Composition* self);
    _Bool          Composition_to_json_file(
                 Composition*     self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Composition_to_json_string(
        Composition* self, OTIOErrorStatus* error_status, int indent);
    _Bool
    Composition_is_equivalent_to(Composition* self, SerializableObject* other);
    Composition*
                Composition_clone(Composition* self, OTIOErrorStatus* error_status);
    const char* Composition_schema_name(Composition* self);
    int         Composition_schema_version(Composition* self);
#ifdef __cplusplus
}
#endif
