#include "copentimelineio/track.h"
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/track.h>
#include <optional>
#include <string.h>
#include <utility>

typedef std::map<OTIO_NS::Composable*, opentime::TimeRange>::iterator
    MapComposableTimeRangeIteratorDef;
typedef std::map<OTIO_NS::Composable*, opentime::TimeRange>
    MapComposableTimeRangeDef;

typedef std::pair<
    nonstd::optional<opentime::RationalTime>,
    nonstd::optional<opentime::RationalTime>>
    OptionalPairRationalTimeDef;
typedef std::pair<
    OTIO_NS::Composable::Retainer<OTIO_NS::Composable>,
    OTIO_NS::Composable::Retainer<OTIO_NS::Composable>>
    RetainerPairComposableDef;

#ifdef __cplusplus
extern "C"
{
#endif
    const char* TrackKind_Video = OTIO_NS::Track::Kind::video;
    const char* TrackKind_Audio = OTIO_NS::Track::Kind::audio;

    Track* Track_create(
        const char*    name,
        TimeRange*     source_range,
        const char*    kind,
        AnyDictionary* metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(source_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(source_range));
        }
        return reinterpret_cast<Track*>(new OTIO_NS::Track(
            name,
            timeRangeOptional,
            kind,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    const char* Track_kind(Track* self)
    {
        std::string returnStr = reinterpret_cast<OTIO_NS::Track*>(self)->kind();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void Track_set_kind(Track* self, const char* kind)
    {
        reinterpret_cast<OTIO_NS::Track*>(self)->set_kind(kind);
    }
    TimeRange* Track_range_of_child_at_index(
        Track* self, int index, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Track*>(self)->range_of_child_at_index(
                index, reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Track_trimmed_range_of_child_at_index(
        Track* self, int index, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Track*>(self)
                ->trimmed_range_of_child_at_index(
                    index,
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeRange* Track_available_range(Track* self, OTIOErrorStatus* error_status)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Track*>(self)->available_range(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    OptionalPairRationalTime* Track_handles_of_child(
        Track* self, Composable* child, OTIOErrorStatus* error_status)
    {
        OptionalPairRationalTimeDef optionalPairRationalTime =
            reinterpret_cast<OTIO_NS::Track*>(self)->handles_of_child(
                reinterpret_cast<OTIO_NS::Composable*>(child),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<OptionalPairRationalTime*>(
            new OptionalPairRationalTimeDef(optionalPairRationalTime));
    }
    RetainerPairComposable* Track_neighbors_of(
        Track*                        self,
        Composable*                   item,
        OTIOErrorStatus*              error_status,
        OTIO_Track_NeighbourGapPolicy insert_gap)
    {
        RetainerPairComposableDef retainerPairComposable =
            reinterpret_cast<OTIO_NS::Track*>(self)->neighbors_of(
                reinterpret_cast<OTIO_NS::Composable*>(item),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status),
                static_cast<OTIO_NS::Track::NeighborGapPolicy>(insert_gap));
        return reinterpret_cast<RetainerPairComposable*>(
            new RetainerPairComposableDef(retainerPairComposable));
    }
    MapComposableTimeRange*
    Track_range_of_all_children(Track* self, OTIOErrorStatus* error_status)
    {
        MapComposableTimeRangeDef mapComposableTimeRange =
            reinterpret_cast<OTIO_NS::Track*>(self)->range_of_all_children(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<MapComposableTimeRange*>(
            new MapComposableTimeRangeDef(mapComposableTimeRange));
    }
#ifdef __cplusplus
}
#endif
