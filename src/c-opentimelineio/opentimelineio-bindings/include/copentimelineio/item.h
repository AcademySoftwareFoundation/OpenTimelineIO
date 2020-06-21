#pragma once

#include "anyDictionary.h"
#include "composition.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "effectRetainerVector.h"
#include "effectVector.h"
#include "errorStatus.h"
#include "markerRetainerVector.h"
#include "markerVector.h"

#ifdef __cplusplus
extern "C"
{
#endif
    struct Item;
    typedef struct Item Item;
    struct Effect;
    typedef struct Effect Effect;
    struct Marker;
    typedef struct Marker Marker;
    Item*                 Item_create(
                        const char*    name,
                        TimeRange*     source_range,
                        AnyDictionary* metadata,
                        EffectVector*  effects,
                        MarkerVector*  markers);
    _Bool      Item_visible(Item* self);
    _Bool      Item_overlapping(Item* self);
    TimeRange* Item_source_range(Item* self);
    void       Item_set_source_range(Item* self, TimeRange* source_range);
    EffectRetainerVector* Item_effects(Item* self);
    MarkerRetainerVector* Item_markers(Item* self);
    RationalTime* Item_duration(Item* self, OTIOErrorStatus* error_status);
    TimeRange* Item_available_range(Item* self, OTIOErrorStatus* error_status);
    TimeRange* Item_trimmed_range(Item* self, OTIOErrorStatus* error_status);
    TimeRange* Item_visible_range(Item* self, OTIOErrorStatus* error_status);
    TimeRange*
               Item_trimmed_range_in_parent(Item* self, OTIOErrorStatus* error_status);
    TimeRange* Item_range_in_parent(Item* self, OTIOErrorStatus* error_status);
    RationalTime* Item_transformed_time(
        Item*            self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    TimeRange* Item_transformed_time_range(
        Item*            self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    Composition*   Item_parent(Item* self);
    const char*    Item_name(Item* self);
    AnyDictionary* Item_metadata(Item* self);
    void           Item_set_name(Item* self, const char* name);
    _Bool          Item_possibly_delete(Item* self);
    _Bool          Item_to_json_file(
                 Item*            self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char*
                Item_to_json_string(Item* self, OTIOErrorStatus* error_status, int indent);
    _Bool       Item_is_equivalent_to(Item* self, SerializableObject* other);
    Item*       Item_clone(Item* self, OTIOErrorStatus* error_status);
    const char* Item_schema_name(Item* self);
    int         Item_schema_version(Item* self);
#ifdef __cplusplus
}
#endif