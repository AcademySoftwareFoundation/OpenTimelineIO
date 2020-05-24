#pragma once

#include "anyDictionary.h"
#include "errorStatus.h"
#include "serializableObject.h"
#include "typeInfo.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    typedef SerializableObject* (*TypeRegistryCreateFunction)();
    typedef void (*TypeRegistryUpgradeFunction)(AnyDictionary*);
    struct TypeRegistry;
    typedef struct TypeRegistry TypeRegistry;
    TypeRegistry*               TypeRegistry_instance();
    /*_Bool                       TypeRegistry_register_type(
                              TypeRegistry*              self,
                              const char*                schema_name,
                              int                        schema_version,
                              TypeInfo*                  type,
                              TypeRegistryCreateFunction create, //unable to cast this function pointer to std::function because of the wrapped return type
                              const char*                class_name);*/
    _Bool TypeRegistry_register_type_from_existing_type(
        TypeRegistry*    self,
        const char*      schema_name,
        int              schema_version,
        const char*      existing_schema_name,
        OTIOErrorStatus* error_status);
    /*_Bool TypeRegistry_register_upgrade_function(
        TypeRegistry*               self,
        const char*                 schema_name,
        int                         version_to_upgrade_to,
        TypeRegistryUpgradeFunction upgrade_function);*/
    SerializableObject* TypeRegistry_instance_from_schema(
        TypeRegistry*    self,
        const char*      schema_name,
        int              schema_version,
        AnyDictionary*   dict,
        OTIOErrorStatus* error_status);
    _Bool TypeRegistry_set_type_record(
        TypeRegistry*       self,
        SerializableObject* var1,
        const char*         schema_name,
        OTIOErrorStatus*    error_status);
    void TypeRegistry_destroy(TypeRegistry* self);
#ifdef __cplusplus
}
#endif
