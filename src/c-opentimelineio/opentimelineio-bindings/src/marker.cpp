#include "copentimelineio/marker.h"
#include <opentimelineio/marker.h>

#ifdef __cplusplus
extern "C"
{
#endif
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
#ifdef __cplusplus
}
#endif