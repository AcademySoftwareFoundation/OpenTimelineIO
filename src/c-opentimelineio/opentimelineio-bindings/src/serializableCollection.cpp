#include "copentimelineio/serializableCollection.h"
#include <copentimelineio/serializableObject.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
#include <opentimelineio/serializableCollection.h>

typedef std::vector<
    OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>
    SerializableObjectRetainerVectorDef;
typedef std::vector<OTIO_NS::SerializableObject::Retainer<
    OTIO_NS::SerializableObject>>::iterator
                                                  SerializableObjectRetainerVectorIteratorDef;
typedef std::vector<OTIO_NS::SerializableObject*> SerializableObjectVectorDef;
typedef std::vector<OTIO_NS::SerializableObject*>::iterator
    SerializableObjectVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    SerializableCollection* SerializableCollection_create(
        const char*               name,
        SerializableObjectVector* children,
        AnyDictionary*            metadata)
    {
        std::string name_str = std::string();
        if(name != NULL) { name_str = name; }
        SerializableObjectVectorDef childrenVector =
            SerializableObjectVectorDef();
        if(children != NULL)
        {
            childrenVector =
                *reinterpret_cast<SerializableObjectVectorDef*>(children);
        }
        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
        {
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);
        }
        return reinterpret_cast<SerializableCollection*>(
            new OTIO_NS::SerializableCollection(
                name_str, childrenVector, metadataDictionary));
    }
    SerializableObjectRetainerVector*
    SerializableCollection_children(SerializableCollection* self)
    {
        SerializableObjectRetainerVectorDef vec =
            reinterpret_cast<OTIO_NS::SerializableCollection*>(self)
                ->children();
        return reinterpret_cast<SerializableObjectRetainerVector*>(
            new SerializableObjectRetainerVectorDef(vec));
    }
    void SerializableCollection_set_children(
        SerializableCollection* self, SerializableObjectVector* children)
    {
        reinterpret_cast<OTIO_NS::SerializableCollection*>(self)->set_children(
            *reinterpret_cast<SerializableObjectVectorDef*>(children));
    }
    void SerializableCollection_clear_children(SerializableCollection* self)
    {
        reinterpret_cast<OTIO_NS::SerializableCollection*>(self)
            ->clear_children();
    }
    void SerializableCollection_insert_child(
        SerializableCollection* self, int index, SerializableObject* child)
    {
        reinterpret_cast<OTIO_NS::SerializableCollection*>(self)->insert_child(
            index, reinterpret_cast<OTIO_NS::SerializableObject*>(child));
    }
    _Bool SerializableCollection_set_child(
        SerializableCollection* self,
        int                     index,
        SerializableObject*     child,
        OTIOErrorStatus*        error_status)
    {
        return reinterpret_cast<OTIO_NS::SerializableCollection*>(self)
            ->set_child(
                index,
                reinterpret_cast<OTIO_NS::SerializableObject*>(child),
                reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    _Bool SerializableCollection_remove_child(
        SerializableCollection* self, int index, OTIOErrorStatus* error_status)
    {
        return reinterpret_cast<OTIO_NS::SerializableCollection*>(self)
            ->remove_child(
                index, reinterpret_cast<OTIO_NS::ErrorStatus*>(error_status));
    }
    const char* SerializableCollection_name(SerializableCollection* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void SerializableCollection_set_name(
        SerializableCollection* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* SerializableCollection_metadata(SerializableCollection* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool SerializableCollection_possibly_delete(SerializableCollection* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool SerializableCollection_to_json_file(
        SerializableCollection* self,
        const char*             file_name,
        OTIOErrorStatus*        error_status,
        int                     indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* SerializableCollection_to_json_string(
        SerializableCollection* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool SerializableCollection_is_equivalent_to(
        SerializableCollection* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    SerializableCollection* SerializableCollection_clone(
        SerializableCollection* self, OTIOErrorStatus* error_status)
    {
        return (SerializableCollection*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* SerializableCollection_schema_name(SerializableCollection* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int SerializableCollection_schema_version(SerializableCollection* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
