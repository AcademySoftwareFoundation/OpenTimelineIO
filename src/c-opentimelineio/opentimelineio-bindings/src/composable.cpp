#include "copentimelineio/composable.h"
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentime/rationalTime.h>
#include <opentimelineio/any.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/composition.h>
#include <opentimelineio/errorStatus.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>
    ComposableRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    RetainerComposable* RetainerComposable_create(Composable* obj)
    {
        return reinterpret_cast<RetainerComposable*>(new ComposableRetainer(
            reinterpret_cast<OTIO_NS::Composable*>(obj)));
    }
    Composable* RetainerComposable_take_value(RetainerComposable* self)
    {
        return reinterpret_cast<Composable*>(
            reinterpret_cast<ComposableRetainer*>(self)->take_value());
    }
    Composable* RetainerComposable_value(RetainerComposable* self)
    {
        return reinterpret_cast<Composable*>(
            reinterpret_cast<ComposableRetainer*>(self)->value);
    }
    void RetainerComposable_managed_destroy(RetainerComposable* self)
    {
        delete reinterpret_cast<ComposableRetainer*>(self);
    }

    Composable* Composable_create()
    {
        return reinterpret_cast<Composable*>(new OTIO_NS::Composable());
    }
    Composable* Composable_create_with_name_and_metadata(
        const char* name, AnyDictionary* metadata)
    {
        return reinterpret_cast<Composable*>(new OTIO_NS::Composable(
            name, *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    _Bool Composable_visible(Composable* self)
    {
        return reinterpret_cast<OTIO_NS::Composable*>(self)->visible();
    }
    _Bool Composable_overlapping(Composable* self)
    {
        return reinterpret_cast<OTIO_NS::Composable*>(self)->overlapping();
    }
    Composition* Composable_parent(Composable* self)
    {
        return reinterpret_cast<Composition*>(
            reinterpret_cast<OTIO_NS::Composable*>(self)->parent());
    }
    RationalTime*
    Composable_duration(Composable* self, OTIOErrorStatus* error_status)
    {
        opentime::RationalTime rationalTime =
            reinterpret_cast<OTIO_NS::Composable*>(self)->duration(
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    const char* Composable_name(Composable* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    AnyDictionary* Composable_metadata(Composable* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    void Composable_set_name(Composable* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    _Bool Composable_possibly_delete(Composable* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool Composable_to_json_file(
        Composable*      self,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* Composable_to_json_string(
        Composable* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool
    Composable_is_equivalent_to(Composable* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, (SerializableObject*) other);
    }
    Composable*
    Composable_clone(Composable* self, OTIOErrorStatus* error_status)
    {
        return (Composable*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* Composable_schema_name(Composable* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int Composable_schema_version(Composable* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
