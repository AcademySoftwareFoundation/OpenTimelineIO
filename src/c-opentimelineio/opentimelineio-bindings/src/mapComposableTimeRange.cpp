#include "copentimelineio/mapComposableTimeRange.h"
#include <map>
#include <opentime/timeRange.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/version.h>
#include <string.h>

typedef std::map<OTIO_NS::Composable*, opentime::TimeRange>::iterator
                                                            MapIterator;
typedef std::map<OTIO_NS::Composable*, opentime::TimeRange> MapDef;

#ifdef __cplusplus
extern "C"
{
#endif
    MapComposableTimeRange* MapComposableTimeRange_create()
    {
        return reinterpret_cast<MapComposableTimeRange*>(new MapDef());
    }
    void MapComposableTimeRange_destroy(MapComposableTimeRange* self)
    {
        delete reinterpret_cast<MapDef*>(self);
    }
    void MapComposableTimeRange_clear(MapComposableTimeRange* self)
    {
        reinterpret_cast<MapDef*>(self)->clear();
    }
    MapComposableTimeRangeIterator*
    MapComposableTimeRange_begin(MapComposableTimeRange* self)
    {
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(reinterpret_cast<MapDef*>(self)->begin()));
    }
    MapComposableTimeRangeIterator*
    MapComposableTimeRange_end(MapComposableTimeRange* self)
    {
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(reinterpret_cast<MapDef*>(self)->end()));
    }
    void MapComposableTimeRange_swap(
        MapComposableTimeRange* self, MapComposableTimeRange* other)
    {
        reinterpret_cast<MapDef*>(self)->swap(
            *reinterpret_cast<MapDef*>(other));
    }
    MapComposableTimeRangeIterator* MapComposableTimeRange_erase(
        MapComposableTimeRange* self, MapComposableTimeRangeIterator* pos)
    {
        MapIterator it = reinterpret_cast<MapDef*>(self)->erase(
            *reinterpret_cast<MapIterator*>(pos));
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(it));
    }
    MapComposableTimeRangeIterator* MapComposableTimeRange_erase_range(
        MapComposableTimeRange*         self,
        MapComposableTimeRangeIterator* first,
        MapComposableTimeRangeIterator* last)
    {
        MapIterator it = reinterpret_cast<MapDef*>(self)->erase(
            *reinterpret_cast<MapIterator*>(first),
            *reinterpret_cast<MapIterator*>(last));
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(it));
    }
    int MapComposableTimeRange_erase_key(
        MapComposableTimeRange* self, Composable* key)
    {
        return reinterpret_cast<MapDef*>(self)->erase(
            reinterpret_cast<OTIO_NS::Composable*>(key));
    }
    int MapComposableTimeRange_size(MapComposableTimeRange* self)
    {
        return reinterpret_cast<MapDef*>(self)->size();
    }
    int MapComposableTimeRange_max_size(MapComposableTimeRange* self)
    {
        return reinterpret_cast<MapDef*>(self)->max_size();
    }
    _Bool MapComposableTimeRange_empty(MapComposableTimeRange* self)
    {
        return reinterpret_cast<MapDef*>(self)->empty();
    }
    MapComposableTimeRangeIterator*
    MapComposableTimeRange_find(MapComposableTimeRange* self, Composable* key)
    {
        MapIterator iter = reinterpret_cast<MapDef*>(self)->find(
            reinterpret_cast<OTIO_NS::Composable*>(key));
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(iter));
    }
    MapComposableTimeRangeIterator* MapComposableTimeRange_insert(
        MapComposableTimeRange* self, Composable* key, TimeRange* anyObj)
    {
        MapIterator it =
            reinterpret_cast<MapDef*>(self)
                ->insert({ reinterpret_cast<OTIO_NS::Composable*>(key),
                           *reinterpret_cast<opentime::TimeRange*>(anyObj) })
                .first;
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(it));
    }
    void MapComposableTimeRangeIterator_advance(
        MapComposableTimeRangeIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<MapIterator*>(iter), dist);
    }
    MapComposableTimeRangeIterator* MapComposableTimeRangeIterator_next(
        MapComposableTimeRangeIterator* iter, int dist)
    {
        MapIterator it = std::next(*reinterpret_cast<MapIterator*>(iter), dist);
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(it));
    }
    MapComposableTimeRangeIterator* MapComposableTimeRangeIterator_prev(
        MapComposableTimeRangeIterator* iter, int dist)
    {
        MapIterator it = std::prev(*reinterpret_cast<MapIterator*>(iter), dist);
        return reinterpret_cast<MapComposableTimeRangeIterator*>(
            new MapIterator(it));
    }
    TimeRange*
    MapComposableTimeRangeIterator_value(MapComposableTimeRangeIterator* iter)
    {
        opentime::TimeRange timeRange =
            (*reinterpret_cast<MapIterator*>(iter))->second;
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    _Bool MapComposableTimeRangeIterator_equal(
        MapComposableTimeRangeIterator* lhs,
        MapComposableTimeRangeIterator* rhs)
    {
        return *reinterpret_cast<MapIterator*>(lhs) ==
               *reinterpret_cast<MapIterator*>(rhs);
    }
    _Bool MapComposableTimeRangeIterator_not_equal(
        MapComposableTimeRangeIterator* lhs,
        MapComposableTimeRangeIterator* rhs)
    {
        return *reinterpret_cast<MapIterator*>(lhs) !=
               *reinterpret_cast<MapIterator*>(rhs);
    }
    void
    MapComposableTimeRangeIterator_destroy(MapComposableTimeRangeIterator* self)
    {
        delete reinterpret_cast<MapIterator*>(self);
    }
#ifdef __cplusplus
}
#endif