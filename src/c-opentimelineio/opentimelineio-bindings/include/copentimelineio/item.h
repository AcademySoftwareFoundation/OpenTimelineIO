#pragma once

#include "anyDictionary.h"
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
#ifdef __cplusplus
}
#endif