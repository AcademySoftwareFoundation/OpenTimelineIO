#pragma once

#include "anyDictionary.h"
#include "composition.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "effectRetainerVector.h"
#include "effectVector.h"
#include "item.h"
#include "markerRetainerVector.h"
#include "markerVector.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Gap;
    typedef struct Gap Gap;

    Gap* Gap_create_with_source_range(
        TimeRange*     source_range,
        const char*    name,
        EffectVector*  effects,
        MarkerVector*  markers,
        AnyDictionary* metadata);
    Gap* Gap_create_with_duration(
        RationalTime*  duration,
        const char*    name,
        EffectVector*  effects,
        MarkerVector*  markers,
        AnyDictionary* metadata);
    _Bool      Gap_visible(Gap* self);
    _Bool      Gap_overlapping(Gap* self);
    TimeRange* Gap_source_range(Gap* self);
    void       Gap_set_source_range(Gap* self, TimeRange* source_range);
    EffectRetainerVector* Gap_effects(Gap* self);
    MarkerRetainerVector* Gap_markers(Gap* self);
    RationalTime* Gap_duration(Gap* self, OTIOErrorStatus* error_status);
    TimeRange*    Gap_available_range(Gap* self, OTIOErrorStatus* error_status);
    TimeRange*    Gap_trimmed_range(Gap* self, OTIOErrorStatus* error_status);
    TimeRange*    Gap_visible_range(Gap* self, OTIOErrorStatus* error_status);
    TimeRange*
                  Gap_trimmed_range_in_parent(Gap* self, OTIOErrorStatus* error_status);
    TimeRange*    Gap_range_in_parent(Gap* self, OTIOErrorStatus* error_status);
    RationalTime* Gap_transformed_time(
        Gap*             self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    TimeRange* Gap_transformed_time_range(
        Gap*             self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    Composition*   Gap_parent(Gap* self);
    const char*    Gap_name(Gap* self);
    AnyDictionary* Gap_metadata(Gap* self);
    void           Gap_set_name(Gap* self, const char* name);
    _Bool          Gap_possibly_delete(Gap* self);
    _Bool          Gap_to_json_file(
                 Gap*             self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char*
                Gap_to_json_string(Gap* self, OTIOErrorStatus* error_status, int indent);
    _Bool       Gap_is_equivalent_to(Gap* self, SerializableObject* other);
    Gap*        Gap_clone(Gap* self, OTIOErrorStatus* error_status);
    const char* Gap_schema_name(Gap* self);
    int         Gap_schema_version(Gap* self);
#ifdef __cplusplus
}
#endif
