#include "copentimelineio/serializableCollection.h"
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
        return reinterpret_cast<SerializableCollection*>(
            new OTIO_NS::SerializableCollection(
                name,
                *reinterpret_cast<SerializableObjectVectorDef*>(children),
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
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
#ifdef __cplusplus
}
#endif
