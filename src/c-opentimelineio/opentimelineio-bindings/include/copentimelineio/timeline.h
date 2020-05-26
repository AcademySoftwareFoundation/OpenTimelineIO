#pragma once

#include "anyDictionary.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "stack.h"
#include "trackVector.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Timeline;
    typedef struct Timeline Timeline;

    Timeline* Timeline_create(
        const char*    name,
        RationalTime*  global_start_time,
        AnyDictionary* metadata);
    Stack*        Timeline_tracks(Timeline* self);
    void          Timeline_set_tracks(Timeline* self, Stack* stack);
    RationalTime* Timeline_global_start_time(Timeline* self);
    void          Timeline_set_global_start_time(
                 Timeline* self, RationalTime* global_start_time);
    RationalTime*
               Timeline_duration(Timeline* self, OTIOErrorStatus* error_status);
    TimeRange* Timeline_range_of_child(
        Timeline* self, Composable* child, OTIOErrorStatus* error_status);
    TrackVector* Timeline_audio_tracks(Timeline* self);
    TrackVector* Timeline_video_tracks(Timeline* self);
#ifdef __cplusplus
}
#endif
