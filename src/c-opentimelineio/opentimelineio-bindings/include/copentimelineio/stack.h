#pragma once

#include "anyDictionary.h"
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
    struct Stack;
    typedef struct Stack Stack;

    Stack* Stack_create(
        const char*    name,
        TimeRange*     source_range,
        AnyDictionary* metadata,
        EffectVector*  effects,
        MarkerVector*  markers);
    TimeRange* Stack_range_of_child_at_index(
        Stack* self, int index, OTIOErrorStatus* error_status);
    TimeRange* Stack_trimmed_range_of_child_at_index(
        Stack* self, int index, OTIOErrorStatus* error_status);
    TimeRange*
    Stack_available_range(Stack* self, OTIOErrorStatus* error_status);
    MapComposableTimeRange*
    Stack_range_of_all_children(Stack* self, OTIOErrorStatus* error_status);

    const char*               Stack_composition_kind(Stack* self);
    ComposableRetainerVector* Stack_children(Stack* self);
    void                      Stack_clear_children(Stack* self);
    _Bool                     Stack_set_children(
                            Stack* self, ComposableVector* children, OTIOErrorStatus* error_status);
    _Bool Stack_insert_child(
        Stack*           self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status);
    _Bool Stack_set_child(
        Stack*           self,
        int              index,
        Composable*      child,
        OTIOErrorStatus* error_status);
    _Bool
          Stack_remove_child(Stack* self, int index, OTIOErrorStatus* error_status);
    _Bool Stack_append_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status);
    _Bool Stack_is_parent_of(Stack* self, Composable* other);
    OptionalPairRationalTime* Stack_handles_of_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Stack_range_of_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Stack_trimmed_range_of_child(
        Stack* self, Composable* child, OTIOErrorStatus* error_status);
    TimeRange* Stack_trim_child_range(Stack* self, TimeRange* child_range);
    _Bool      Stack_has_child(Stack* self, Composable* child);

    _Bool      Stack_visible(Stack* self);
    _Bool      Stack_overlapping(Stack* self);
    TimeRange* Stack_source_range(Stack* self);
    void       Stack_set_source_range(Stack* self, TimeRange* source_range);
    EffectRetainerVector* Stack_effects(Stack* self);
    MarkerRetainerVector* Stack_markers(Stack* self);
    RationalTime* Stack_duration(Stack* self, OTIOErrorStatus* error_status);
    TimeRange* Stack_trimmed_range(Stack* self, OTIOErrorStatus* error_status);
    TimeRange* Stack_visible_range(Stack* self, OTIOErrorStatus* error_status);
    TimeRange*
    Stack_trimmed_range_in_parent(Stack* self, OTIOErrorStatus* error_status);
    TimeRange*
                  Stack_range_in_parent(Stack* self, OTIOErrorStatus* error_status);
    RationalTime* Stack_transformed_time(
        Stack*           self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    TimeRange* Stack_transformed_time_range(
        Stack*           self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    Composition*   Stack_parent(Stack* self);
    const char*    Stack_name(Stack* self);
    AnyDictionary* Stack_metadata(Stack* self);
    void           Stack_set_name(Stack* self, const char* name);
    _Bool          Stack_possibly_delete(Stack* self);
    _Bool          Stack_to_json_file(
                 Stack*           self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Stack_to_json_string(
        Stack* self, OTIOErrorStatus* error_status, int indent);
    _Bool       Stack_is_equivalent_to(Stack* self, SerializableObject* other);
    Stack*      Stack_clone(Stack* self, OTIOErrorStatus* error_status);
    const char* Stack_schema_name(Stack* self);
    int         Stack_schema_version(Stack* self);
#ifdef __cplusplus
}
#endif
