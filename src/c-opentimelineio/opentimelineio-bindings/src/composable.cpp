#include "copentimelineio/composable.h"
#include <opentime/rationalTime.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/errorStatus.h>

#ifdef __cplusplus
extern "C"
{
#endif
    Composable* Composable_create()
    {
        return reinterpret_cast<Composable*>(new OTIO_NS::Composable());
    }
    Composable* Composable_create_with_name_and_metadata(
        const char* name, AnyDictionary* metadata)
    {
        return reinterpret_cast<Composable*>(new OTIO_NS::Composable(
            name, *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    _Bool Composable_visible(Composable* self)
    {
        return reinterpret_cast<OTIO_NS::Composable*>(self)->visible();
    }
    _Bool Composable_overlapping(Composable* self)
    {
        return reinterpret_cast<OTIO_NS::Composable*>(self)->overlapping();
    }
    /*Composition* Composable_parent(Composable* self)
    {
        return reinterpret_cast<Composition*>(
            reinterpret_cast<OTIO_NS::Composable*>(self)->parent());
    }*/
    RationalTime*
    Composable_duration(Composable* self, OTIOErrorStatus* error_status)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<OTIO_NS::Composable*>(self)->duration(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
#ifdef __cplusplus
}
#endif
