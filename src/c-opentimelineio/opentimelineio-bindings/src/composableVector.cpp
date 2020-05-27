#include "copentimelineio/composableVector.h"
#include <opentimelineio/composable.h>
#include <vector>

typedef std::vector<OTIO_NS::Composable*>           ComposableVectorDef;
typedef std::vector<OTIO_NS::Composable*>::iterator ComposableVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    ComposableVector* ComposableVector_create()
    {
        return reinterpret_cast<ComposableVector*>(new ComposableVectorDef());
    }
    void ComposableVector_destroy(ComposableVector* self)
    {
        delete reinterpret_cast<ComposableVectorDef*>(self);
    }
    ComposableVectorIterator* ComposableVector_begin(ComposableVector* self)
    {
        ComposableVectorIteratorDef iter =
            reinterpret_cast<ComposableVectorDef*>(self)->begin();
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(iter));
    }
    ComposableVectorIterator* ComposableVector_end(ComposableVector* self)
    {
        ComposableVectorIteratorDef iter =
            reinterpret_cast<ComposableVectorDef*>(self)->end();
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(iter));
    }
    int ComposableVector_size(ComposableVector* self)
    {
        return reinterpret_cast<ComposableVectorDef*>(self)->size();
    }
    int ComposableVector_max_size(ComposableVector* self)
    {
        return reinterpret_cast<ComposableVectorDef*>(self)->max_size();
    }
    int ComposableVector_capacity(ComposableVector* self)
    {
        return reinterpret_cast<ComposableVectorDef*>(self)->capacity();
    }
    void ComposableVector_resize(ComposableVector* self, int n)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->resize(n);
    }
    _Bool ComposableVector_empty(ComposableVector* self)
    {
        return reinterpret_cast<ComposableVectorDef*>(self)->empty();
    }
    void ComposableVector_shrink_to_fit(ComposableVector* self)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->shrink_to_fit();
    }
    void ComposableVector_reserve(ComposableVector* self, int n)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->reserve(n);
    }
    void ComposableVector_swap(ComposableVector* self, ComposableVector* other)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->swap(
            *reinterpret_cast<ComposableVectorDef*>(other));
    }
    Composable* ComposableVector_at(ComposableVector* self, int pos)
    {
        return reinterpret_cast<Composable*>(
            reinterpret_cast<ComposableVectorDef*>(self)->at(pos));
    }
    void ComposableVector_push_back(ComposableVector* self, Composable* value)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->push_back(
            reinterpret_cast<OTIO_NS::Composable*>(value));
    }
    void ComposableVector_pop_back(ComposableVector* self)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->pop_back();
    }
    ComposableVectorIterator* ComposableVector_insert(
        ComposableVector* self, ComposableVectorIterator* pos, Composable* val)
    {
        ComposableVectorIteratorDef iter =
            reinterpret_cast<ComposableVectorDef*>(self)->insert(
                *reinterpret_cast<ComposableVectorIteratorDef*>(pos),
                reinterpret_cast<OTIO_NS::Composable*>(val));
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(iter));
    }
    void ComposableVector_clear(ComposableVector* self)
    {
        reinterpret_cast<ComposableVectorDef*>(self)->clear();
    }
    ComposableVectorIterator* ComposableVector_erase(
        ComposableVector* self, ComposableVectorIterator* pos)
    {
        ComposableVectorIteratorDef iter =
            reinterpret_cast<ComposableVectorDef*>(self)->erase(
                *reinterpret_cast<ComposableVectorIteratorDef*>(pos));
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(iter));
    }
    ComposableVectorIterator* ComposableVector_erase_range(
        ComposableVector*         self,
        ComposableVectorIterator* first,
        ComposableVectorIterator* last)
    {
        ComposableVectorIteratorDef iter =
            reinterpret_cast<ComposableVectorDef*>(self)->erase(
                *reinterpret_cast<ComposableVectorIteratorDef*>(first),
                *reinterpret_cast<ComposableVectorIteratorDef*>(last));
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(iter));
    }
    void
    ComposableVectorIterator_advance(ComposableVectorIterator* iter, int dist)
    {
        std::advance(
            *reinterpret_cast<ComposableVectorIteratorDef*>(iter), dist);
    }
    ComposableVectorIterator*
    ComposableVectorIterator_next(ComposableVectorIterator* iter, int dist)
    {
        ComposableVectorIteratorDef it = std::next(
            *reinterpret_cast<ComposableVectorIteratorDef*>(iter), dist);
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(it));
    }
    ComposableVectorIterator*
    ComposableVectorIterator_prev(ComposableVectorIterator* iter, int dist)
    {
        ComposableVectorIteratorDef it = std::prev(
            *reinterpret_cast<ComposableVectorIteratorDef*>(iter), dist);
        return reinterpret_cast<ComposableVectorIterator*>(
            new ComposableVectorIteratorDef(it));
    }
    Composable* ComposableVectorIterator_value(ComposableVectorIterator* iter)
    {
        OTIO_NS::Composable* obj =
            **reinterpret_cast<ComposableVectorIteratorDef*>(iter);
        return reinterpret_cast<Composable*>(obj);
    }
    _Bool ComposableVectorIterator_equal(
        ComposableVectorIterator* lhs, ComposableVectorIterator* rhs)
    {
        return *reinterpret_cast<ComposableVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<ComposableVectorIteratorDef*>(rhs);
    }
    _Bool ComposableVectorIterator_not_equal(
        ComposableVectorIterator* lhs, ComposableVectorIterator* rhs)
    {
        return *reinterpret_cast<ComposableVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<ComposableVectorIteratorDef*>(rhs);
    }
    void ComposableVectorIterator_destroy(ComposableVectorIterator* self)
    {
        delete reinterpret_cast<ComposableVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif
