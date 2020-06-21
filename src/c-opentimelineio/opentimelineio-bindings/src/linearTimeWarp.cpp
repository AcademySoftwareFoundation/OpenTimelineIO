#include "copentimelineio/linearTimeWarp.h"
#include <copentimelineio/effect.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/linearTimeWarp.h>

#ifdef __cplusplus
extern "C"
{
#endif
    LinearTimeWarp* LinearTimeWarp_create(
        const char*    name,
        const char*    effect_name,
        double         time_scalar,
        AnyDictionary* metadata)
    {
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        std::string effect_name_str = "LinearTimeWarp";
        if(effect_name != NULL) effect_name_str = effect_name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<LinearTimeWarp*>(new OTIO_NS::LinearTimeWarp(
            name_str, effect_name_str, time_scalar, metadataDictionary));
    }
    double LinearTimeWarp_time_scalar(LinearTimeWarp* self)
    {
        return reinterpret_cast<OTIO_NS::LinearTimeWarp*>(self)->time_scalar();
    }
    void
    LinearTimeWarp_set_time_scalar(LinearTimeWarp* self, double time_scalar)
    {
        reinterpret_cast<OTIO_NS::LinearTimeWarp*>(self)->set_time_scalar(
            time_scalar);
    }
    const char* LinearTimeWarp_effect_name(LinearTimeWarp* self)
    {
        return Effect_effect_name((Effect*) self);
    }
    void LinearTimeWarp_set_effect_name(
        LinearTimeWarp* self, const char* effect_name)
    {
        Effect_set_name((Effect*) self, effect_name);
    }
    const char* LinearTimeWarp_name(LinearTimeWarp* self)
    {
        return Effect_name((Effect*) self);
    }
    void LinearTimeWarp_set_name(LinearTimeWarp* self, const char* name)
    {
        Effect_set_name((Effect*) self, name);
    }
    AnyDictionary* LinearTimeWarp_metadata(LinearTimeWarp* self)
    {
        return Effect_metadata((Effect*) self);
    }
    _Bool LinearTimeWarp_possibly_delete(LinearTimeWarp* self)
    {
        return Effect_possibly_delete((Effect*) self);
    }
    _Bool LinearTimeWarp_to_json_file(
        LinearTimeWarp*  self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return Effect_to_json_file(
            (Effect*) self, file_name, error_status, indent);
    }
    const char* LinearTimeWarp_to_json_string(
        LinearTimeWarp* self, OTIOErrorStatus* error_status, int indent)
    {
        return Effect_to_json_string((Effect*) self, error_status, indent);
    }
    _Bool LinearTimeWarp_is_equivalent_to(
        LinearTimeWarp* self, SerializableObject* other)
    {
        return Effect_is_equivalent_to((Effect*) self, other);
    }
    LinearTimeWarp*
    LinearTimeWarp_clone(LinearTimeWarp* self, OTIOErrorStatus* error_status)
    {
        return (LinearTimeWarp*) Effect_clone((Effect*) self, error_status);
    }
    const char* LinearTimeWarp_schema_name(LinearTimeWarp* self)
    {
        return Effect_schema_name((Effect*) self);
    }
    int LinearTimeWarp_schema_version(LinearTimeWarp* self)
    {
        return Effect_schema_version((Effect*) self);
    }
#ifdef __cplusplus
}
#endif
