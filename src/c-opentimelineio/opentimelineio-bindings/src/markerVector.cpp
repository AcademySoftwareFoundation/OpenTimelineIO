#include "copentimelineio/markerVector.h"
#include <opentimelineio/marker.h>
#include <vector>

typedef std::vector<OTIO_NS::Marker*>           MarkerVectorDef;
typedef std::vector<OTIO_NS::Marker*>::iterator MarkerVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    MarkerVector* MarkerVector_create()
    {
        return reinterpret_cast<MarkerVector*>(new MarkerVectorDef());
    }
    void MarkerVector_destroy(MarkerVector* self)
    {
        delete reinterpret_cast<MarkerVectorDef*>(self);
    }
    MarkerVectorIterator* MarkerVector_begin(MarkerVector* self)
    {
        MarkerVectorIteratorDef iter =
            reinterpret_cast<MarkerVectorDef*>(self)->begin();
        return reinterpret_cast<MarkerVectorIterator*>(
            new MarkerVectorIteratorDef(iter));
    }
    MarkerVectorIterator* MarkerVector_end(MarkerVector* self)
    {
        MarkerVectorIteratorDef iter =
            reinterpret_cast<MarkerVectorDef*>(self)->end();
        return reinterpret_cast<MarkerVectorIterator*>(
            new MarkerVectorIteratorDef(iter));
    }
    int MarkerVector_size(MarkerVector* self)
    {
        return reinterpret_cast<MarkerVectorDef*>(self)->size();
    }
    int MarkerVector_max_size(MarkerVector* self)
    {
        return reinterpret_cast<MarkerVectorDef*>(self)->max_size();
    }
    int MarkerVector_capacity(MarkerVector* self)
    {
        return reinterpret_cast<MarkerVectorDef*>(self)->capacity();
    }
    void MarkerVector_resize(MarkerVector* self, int n)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->resize(n);
    }
    _Bool MarkerVector_empty(MarkerVector* self)
    {
        return reinterpret_cast<MarkerVectorDef*>(self)->empty();
    }
    void MarkerVector_shrink_to_fit(MarkerVector* self)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->shrink_to_fit();
    }
    void MarkerVector_reserve(MarkerVector* self, int n)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->reserve(n);
    }
    void MarkerVector_swap(MarkerVector* self, MarkerVector* other)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->swap(
            *reinterpret_cast<MarkerVectorDef*>(other));
    }
    Marker* MarkerVector_at(MarkerVector* self, int pos)
    {
        return reinterpret_cast<Marker*>(
            reinterpret_cast<MarkerVectorDef*>(self)->at(pos));
    }
    void MarkerVector_push_back(MarkerVector* self, Marker* value)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->push_back(
            reinterpret_cast<OTIO_NS::Marker*>(value));
    }
    void MarkerVector_pop_back(MarkerVector* self)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->pop_back();
    }
    MarkerVectorIterator* MarkerVector_insert(
        MarkerVector* self, MarkerVectorIterator* pos, Marker* val)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->insert(
            *reinterpret_cast<MarkerVectorIteratorDef*>(pos),
            reinterpret_cast<OTIO_NS::Marker*>(val));
    }
    void MarkerVector_clear(MarkerVector* self)
    {
        reinterpret_cast<MarkerVectorDef*>(self)->clear();
    }
    MarkerVectorIterator*
    MarkerVector_erase(MarkerVector* self, MarkerVectorIterator* pos)
    {
        MarkerVectorIteratorDef iter =
            reinterpret_cast<MarkerVectorDef*>(self)->erase(
                *reinterpret_cast<MarkerVectorIteratorDef*>(pos));
        return reinterpret_cast<MarkerVectorIterator*>(
            new MarkerVectorIteratorDef(iter));
    }
    MarkerVectorIterator* MarkerVector_erase_range(
        MarkerVector*         self,
        MarkerVectorIterator* first,
        MarkerVectorIterator* last)
    {
        MarkerVectorIteratorDef iter =
            reinterpret_cast<MarkerVectorDef*>(self)->erase(
                *reinterpret_cast<MarkerVectorIteratorDef*>(first),
                *reinterpret_cast<MarkerVectorIteratorDef*>(last));
        return reinterpret_cast<MarkerVectorIterator*>(
            new MarkerVectorIteratorDef(iter));
    }
    void MarkerVectorIterator_advance(MarkerVectorIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<MarkerVectorIteratorDef*>(iter), dist);
    }
    MarkerVectorIterator*
    MarkerVectorIterator_next(MarkerVectorIterator* iter, int dist)
    {
        std::next(*reinterpret_cast<MarkerVectorIteratorDef*>(iter), dist);
    }
    MarkerVectorIterator*
    MarkerVectorIterator_prev(MarkerVectorIterator* iter, int dist)
    {
        std::prev(*reinterpret_cast<MarkerVectorIteratorDef*>(iter), dist);
    }
    Marker* MarkerVectorIterator_value(MarkerVectorIterator* iter)
    {
        OTIO_NS::Marker* obj =
            **reinterpret_cast<MarkerVectorIteratorDef*>(iter);
        return reinterpret_cast<Marker*>(obj);
    }
    _Bool MarkerVectorIterator_equal(
        MarkerVectorIterator* lhs, MarkerVectorIterator* rhs)
    {
        return *reinterpret_cast<MarkerVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<MarkerVectorIteratorDef*>(rhs);
    }
    _Bool MarkerVectorIterator_not_equal(
        MarkerVectorIterator* lhs, MarkerVectorIterator* rhs)
    {
        return *reinterpret_cast<MarkerVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<MarkerVectorIteratorDef*>(rhs);
    }
    void MarkerVectorIterator_destroy(MarkerVectorIterator* self)
    {
        delete reinterpret_cast<MarkerVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif
