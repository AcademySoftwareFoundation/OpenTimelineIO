#pragma once

#include "composable.h"
#include "copentime/timeRange.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif

    struct MapComposableTimeRangeIterator;
    typedef struct MapComposableTimeRangeIterator
        MapComposableTimeRangeIterator;
    struct MapComposableTimeRange;
    typedef struct MapComposableTimeRange MapComposableTimeRange;

    MapComposableTimeRange* MapComposableTimeRange_create();
    void MapComposableTimeRange_destroy(MapComposableTimeRange* self);
    void MapComposableTimeRange_clear(MapComposableTimeRange* self);
    MapComposableTimeRangeIterator*
    MapComposableTimeRange_begin(MapComposableTimeRange* self);
    MapComposableTimeRangeIterator*
         MapComposableTimeRange_end(MapComposableTimeRange* self);
    void MapComposableTimeRange_swap(
        MapComposableTimeRange* self, MapComposableTimeRange* other);
    MapComposableTimeRangeIterator* MapComposableTimeRange_erase(
        MapComposableTimeRange* self, MapComposableTimeRangeIterator* pos);
    MapComposableTimeRangeIterator* MapComposableTimeRange_erase_range(
        MapComposableTimeRange*         self,
        MapComposableTimeRangeIterator* first,
        MapComposableTimeRangeIterator* last);
    int MapComposableTimeRange_erase_key(
        MapComposableTimeRange* self, Composable* key);
    int   MapComposableTimeRange_size(MapComposableTimeRange* self);
    int   MapComposableTimeRange_max_size(MapComposableTimeRange* self);
    _Bool MapComposableTimeRange_empty(MapComposableTimeRange* self);
    MapComposableTimeRangeIterator*
                                    MapComposableTimeRange_find(MapComposableTimeRange* self, Composable* key);
    MapComposableTimeRangeIterator* MapComposableTimeRange_insert(
        MapComposableTimeRange* self, Composable* key, TimeRange* anyObj);
    void MapComposableTimeRangeIterator_advance(
        MapComposableTimeRangeIterator* iter, int dist);
    MapComposableTimeRangeIterator* MapComposableTimeRangeIterator_next(
        MapComposableTimeRangeIterator* iter, int dist);
    MapComposableTimeRangeIterator* MapComposableTimeRangeIterator_prev(
        MapComposableTimeRangeIterator* iter, int dist);
    TimeRange*
          MapComposableTimeRangeIterator_value(MapComposableTimeRangeIterator* iter);
    _Bool MapComposableTimeRangeIterator_equal(
        MapComposableTimeRangeIterator* lhs,
        MapComposableTimeRangeIterator* rhs);
    _Bool MapComposableTimeRangeIterator_not_equal(
        MapComposableTimeRangeIterator* lhs,
        MapComposableTimeRangeIterator* rhs);
    void MapComposableTimeRangeIterator_destroy(
        MapComposableTimeRangeIterator* self);
#ifdef __cplusplus
}
#endif