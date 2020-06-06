#include "copentimelineio/effect.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/serializableObject.h>
#include <string.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect> EffectRetainer;

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
    Effect* RetainerEffect_value(RetainerEffect* self)
    {
        return reinterpret_cast<Effect*>(
            reinterpret_cast<EffectRetainer*>(self)->value);
    }
    void RetainerEffect_managed_destroy(RetainerEffect* self)
    {
        delete reinterpret_cast<EffectRetainer*>(self);
    }

    Effect* Effect_create(
        const char* name, const char* effect_name, AnyDictionary* metadata)
    {
        return reinterpret_cast<Effect*>(new OTIO_NS::Effect(
            name,
            effect_name,
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    const char* Effect_effect_name(Effect* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::Effect*>(self)->effect_name();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void Effect_set_effect_name(Effect* self, const char* effect_name)
    {
        reinterpret_cast<OTIO_NS::Effect*>(self)->set_effect_name(effect_name);
    }
#ifdef __cplusplus
}
#endif