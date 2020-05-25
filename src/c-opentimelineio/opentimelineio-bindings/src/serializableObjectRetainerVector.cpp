#include "copentimelineio/serializableObjectRetainerVector.h"
#include <opentimelineio/serializableObject.h>

typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>
    SerializableObjectRetainer;
typedef std::vector<
    OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>
    SerializableObjectRetainerVectorDef;
typedef std::vector<OTIO_NS::SerializableObject::Retainer<
    OTIO_NS::SerializableObject>>::iterator
    SerializableObjectRetainerVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    SerializableObjectRetainerVector* SerializableObjectRetainerVector_create()
    {
        return reinterpret_cast<SerializableObjectRetainerVector*>(
            new SerializableObjectRetainerVectorDef());
    }
    void SerializableObjectRetainerVector_destroy(
        SerializableObjectRetainerVector* self)
    {
        delete reinterpret_cast<SerializableObjectRetainerVectorDef*>(self);
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_begin(
        SerializableObjectRetainerVector* self)
    {
        SerializableObjectRetainerVectorIteratorDef iter =
            reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
                ->begin();
        return reinterpret_cast<SerializableObjectRetainerVectorIterator*>(
            new SerializableObjectRetainerVectorIteratorDef(iter));
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_end(SerializableObjectRetainerVector* self)
    {
        SerializableObjectRetainerVectorIteratorDef iter =
            reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->end();
        return reinterpret_cast<SerializableObjectRetainerVectorIterator*>(
            new SerializableObjectRetainerVectorIteratorDef(iter));
    }
    int SerializableObjectRetainerVector_size(
        SerializableObjectRetainerVector* self)
    {
        return reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
            ->size();
    }
    int SerializableObjectRetainerVector_max_size(
        SerializableObjectRetainerVector* self)
    {
        return reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
            ->max_size();
    }
    int SerializableObjectRetainerVector_capacity(
        SerializableObjectRetainerVector* self)
    {
        return reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
            ->capacity();
    }
    void SerializableObjectRetainerVector_resize(
        SerializableObjectRetainerVector* self, int n)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->resize(n);
    }
    _Bool SerializableObjectRetainerVector_empty(
        SerializableObjectRetainerVector* self)
    {
        return reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
            ->empty();
    }
    void SerializableObjectRetainerVector_shrink_to_fit(
        SerializableObjectRetainerVector* self)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
            ->shrink_to_fit();
    }
    void SerializableObjectRetainerVector_reserve(
        SerializableObjectRetainerVector* self, int n)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->reserve(
            n);
    }
    void SerializableObjectRetainerVector_swap(
        SerializableObjectRetainerVector* self,
        SerializableObjectRetainerVector* other)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->swap(
            *reinterpret_cast<SerializableObjectRetainerVectorDef*>(other));
    }
    RetainerSerializableObject* SerializableObjectRetainerVector_at(
        SerializableObjectRetainerVector* self, int pos)
    {
        SerializableObjectRetainer obj =
            reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->at(
                pos);
        return reinterpret_cast<RetainerSerializableObject*>(
            new SerializableObjectRetainer(obj));
    }
    void SerializableObjectRetainerVector_push_back(
        SerializableObjectRetainerVector* self,
        RetainerSerializableObject*       value)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->push_back(
            *reinterpret_cast<SerializableObjectRetainer*>(value));
    }
    void SerializableObjectRetainerVector_pop_back(
        SerializableObjectRetainerVector* self)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)
            ->pop_back();
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_insert(
        SerializableObjectRetainerVector*         self,
        SerializableObjectRetainerVectorIterator* pos,
        RetainerSerializableObject*               val)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->insert(
            *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                pos),
            *reinterpret_cast<SerializableObjectRetainer*>(val));
    }
    void SerializableObjectRetainerVector_clear(
        SerializableObjectRetainerVector* self)
    {
        reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->clear();
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_erase(
        SerializableObjectRetainerVector*         self,
        SerializableObjectRetainerVectorIterator* pos)
    {
        SerializableObjectRetainerVectorIteratorDef iter =
            reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                    pos));
        return reinterpret_cast<SerializableObjectRetainerVectorIterator*>(
            new SerializableObjectRetainerVectorIteratorDef(iter));
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_erase_range(
        SerializableObjectRetainerVector*         self,
        SerializableObjectRetainerVectorIterator* first,
        SerializableObjectRetainerVectorIterator* last)
    {
        SerializableObjectRetainerVectorIteratorDef iter =
            reinterpret_cast<SerializableObjectRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                    first),
                *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                    last));
        return reinterpret_cast<SerializableObjectRetainerVectorIterator*>(
            new SerializableObjectRetainerVectorIteratorDef(iter));
    }
    void SerializableObjectRetainerVectorIterator_advance(
        SerializableObjectRetainerVectorIterator* iter, int dist)
    {
        std::advance(
            *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                iter),
            dist);
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVectorIterator_next(
        SerializableObjectRetainerVectorIterator* iter, int dist)
    {
        std::next(
            *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                iter),
            dist);
    }
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVectorIterator_prev(
        SerializableObjectRetainerVectorIterator* iter, int dist)
    {
        std::prev(
            *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                iter),
            dist);
    }
    RetainerSerializableObject* SerializableObjectRetainerVectorIterator_value(
        SerializableObjectRetainerVectorIterator* iter)
    {
        SerializableObjectRetainer obj =
            **reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                iter);
        return reinterpret_cast<RetainerSerializableObject*>(
            new SerializableObjectRetainer(obj));
    }
    _Bool SerializableObjectRetainerVectorIterator_equal(
        SerializableObjectRetainerVectorIterator* lhs,
        SerializableObjectRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                   lhs) ==
               *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                   rhs);
    }
    _Bool SerializableObjectRetainerVectorIterator_not_equal(
        SerializableObjectRetainerVectorIterator* lhs,
        SerializableObjectRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                   lhs) !=
               *reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
                   rhs);
    }
    void SerializableObjectRetainerVectorIterator_destroy(
        SerializableObjectRetainerVectorIterator* self)
    {
        delete reinterpret_cast<SerializableObjectRetainerVectorIteratorDef*>(
            self);
    }
#ifdef __cplusplus
}
#endif