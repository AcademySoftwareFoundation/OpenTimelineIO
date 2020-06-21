#include "copentimelineio/freezeFrame.h"
#include <copentimelineio/effect.h>
#include <copentimelineio/linearTimeWarp.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/freezeFrame.h>

#ifdef __cplusplus
extern "C"
{
#endif
    FreezeFrame* FreezeFrame_create(const char* name, AnyDictionary* metadata)
    {
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

        return reinterpret_cast<FreezeFrame*>(
            new OTIO_NS::FreezeFrame(name_str, metadataDictionary));
    }
    double FreezeFrame_time_scalar(FreezeFrame* self)
    {
        return LinearTimeWarp_time_scalar((LinearTimeWarp*) self);
    }
    void FreezeFrame_set_time_scalar(FreezeFrame* self, double time_scalar)
    {
        LinearTimeWarp_set_time_scalar((LinearTimeWarp*) self, time_scalar);
    }
    const char* FreezeFrame_effect_name(FreezeFrame* self)
    {
        return Effect_effect_name((Effect*) self);
    }
    void FreezeFrame_set_effect_name(FreezeFrame* self, const char* effect_name)
    {
        Effect_set_effect_name((Effect*) self, effect_name);
    }
    const char* FreezeFrame_name(FreezeFrame* self)
    {
        return Effect_name((Effect*) self);
    }
    void FreezeFrame_set_name(FreezeFrame* self, const char* name)
    {
        Effect_set_name((Effect*) self, name);
    }
    AnyDictionary* FreezeFrame_metadata(FreezeFrame* self)
    {
        return Effect_metadata((Effect*) self);
    }
    _Bool FreezeFrame_possibly_delete(FreezeFrame* self)
    {
        return Effect_possibly_delete((Effect*) self);
    }
    _Bool FreezeFrame_to_json_file(
        FreezeFrame*     self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return Effect_to_json_file(
            (Effect*) self, file_name, error_status, indent);
    }
    const char* FreezeFrame_to_json_string(
        FreezeFrame* self, OTIOErrorStatus* error_status, int indent)
    {
        return Effect_to_json_string((Effect*) self, error_status, indent);
    }
    _Bool
    FreezeFrame_is_equivalent_to(FreezeFrame* self, SerializableObject* other)
    {
        return Effect_is_equivalent_to((Effect*) self, other);
    }
    FreezeFrame*
    FreezeFrame_clone(FreezeFrame* self, OTIOErrorStatus* error_status)
    {
        return (FreezeFrame*) Effect_clone((Effect*) self, error_status);
    }
    const char* FreezeFrame_schema_name(FreezeFrame* self)
    {
        return Effect_schema_name((Effect*) self);
    }
    int FreezeFrame_schema_version(FreezeFrame* self)
    {
        return Effect_schema_version((Effect*) self);
    }
#ifdef __cplusplus
}
#endif
