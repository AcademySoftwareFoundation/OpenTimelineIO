#pragma once

#include "anyDictionary.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
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
    TrackVector*   Timeline_audio_tracks(Timeline* self);
    TrackVector*   Timeline_video_tracks(Timeline* self);
    const char*    Timeline_name(Timeline* self);
    void           Timeline_set_name(Timeline* self, const char* name);
    AnyDictionary* Timeline_metadata(Timeline* self);
    _Bool          Timeline_possibly_delete(Timeline* self);
    _Bool          Timeline_to_json_file(
                 Timeline*        self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Timeline_to_json_string(
        Timeline* self, OTIOErrorStatus* error_status, int indent);
    _Bool Timeline_is_equivalent_to(Timeline* self, SerializableObject* other);
    Timeline*   Timeline_clone(Timeline* self, OTIOErrorStatus* error_status);
    _Bool       Timeline_is_unknown_schema(Timeline* self);
    const char* Timeline_schema_name(Timeline* self);
    int         Timeline_schema_version(Timeline* self);
#ifdef __cplusplus
}
#endif
