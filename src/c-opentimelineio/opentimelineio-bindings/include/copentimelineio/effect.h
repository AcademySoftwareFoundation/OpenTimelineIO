#pragma once

#include "anyDictionary.h"
#include "serializableObject.h"

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
    Effect*         RetainerEffect_value(RetainerEffect* self);
    void            RetainerEffect_managed_destroy(RetainerEffect* self);

    Effect* Effect_create(
        const char* name, const char* effect_name, AnyDictionary* metadata);
    const char* Effect_effect_name(Effect* self);
    void        Effect_set_effect_name(Effect* self, const char* effect_name);
    const char* Effect_name(Effect* self);
    void        Effect_set_name(Effect* self, const char* name);
    AnyDictionary* Effect_metadata(Effect* self);
    _Bool          Effect_possibly_delete(Effect* self);
    _Bool          Effect_to_json_file(
                 Effect*          self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Effect_to_json_string(
        Effect* self, OTIOErrorStatus* error_status, int indent);
    _Bool   Effect_is_equivalent_to(Effect* self, SerializableObject* other);
    Effect* Effect_clone(Effect* self, OTIOErrorStatus* error_status);
    const char* Effect_schema_name(Effect* self);
    int         Effect_schema_version(Effect* self);
#ifdef __cplusplus
}
#endif