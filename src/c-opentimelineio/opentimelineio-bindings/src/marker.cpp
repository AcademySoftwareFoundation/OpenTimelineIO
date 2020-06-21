#include "copentimelineio/marker.h"
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
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
    Marker* RetainerMarker_value(RetainerMarker* self)
    {
        return reinterpret_cast<Marker*>(
            reinterpret_cast<MarkerRetainer*>(self)->value);
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
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        opentime::TimeRange marked_range_tr = opentime::TimeRange();
        if(marked_range != NULL)
            marked_range_tr =
                *reinterpret_cast<opentime::TimeRange*>(marked_range);

        std::string color_str = OTIO_NS::Marker::Color::green;
        if(color != NULL) color_str = color;

        OTIO_NS::AnyDictionary metdata_dictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metdata_dictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<Marker*>(new OTIO_NS::Marker(
            name_str, marked_range_tr, color_str, metdata_dictionary));
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
    const char* Marker_name(Marker* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void Marker_set_name(Marker* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* Marker_metadata(Marker* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool Marker_possibly_delete(Marker* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool Marker_to_json_file(
        Marker*          self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* Marker_to_json_string(
        Marker* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool Marker_is_equivalent_to(Marker* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    Marker* Marker_clone(Marker* self, OTIOErrorStatus* error_status)
    {
        return (Marker*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* Marker_schema_name(Marker* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int Marker_schema_version(Marker* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif