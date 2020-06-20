#pragma once

#include "anyDictionary.h"
#include "composition.h"
#include "copentime/timeRange.h"
#include "effectRetainerVector.h"
#include "errorStatus.h"
#include "item.h"
#include "markerRetainerVector.h"
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
    TimeRange* Clip_source_range(Clip* self);
    void       Clip_set_source_range(Clip* self, TimeRange* source_range);
    EffectRetainerVector* Clip_effects(Clip* self);
    MarkerRetainerVector* Clip_markers(Clip* self);
    RationalTime* Clip_duration(Clip* self, OTIOErrorStatus* error_status);
    TimeRange*    Clip_trimmed_range(Clip* self, OTIOErrorStatus* error_status);
    TimeRange*    Clip_visible_range(Clip* self, OTIOErrorStatus* error_status);
    TimeRange*
               Clip_trimmed_range_in_parent(Clip* self, OTIOErrorStatus* error_status);
    TimeRange* Clip_range_in_parent(Clip* self, OTIOErrorStatus* error_status);
    RationalTime* Clip_transformed_time(
        Clip*            self,
        RationalTime*    time,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    TimeRange* Clip_transformed_time_range(
        Clip*            self,
        TimeRange*       time_range,
        Item*            to_item,
        OTIOErrorStatus* error_status);
    _Bool          Clip_visible(Clip* self);
    _Bool          Clip_overlapping(Clip* self);
    Composition*   Clip_parent(Clip* self);
    const char*    Clip_name(Clip* self);
    AnyDictionary* Clip_metadata(Clip* self);
    void           Clip_set_name(Clip* self, const char* name);
    _Bool          Clip_possibly_delete(Clip* self);
    _Bool          Clip_to_json_file(
                 Clip*            self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char*
                Clip_to_json_string(Clip* self, OTIOErrorStatus* error_status, int indent);
    _Bool       Clip_is_equivalent_to(Clip* self, SerializableObject* other);
    Clip*       Clip_clone(Clip* self, OTIOErrorStatus* error_status);
    const char* Clip_schema_name(Clip* self);
    int         Clip_schema_version(Clip* self);
#ifdef __cplusplus
}
#endif
