#include "copentimelineio/effectRetainerVector.h"
#include <opentimelineio/effect.h>
#include <vector>

typedef std::vector<OTIO_NS::Effect::Retainer<OTIO_NS::Effect>>
    EffectRetainerVectorDef;
typedef std::vector<OTIO_NS::Effect::Retainer<OTIO_NS::Effect>>::iterator
    EffectRetainerVectorIteratorDef;
typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect> EffectRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    EffectRetainerVector* EffectRetainerVector_create()
    {
        return reinterpret_cast<EffectRetainerVector*>(
            new EffectRetainerVectorDef());
    }
    void EffectRetainerVector_destroy(EffectRetainerVector* self)
    {
        delete reinterpret_cast<EffectRetainerVectorDef*>(self);
    }
    EffectRetainerVectorIterator*
    EffectRetainerVector_begin(EffectRetainerVector* self)
    {
        EffectRetainerVectorIteratorDef iter =
            reinterpret_cast<EffectRetainerVectorDef*>(self)->begin();
        return reinterpret_cast<EffectRetainerVectorIterator*>(
            new EffectRetainerVectorIteratorDef(iter));
    }
    EffectRetainerVectorIterator*
    EffectRetainerVector_end(EffectRetainerVector* self)
    {
        EffectRetainerVectorIteratorDef iter =
            reinterpret_cast<EffectRetainerVectorDef*>(self)->end();
        return reinterpret_cast<EffectRetainerVectorIterator*>(
            new EffectRetainerVectorIteratorDef(iter));
    }
    int EffectRetainerVector_size(EffectRetainerVector* self)
    {
        return reinterpret_cast<EffectRetainerVectorDef*>(self)->size();
    }
    int EffectRetainerVector_max_size(EffectRetainerVector* self)
    {
        return reinterpret_cast<EffectRetainerVectorDef*>(self)->max_size();
    }
    int EffectRetainerVector_capacity(EffectRetainerVector* self)
    {
        return reinterpret_cast<EffectRetainerVectorDef*>(self)->capacity();
    }
    void EffectRetainerVector_resize(EffectRetainerVector* self, int n)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->resize(n);
    }
    _Bool EffectRetainerVector_empty(EffectRetainerVector* self)
    {
        return reinterpret_cast<EffectRetainerVectorDef*>(self)->empty();
    }
    void EffectRetainerVector_shrink_to_fit(EffectRetainerVector* self)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->shrink_to_fit();
    }
    void EffectRetainerVector_reserve(EffectRetainerVector* self, int n)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->reserve(n);
    }
    void EffectRetainerVector_swap(
        EffectRetainerVector* self, EffectRetainerVector* other)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->swap(
            *reinterpret_cast<EffectRetainerVectorDef*>(other));
    }
    RetainerEffect* EffectRetainerVector_at(EffectRetainerVector* self, int pos)
    {
        EffectRetainer obj =
            reinterpret_cast<EffectRetainerVectorDef*>(self)->at(pos);
        return reinterpret_cast<RetainerEffect*>(new EffectRetainer(obj));
    }
    void EffectRetainerVector_push_back(
        EffectRetainerVector* self, RetainerEffect* value)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->push_back(
            *reinterpret_cast<EffectRetainer*>(value));
    }
    void EffectRetainerVector_pop_back(EffectRetainerVector* self)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->pop_back();
    }
    EffectRetainerVectorIterator* EffectRetainerVector_insert(
        EffectRetainerVector*         self,
        EffectRetainerVectorIterator* pos,
        RetainerEffect*               val)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->insert(
            *reinterpret_cast<EffectRetainerVectorIteratorDef*>(pos),
            *reinterpret_cast<EffectRetainer*>(val));
    }
    void EffectRetainerVector_clear(EffectRetainerVector* self)
    {
        reinterpret_cast<EffectRetainerVectorDef*>(self)->clear();
    }
    EffectRetainerVectorIterator* EffectRetainerVector_erase(
        EffectRetainerVector* self, EffectRetainerVectorIterator* pos)
    {
        EffectRetainerVectorIteratorDef iter =
            reinterpret_cast<EffectRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<EffectRetainerVectorIteratorDef*>(pos));
        return reinterpret_cast<EffectRetainerVectorIterator*>(
            new EffectRetainerVectorIteratorDef(iter));
    }
    EffectRetainerVectorIterator* EffectRetainerVector_erase_range(
        EffectRetainerVector*         self,
        EffectRetainerVectorIterator* first,
        EffectRetainerVectorIterator* last)
    {
        EffectRetainerVectorIteratorDef iter =
            reinterpret_cast<EffectRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<EffectRetainerVectorIteratorDef*>(first),
                *reinterpret_cast<EffectRetainerVectorIteratorDef*>(last));
        return reinterpret_cast<EffectRetainerVectorIterator*>(
            new EffectRetainerVectorIteratorDef(iter));
    }
    void EffectRetainerVectorIterator_advance(
        EffectRetainerVectorIterator* iter, int dist)
    {
        std::advance(
            *reinterpret_cast<EffectRetainerVectorIteratorDef*>(iter), dist);
    }
    EffectRetainerVectorIterator* EffectRetainerVectorIterator_next(
        EffectRetainerVectorIterator* iter, int dist)
    {
        std::next(
            *reinterpret_cast<EffectRetainerVectorIteratorDef*>(iter), dist);
    }
    EffectRetainerVectorIterator* EffectRetainerVectorIterator_prev(
        EffectRetainerVectorIterator* iter, int dist)
    {
        std::prev(
            *reinterpret_cast<EffectRetainerVectorIteratorDef*>(iter), dist);
    }
    RetainerEffect*
    EffectRetainerVectorIterator_value(EffectRetainerVectorIterator* iter)
    {
        EffectRetainer obj =
            **reinterpret_cast<EffectRetainerVectorIteratorDef*>(iter);
        return reinterpret_cast<RetainerEffect*>(new EffectRetainer(obj));
    }
    _Bool EffectRetainerVectorIterator_equal(
        EffectRetainerVectorIterator* lhs, EffectRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<EffectRetainerVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<EffectRetainerVectorIteratorDef*>(rhs);
    }
    _Bool EffectRetainerVectorIterator_not_equal(
        EffectRetainerVectorIterator* lhs, EffectRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<EffectRetainerVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<EffectRetainerVectorIteratorDef*>(rhs);
    }
    void
    EffectRetainerVectorIterator_destroy(EffectRetainerVectorIterator* self)
    {
        delete reinterpret_cast<EffectRetainerVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif