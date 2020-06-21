#pragma once

#include "anyDictionary.h"
#include "composable.h"
#include "composableRetainerVector.h"
#include "composableVector.h"
#include "copentime/timeRange.h"
#include "effectRetainerVector.h"
#include "errorStatus.h"
#include "item.h"
#include "mapComposableTimeRange.h"
#include "markerRetainerVector.h"
#include "optionalPairRationalTime.h"
#include "retainerPairComposable.h"

#ifdef __cplusplus
extern "C"
{
#endif
#include <stdbool.h>
    struct Track;
    typedef struct Track Track;

    typedef enum
    {
        OTIO_Track_NeighbourGapPolicy_never              = 0,
        OTIO_Track_NeighbourGapPolicy_around_transitions = 1,
    } OTIO_Track_NeighbourGapPolicy_;
    typedef int OTIO_Track_NeighbourGapPolicy;

    extern const char* TrackKind_Video;
    extern const char* TrackKind_Audio;

    Track* Track_create(
        const char*    name,
        TimeRange*     source_range,
        const char*    kind,
        AnyDictionary* metadata);
    const char* Track_kind(Track* self);
    void        Track_set_kind(Track* self, const char* kind);
    TimeRange*  Track_range_of_child_at_index(
         Track* self, int index, OTIOErrorStatus* error_status);
    TimeRange* Track_trimmed_range_of_child_at_index(
        Track* self, int index, OTIOErrorStatus* error_status);
    TimeRange*
                              Track_available_range(Track* self, OTIOErrorStatus* error_status);
    OptionalPairRationalTime* Track_handles_of_child(
        Track* self, Composable* child, OTIOErrorStatus* error_status);
    RetainerPairComposable* Track_neighbors_of(
        Track*                        self,
        Composable*                   item,
        OTIOErrorStatus*              error_status,
        OTIO_Track_NeighbourGapPolicy insert_gap);
    ComposableVector* Track_each_clip(Track* self);
    MapComposableTimeRange*
    Track_range_of_all_children(Track* self, OTIOErrorStatus* error_status);

    const char*               Track_composition_kind(Track* self);
    ComposableRetainerVector* Track_children(Track* self);
    void                      Track_clear_children(Track* self);
    _Bool                     Track_set_children(
                            Track* self, ComposableVector* children, OTIOErrorStatus* error_status);
    _Bool Track_insert_child(
        Track*           self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status);
    _Bool Track_set_child(
        Track*           self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status);
    _Bool
          Track_remove_child(Track* self, int index, OTIOErrorStatus* error_status);
    _Bool Track_append_child(
        Track* self, Composable* child, OTIOErrorStatus* error_status);
    _Bool      Track_is_parent_of(Track* self, Composable* other);
    TimeRange* Track_range_of_child(
        Track* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Track_trimmed_range_of_child(
        Track* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Track_trim_child_range(Track* self, TimeRange* child_range);
    _Bool      Track_has_child(Track* self, Composable* child);

    _Bool      Track_visible(Track* self);
    _Bool      Track_overlapping(Track* self);
    TimeRange* Track_source_range(Track* self);
    void       Track_set_source_range(Track* self, TimeRange* source_range);
    EffectRetainerVector* Track_effects(Track* self);
    MarkerRetainerVector* Track_markers(Track* self);
    RationalTime* Track_duration(Track* self, OTIOErrorStatus* error_status);
    TimeRange*
               Track_available_range(Track* self, OTIOErrorStatus* error_status);
    TimeRange* Track_trimmed_range(Track* self, OTIOErrorStatus* error_status);
    TimeRange* Track_visible_range(Track* self, OTIOErrorStatus* error_status);
    TimeRange*
    Track_trimmed_range_in_parent(Track* self, OTIOErrorStatus* error_status);
    TimeRange*
                  Track_range_in_parent(Track* self, OTIOErrorStatus* error_status);
    RationalTime* Track_transformed_time(
        Track*           self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    TimeRange* Track_transformed_time_range(
        Track*           self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    Composition*   Track_parent(Track* self);
    const char*    Track_name(Track* self);
    AnyDictionary* Track_metadata(Track* self);
    void           Track_set_name(Track* self, const char* name);
    _Bool          Track_possibly_delete(Track* self);
    _Bool          Track_to_json_file(
                 Track*           self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Track_to_json_string(
        Track* self, OTIOErrorStatus* error_status, int indent);
    _Bool       Track_is_equivalent_to(Track* self, SerializableObject* other);
    Track*      Track_clone(Track* self, OTIOErrorStatus* error_status);
    const char* Track_schema_name(Track* self);
    int         Track_schema_version(Track* self);
#ifdef __cplusplus
}
#endif
