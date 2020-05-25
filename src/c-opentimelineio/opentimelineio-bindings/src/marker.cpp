#include "copentimelineio/marker.h"
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>
#include <string.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker> MarkerRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    const char*     MarkerColor_pink    = "PINK";
    const char*     MarkerColor_red     = "RED";
    const char*     MarkerColor_orange  = "ORANGE";
    const char*     MarkerColor_yellow  = "YELLOW";
    const char*     MarkerColor_green   = "GREEN";
    const char*     MarkerColor_cyan    = "CYAN";
    const char*     MarkerColor_blue    = "BLUE";
    const char*     MarkerColor_purple  = "PURPLE";
    const char*     MarkerColor_magenta = "MAGENTA";
    const char*     MarkerColor_black   = "BLACK";
    const char*     MarkerColor_white   = "WHITE";
    RetainerMarker* RetainerMarker_create(Marker* obj)
    {
        return reinterpret_cast<RetainerMarker*>(
            new MarkerRetainer(reinterpret_cast<OTIO_NS::Marker*>(obj)));
    }
    Marker* RetainerMarker_take_value(RetainerMarker* self)
    {
        return reinterpret_cast<Marker*>(
            reinterpret_cast<MarkerRetainer*>(self)->take_value());
    }
    void RetainerMarker_managed_destroy(RetainerMarker* self)
    {
        delete reinterpret_cast<MarkerRetainer*>(self);
    }

    Marker* Marker_create(
        const char*    name,
        TimeRange*     marked_range,
        const char*    color,
        AnyDictionary* metadata)
    {
        return reinterpret_cast<Marker*>(new OTIO_NS::Marker(
            name,
            *reinterpret_cast<opentime::TimeRange*>(marked_range),
            color,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    const char* Marker_color(Marker* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::Marker*>(self)->color();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void Marker_set_color(Marker* self, const char* color)
    {
        reinterpret_cast<OTIO_NS::Marker*>(self)->set_color(color);
    }
    TimeRange* Marker_marked_range(Marker* self)
    {
        opentime::TimeRange timeRange =
            reinterpret_cast<OTIO_NS::Marker*>(self)->marked_range();
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    void Marker_set_marked_range(Marker* self, TimeRange* marked_range)
    {
        reinterpret_cast<OTIO_NS::Marker*>(self)->set_marked_range(
            *reinterpret_cast<OTIO_NS::TimeRange*>(marked_range));
    }
#ifdef __cplusplus
}
#endif