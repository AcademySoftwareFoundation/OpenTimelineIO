#include "copentimelineio/timeEffect.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/timeEffect.h>

#ifdef __cplusplus
extern "C"
{
#endif
    TimeEffect* TimeEffect_create(
        const char* name, const char* effect_name, AnyDictionary* metadata)
    {
        return reinterpret_cast<TimeEffect*>(new OTIO_NS::TimeEffect(
            name,
            effect_name,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
#ifdef __cplusplus
}
#endif
