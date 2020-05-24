#pragma once

#include <opentimelineio/effect.h>
#include <opentimelineio/serializableObject.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect> EffectRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    struct RetainerEffect;
    typedef struct RetainerEffect RetainerEffect;
    struct Effect;
    typedef struct Effect Effect;
    RetainerEffect*       RetainerEffect_create(Effect* obj);
    Effect*               RetainerEffect_take_value(RetainerEffect* self);
    void                  RetainerEffect_managed_destroy(RetainerEffect* self);
#ifdef __cplusplus
}
#endif