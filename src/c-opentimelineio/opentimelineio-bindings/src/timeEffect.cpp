#include "copentimelineio/timeEffect.h"
#include <copentimelineio/effect.h>
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
    const char* TimeEffect_effect_name(TimeEffect* self)
    {
        return Effect_effect_name((Effect*) self);
    }
    void TimeEffect_set_effect_name(TimeEffect* self, const char* effect_name)
    {
        Effect_set_effect_name((Effect*) self, effect_name);
    }
    const char* TimeEffect_name(TimeEffect* self)
    {
        return Effect_name((Effect*) self);
    }
    void TimeEffect_set_name(TimeEffect* self, const char* name)
    {
        Effect_set_name((Effect*) self, name);
    }
    AnyDictionary* TimeEffect_metadata(TimeEffect* self)
    {
        return Effect_metadata((Effect*) self);
    }
    _Bool TimeEffect_possibly_delete(TimeEffect* self)
    {
        return Effect_possibly_delete((Effect*) self);
    }
    _Bool TimeEffect_to_json_file(
        TimeEffect*      self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return Effect_to_json_file(
            (Effect*) self, file_name, error_status, indent);
    }
    const char* TimeEffect_to_json_string(
        TimeEffect* self, OTIOErrorStatus* error_status, int indent)
    {
        return Effect_to_json_string((Effect*) self, error_status, indent);
    }
    _Bool
    TimeEffect_is_equivalent_to(TimeEffect* self, SerializableObject* other)
    {
        return Effect_is_equivalent_to((Effect*) self, other);
    }
    TimeEffect*
    TimeEffect_clone(TimeEffect* self, OTIOErrorStatus* error_status)
    {
        return (TimeEffect*) Effect_clone((Effect*) self, error_status);
    }
    const char* TimeEffect_schema_name(TimeEffect* self)
    {
        return Effect_schema_name((Effect*) self);
    }
    int TimeEffect_schema_version(TimeEffect* self)
    {
        return Effect_schema_version((Effect*) self);
    }
#ifdef __cplusplus
}
#endif
