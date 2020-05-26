#pragma once

#include "anyDictionary.h"
#include "composable.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include "mapComposableTimeRange.h"
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
    MapComposableTimeRange*
    Track_range_of_all_children(Track* self, OTIOErrorStatus* error_status);
#ifdef __cplusplus
}
#endif
