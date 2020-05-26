#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"

#ifdef __cplusplus
extern "C"
{
#endif
    extern const char* MarkerColor_pink;
    extern const char* MarkerColor_red;
    extern const char* MarkerColor_orange;
    extern const char* MarkerColor_yellow;
    extern const char* MarkerColor_green;
    extern const char* MarkerColor_cyan;
    extern const char* MarkerColor_blue;
    extern const char* MarkerColor_purple;
    extern const char* MarkerColor_magenta;
    extern const char* MarkerColor_black;
    extern const char* MarkerColor_white;
    struct RetainerMarker;
    typedef struct RetainerMarker RetainerMarker;
    struct Marker;
    typedef struct Marker Marker;

    RetainerMarker* RetainerMarker_create(Marker* obj);
    Marker*         RetainerMarker_take_value(RetainerMarker* self);
    void            RetainerMarker_managed_destroy(RetainerMarker* self);

    Marker* Marker_create(
        const char*    name,
        TimeRange*     marked_range,
        const char*    color,
        AnyDictionary* metadata);
    const char* Marker_color(Marker* self);
    void        Marker_set_color(Marker* self, const char* color);
    TimeRange*  Marker_marked_range(Marker* self);
    void        Marker_set_marked_range(Marker* self, TimeRange* marked_range);
#ifdef __cplusplus
}
#endif