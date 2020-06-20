#include "copentimelineio/effect.h"
#include <copentimelineio/serializableObjectWithMetadata.h>
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
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        std::string effect_name_str = std::string();
        if(effect_name != NULL) effect_name_str = effect_name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<Effect*>(
            new OTIO_NS::Effect(name_str, effect_name_str, metadataDictionary));
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

    const char* Effect_name(Effect* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void Effect_set_name(Effect* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* Effect_metadata(Effect* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool Effect_possibly_delete(Effect* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool Effect_to_json_file(
        Effect*          self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* Effect_to_json_string(
        Effect* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool Effect_is_equivalent_to(Effect* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    Effect* Effect_clone(Effect* self, OTIOErrorStatus* error_status)
    {
        return (Effect*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* Effect_schema_name(Effect* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int Effect_schema_version(Effect* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif