#include "copentimelineio/composableRetainerVector.h"
#include <opentimelineio/composable.h>
#include <vector>

typedef std::vector<OTIO_NS::Composable::Retainer<OTIO_NS::Composable>>
    ComposableRetainerVectorDef;
typedef std::vector<OTIO_NS::Composable::Retainer<OTIO_NS::Composable>>::
    iterator ComposableRetainerVectorIteratorDef;
typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>
    ComposableRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    ComposableRetainerVector* ComposableRetainerVector_create()
    {
        return reinterpret_cast<ComposableRetainerVector*>(
            new ComposableRetainerVectorDef());
    }
    void ComposableRetainerVector_destroy(ComposableRetainerVector* self)
    {
        delete reinterpret_cast<ComposableRetainerVectorDef*>(self);
    }
    ComposableRetainerVectorIterator*
    ComposableRetainerVector_begin(ComposableRetainerVector* self)
    {
        ComposableRetainerVectorIteratorDef iter =
            reinterpret_cast<ComposableRetainerVectorDef*>(self)->begin();
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(iter));
    }
    ComposableRetainerVectorIterator*
    ComposableRetainerVector_end(ComposableRetainerVector* self)
    {
        ComposableRetainerVectorIteratorDef iter =
            reinterpret_cast<ComposableRetainerVectorDef*>(self)->end();
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(iter));
    }
    int ComposableRetainerVector_size(ComposableRetainerVector* self)
    {
        return reinterpret_cast<ComposableRetainerVectorDef*>(self)->size();
    }
    int ComposableRetainerVector_max_size(ComposableRetainerVector* self)
    {
        return reinterpret_cast<ComposableRetainerVectorDef*>(self)->max_size();
    }
    int ComposableRetainerVector_capacity(ComposableRetainerVector* self)
    {
        return reinterpret_cast<ComposableRetainerVectorDef*>(self)->capacity();
    }
    void ComposableRetainerVector_resize(ComposableRetainerVector* self, int n)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->resize(n);
    }
    _Bool ComposableRetainerVector_empty(ComposableRetainerVector* self)
    {
        return reinterpret_cast<ComposableRetainerVectorDef*>(self)->empty();
    }
    void ComposableRetainerVector_shrink_to_fit(ComposableRetainerVector* self)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->shrink_to_fit();
    }
    void ComposableRetainerVector_reserve(ComposableRetainerVector* self, int n)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->reserve(n);
    }
    void ComposableRetainerVector_swap(
        ComposableRetainerVector* self, ComposableRetainerVector* other)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->swap(
            *reinterpret_cast<ComposableRetainerVectorDef*>(other));
    }
    RetainerComposable*
    ComposableRetainerVector_at(ComposableRetainerVector* self, int pos)
    {
        ComposableRetainer obj =
            reinterpret_cast<ComposableRetainerVectorDef*>(self)->at(pos);
        return reinterpret_cast<RetainerComposable*>(
            new ComposableRetainer(obj));
    }
    void ComposableRetainerVector_push_back(
        ComposableRetainerVector* self, RetainerComposable* value)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->push_back(
            *reinterpret_cast<ComposableRetainer*>(value));
    }
    void ComposableRetainerVector_pop_back(ComposableRetainerVector* self)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->pop_back();
    }
    ComposableRetainerVectorIterator* ComposableRetainerVector_insert(
        ComposableRetainerVector*         self,
        ComposableRetainerVectorIterator* pos,
        RetainerComposable*               val)
    {
        ComposableRetainerVectorIteratorDef iter =
            reinterpret_cast<ComposableRetainerVectorDef*>(self)->insert(
                *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(pos),
                *reinterpret_cast<ComposableRetainer*>(val));
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(iter));
    }
    void ComposableRetainerVector_clear(ComposableRetainerVector* self)
    {
        reinterpret_cast<ComposableRetainerVectorDef*>(self)->clear();
    }
    ComposableRetainerVectorIterator* ComposableRetainerVector_erase(
        ComposableRetainerVector* self, ComposableRetainerVectorIterator* pos)
    {
        ComposableRetainerVectorIteratorDef iter =
            reinterpret_cast<ComposableRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(pos));
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(iter));
    }
    ComposableRetainerVectorIterator* ComposableRetainerVector_erase_range(
        ComposableRetainerVector*         self,
        ComposableRetainerVectorIterator* first,
        ComposableRetainerVectorIterator* last)
    {
        ComposableRetainerVectorIteratorDef iter =
            reinterpret_cast<ComposableRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(first),
                *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(last));
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(iter));
    }
    void ComposableRetainerVectorIterator_advance(
        ComposableRetainerVectorIterator* iter, int dist)
    {
        std::advance(
            *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(iter),
            dist);
    }
    ComposableRetainerVectorIterator* ComposableRetainerVectorIterator_next(
        ComposableRetainerVectorIterator* iter, int dist)
    {
        ComposableRetainerVectorIteratorDef it = std::next(
            *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(iter),
            dist);
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(it));
    }
    ComposableRetainerVectorIterator* ComposableRetainerVectorIterator_prev(
        ComposableRetainerVectorIterator* iter, int dist)
    {
        ComposableRetainerVectorIteratorDef it = std::prev(
            *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(iter),
            dist);
        return reinterpret_cast<ComposableRetainerVectorIterator*>(
            new ComposableRetainerVectorIteratorDef(it));
    }
    RetainerComposable* ComposableRetainerVectorIterator_value(
        ComposableRetainerVectorIterator* iter)
    {
        ComposableRetainer obj =
            **reinterpret_cast<ComposableRetainerVectorIteratorDef*>(iter);
        return reinterpret_cast<RetainerComposable*>(
            new ComposableRetainer(obj));
    }
    _Bool ComposableRetainerVectorIterator_equal(
        ComposableRetainerVectorIterator* lhs,
        ComposableRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(rhs);
    }
    _Bool ComposableRetainerVectorIterator_not_equal(
        ComposableRetainerVectorIterator* lhs,
        ComposableRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<ComposableRetainerVectorIteratorDef*>(rhs);
    }
    void ComposableRetainerVectorIterator_destroy(
        ComposableRetainerVectorIterator* self)
    {
        delete reinterpret_cast<ComposableRetainerVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif