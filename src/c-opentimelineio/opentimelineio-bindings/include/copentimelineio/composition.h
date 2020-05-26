#pragma once

#include "anyDictionary.h"
#include "composable.h"
#include "composableRetainerVector.h"
#include "composableVector.h"
#include "copentime/timeRange.h"
#include "effectVector.h"
#include "errorStatus.h"
#include "mapComposableTimeRange.h"
#include "markerVector.h"
#include "optionalPairRationalTime.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Composition;
    typedef struct Composition Composition;

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
#ifdef __cplusplus
}
#endif
