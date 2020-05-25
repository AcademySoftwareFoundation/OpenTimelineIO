#pragma once

#include "anyDictionary.h"

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