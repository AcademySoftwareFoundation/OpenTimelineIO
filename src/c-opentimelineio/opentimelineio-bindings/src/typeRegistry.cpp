#include "copentimelineio/typeRegistry.h"
#include <opentimelineio/typeRegistry.h>

#ifdef __cplusplus
extern "C"
{
#endif

    TypeRegistry* TypeRegistry_instance()
    {
        return reinterpret_cast<TypeRegistry*>(
            &OTIO_NS::TypeRegistry::instance());
    }
    /*_Bool TypeRegistry_register_type(
        TypeRegistry*              self,
        const char*                schema_name,
        int                        schema_version,
        TypeInfo*                  type,
        TypeRegistryCreateFunction create, //unable to cast this function pointer to std::function because of the wrapped return type
        const char*                class_name)
    {
        std::function<OTIO_NS::SerializableObject*()> create_func =
            static_cast<OTIO_NS::SerializableObject*()>(create);
        return reinterpret_cast<OTIO_NS::TypeRegistry*>(self)->register_type(
            schema_name,
            reinterpret_cast<std::type_info*>(type),
            create_func,
            class_name);
    }*/
    _Bool TypeRegistry_register_type_from_existing_type(
        TypeRegistry*    self,
        const char*      schema_name,
        int              schema_version,
        const char*      existing_schema_name,
        OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<OTIO_NS::TypeRegistry*>(self)
            ->register_type_from_existing_type(
                schema_name,
                schema_version,
                existing_schema_name,
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    //    _Bool TypeRegistry_register_upgrade_function(
    //        TypeRegistry*               self,
    //        const char*                 schema_name,
    //        int                         version_to_upgrade_to,
    //        TypeRegistryUpgradeFunction upgrade_function);
    //
    SerializableObject* TypeRegistry_instance_from_schema(
        TypeRegistry*    self,
        const char*      schema_name,
        int              schema_version,
        AnyDictionary*   dict,
        OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<SerializableObject*>(
            reinterpret_cast<OTIO_NS::TypeRegistry*>(self)
                ->instance_from_schema(
                    schema_name,
                    schema_version,
                    *reinterpret_cast<OTIO_NS::AnyDictionary*>(dict),
                    reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status)));
    }
    _Bool TypeRegistry_set_type_record(
        TypeRegistry*       self,
        SerializableObject* var1,
        const char*         schema_name,
        OTIOErrorStatus*    error_status)
    {
        return reinterpret_cast<OTIO_NS::TypeRegistry*>(self)->set_type_record(
            reinterpret_cast<OTIO_NS::SerializableObject*>(var1),
            schema_name,
            reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    void TypeRegistry_destroy(TypeRegistry* self)
    {
        delete reinterpret_cast<OTIO_NS::TypeRegistry*>(self);
    }
#ifdef __cplusplus
}
#endif