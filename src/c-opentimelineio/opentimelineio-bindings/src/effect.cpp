#include "copentimelineio/effect.h"
#include <opentimelineio/effect.h>

#ifdef __cplusplus
extern "C"
{
#endif
    RetainerEffect* RetainerEffect_create(Effect* obj)
    {
        return reinterpret_cast<RetainerEffect*>(
            new EffectRetainer(reinterpret_cast<OTIO_NS::Effect*>(obj)));
    }
    Effect* RetainerEffect_take_value(RetainerEffect* self)
    {
        return reinterpret_cast<Effect*>(
            reinterpret_cast<EffectRetainer*>(self)->take_value());
    }
    void RetainerEffect_managed_destroy(RetainerEffect* self)
    {
        delete reinterpret_cast<EffectRetainer*>(self);
    }
#ifdef __cplusplus
}
#endif