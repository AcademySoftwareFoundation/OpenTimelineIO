#pragma once

#include <opentimelineio/marker.h>
#include <opentimelineio/serializableObject.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker> MarkerRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    struct RetainerMarker;
    typedef struct RetainerMarker RetainerMarker;
    struct Marker;
    typedef struct Marker Marker;
    RetainerMarker*       RetainerMarker_create(Marker* obj);
    Marker*               RetainerMarker_take_value(RetainerMarker* self);
    void                  RetainerMarker_managed_destroy(RetainerMarker* self);
#ifdef __cplusplus
}
#endif