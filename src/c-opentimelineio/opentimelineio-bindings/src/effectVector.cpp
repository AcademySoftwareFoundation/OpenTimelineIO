#include "copentimelineio/effectVector.h"
#include <opentimelineio/effect.h>
#include <vector>

typedef std::vector<OTIO_NS::Effect*>           EffectVectorDef;
typedef std::vector<OTIO_NS::Effect*>::iterator EffectVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    EffectVector* EffectVector_create()
    {
        return reinterpret_cast<EffectVector*>(new EffectVectorDef());
    }
    void EffectVector_destroy(EffectVector* self)
    {
        delete reinterpret_cast<EffectVectorDef*>(self);
    }
    EffectVectorIterator* EffectVector_begin(EffectVector* self)
    {
        EffectVectorIteratorDef iter =
            reinterpret_cast<EffectVectorDef*>(self)->begin();
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(iter));
    }
    EffectVectorIterator* EffectVector_end(EffectVector* self)
    {
        EffectVectorIteratorDef iter =
            reinterpret_cast<EffectVectorDef*>(self)->end();
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(iter));
    }
    int EffectVector_size(EffectVector* self)
    {
        return reinterpret_cast<EffectVectorDef*>(self)->size();
    }
    int EffectVector_max_size(EffectVector* self)
    {
        return reinterpret_cast<EffectVectorDef*>(self)->max_size();
    }
    int EffectVector_capacity(EffectVector* self)
    {
        return reinterpret_cast<EffectVectorDef*>(self)->capacity();
    }
    void EffectVector_resize(EffectVector* self, int n)
    {
        reinterpret_cast<EffectVectorDef*>(self)->resize(n);
    }
    _Bool EffectVector_empty(EffectVector* self)
    {
        return reinterpret_cast<EffectVectorDef*>(self)->empty();
    }
    void EffectVector_shrink_to_fit(EffectVector* self)
    {
        reinterpret_cast<EffectVectorDef*>(self)->shrink_to_fit();
    }
    void EffectVector_reserve(EffectVector* self, int n)
    {
        reinterpret_cast<EffectVectorDef*>(self)->reserve(n);
    }
    void EffectVector_swap(EffectVector* self, EffectVector* other)
    {
        reinterpret_cast<EffectVectorDef*>(self)->swap(
            *reinterpret_cast<EffectVectorDef*>(other));
    }
    Effect* EffectVector_at(EffectVector* self, int pos)
    {
        return reinterpret_cast<Effect*>(
            reinterpret_cast<EffectVectorDef*>(self)->at(pos));
    }
    void EffectVector_push_back(EffectVector* self, Effect* value)
    {
        reinterpret_cast<EffectVectorDef*>(self)->push_back(
            reinterpret_cast<OTIO_NS::Effect*>(value));
    }
    void EffectVector_pop_back(EffectVector* self)
    {
        reinterpret_cast<EffectVectorDef*>(self)->pop_back();
    }
    EffectVectorIterator* EffectVector_insert(
        EffectVector* self, EffectVectorIterator* pos, Effect* val)
    {
        EffectVectorIteratorDef iter =
            reinterpret_cast<EffectVectorDef*>(self)->insert(
                *reinterpret_cast<EffectVectorIteratorDef*>(pos),
                reinterpret_cast<OTIO_NS::Effect*>(val));
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(iter));
    }
    void EffectVector_clear(EffectVector* self)
    {
        reinterpret_cast<EffectVectorDef*>(self)->clear();
    }
    EffectVectorIterator*
    EffectVector_erase(EffectVector* self, EffectVectorIterator* pos)
    {
        EffectVectorIteratorDef iter =
            reinterpret_cast<EffectVectorDef*>(self)->erase(
                *reinterpret_cast<EffectVectorIteratorDef*>(pos));
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(iter));
    }
    EffectVectorIterator* EffectVector_erase_range(
        EffectVector*         self,
        EffectVectorIterator* first,
        EffectVectorIterator* last)
    {
        EffectVectorIteratorDef iter =
            reinterpret_cast<EffectVectorDef*>(self)->erase(
                *reinterpret_cast<EffectVectorIteratorDef*>(first),
                *reinterpret_cast<EffectVectorIteratorDef*>(last));
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(iter));
    }
    void EffectVectorIterator_advance(EffectVectorIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<EffectVectorIteratorDef*>(iter), dist);
    }
    EffectVectorIterator*
    EffectVectorIterator_next(EffectVectorIterator* iter, int dist)
    {
        EffectVectorIteratorDef it =
            std::next(*reinterpret_cast<EffectVectorIteratorDef*>(iter), dist);
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(it));
    }
    EffectVectorIterator*
    EffectVectorIterator_prev(EffectVectorIterator* iter, int dist)
    {
        EffectVectorIteratorDef it =
            std::prev(*reinterpret_cast<EffectVectorIteratorDef*>(iter), dist);
        return reinterpret_cast<EffectVectorIterator*>(
            new EffectVectorIteratorDef(it));
    }
    Effect* EffectVectorIterator_value(EffectVectorIterator* iter)
    {
        OTIO_NS::Effect* obj =
            **reinterpret_cast<EffectVectorIteratorDef*>(iter);
        return reinterpret_cast<Effect*>(obj);
    }
    _Bool EffectVectorIterator_equal(
        EffectVectorIterator* lhs, EffectVectorIterator* rhs)
    {
        return *reinterpret_cast<EffectVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<EffectVectorIteratorDef*>(rhs);
    }
    _Bool EffectVectorIterator_not_equal(
        EffectVectorIterator* lhs, EffectVectorIterator* rhs)
    {
        return *reinterpret_cast<EffectVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<EffectVectorIteratorDef*>(rhs);
    }
    void EffectVectorIterator_destroy(EffectVectorIterator* self)
    {
        delete reinterpret_cast<EffectVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif
