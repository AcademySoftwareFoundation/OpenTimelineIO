#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include "mediaReference.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Clip;
    typedef struct Clip Clip;

    Clip* Clip_create(
        const char*     name,
        MediaReference* media_reference,
        TimeRange*      source_range,
        AnyDictionary*  metadata);
    void Clip_set_media_reference(Clip* self, MediaReference* media_reference);
    MediaReference* Clip_media_reference(Clip* self);
    TimeRange* Clip_available_range(Clip* self, OTIOErrorStatus* error_status);
#ifdef __cplusplus
}
#endif
