#pragma once

#include "anyDictionary.h"
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

    RetainerEffect* RetainerEffect_create(Effect* obj);
    Effect*         RetainerEffect_take_value(RetainerEffect* self);
    void            RetainerEffect_managed_destroy(RetainerEffect* self);

    Effect* Effect_create(
        const char* name, const char* effect_name, AnyDictionary* metadata);
    const char* Effect_effect_name(Effect* self);
    void        Effect_set_effect_name(Effect* self, const char* effect_name);
#ifdef __cplusplus
}
#endif