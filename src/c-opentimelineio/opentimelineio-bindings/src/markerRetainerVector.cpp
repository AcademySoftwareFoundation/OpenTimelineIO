#include "copentimelineio/markerRetainerVector.h"
#include <opentimelineio/marker.h>
#include <vector>

typedef std::vector<OTIO_NS::Marker::Retainer<OTIO_NS::Marker>>
    MarkerRetainerVectorDef;
typedef std::vector<OTIO_NS::Marker::Retainer<OTIO_NS::Marker>>::iterator
                                                               MarkerRetainerVectorIteratorDef;
typedef OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker> MarkerRetainer;

#ifdef __cplusplus
extern "C"
{
#endif
    MarkerRetainerVector* MarkerRetainerVector_create()
    {
        return reinterpret_cast<MarkerRetainerVector*>(
            new MarkerRetainerVectorDef());
    }
    void MarkerRetainerVector_destroy(MarkerRetainerVector* self)
    {
        delete reinterpret_cast<MarkerRetainerVectorDef*>(self);
    }
    MarkerRetainerVectorIterator*
    MarkerRetainerVector_begin(MarkerRetainerVector* self)
    {
        MarkerRetainerVectorIteratorDef iter =
            reinterpret_cast<MarkerRetainerVectorDef*>(self)->begin();
        return reinterpret_cast<MarkerRetainerVectorIterator*>(
            new MarkerRetainerVectorIteratorDef(iter));
    }
    MarkerRetainerVectorIterator*
    MarkerRetainerVector_end(MarkerRetainerVector* self)
    {
        MarkerRetainerVectorIteratorDef iter =
            reinterpret_cast<MarkerRetainerVectorDef*>(self)->end();
        return reinterpret_cast<MarkerRetainerVectorIterator*>(
            new MarkerRetainerVectorIteratorDef(iter));
    }
    int MarkerRetainerVector_size(MarkerRetainerVector* self)
    {
        return reinterpret_cast<MarkerRetainerVectorDef*>(self)->size();
    }
    int MarkerRetainerVector_max_size(MarkerRetainerVector* self)
    {
        return reinterpret_cast<MarkerRetainerVectorDef*>(self)->max_size();
    }
    int MarkerRetainerVector_capacity(MarkerRetainerVector* self)
    {
        return reinterpret_cast<MarkerRetainerVectorDef*>(self)->capacity();
    }
    void MarkerRetainerVector_resize(MarkerRetainerVector* self, int n)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->resize(n);
    }
    _Bool MarkerRetainerVector_empty(MarkerRetainerVector* self)
    {
        return reinterpret_cast<MarkerRetainerVectorDef*>(self)->empty();
    }
    void MarkerRetainerVector_shrink_to_fit(MarkerRetainerVector* self)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->shrink_to_fit();
    }
    void MarkerRetainerVector_reserve(MarkerRetainerVector* self, int n)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->reserve(n);
    }
    void MarkerRetainerVector_swap(
        MarkerRetainerVector* self, MarkerRetainerVector* other)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->swap(
            *reinterpret_cast<MarkerRetainerVectorDef*>(other));
    }
    RetainerMarker* MarkerRetainerVector_at(MarkerRetainerVector* self, int pos)
    {
        MarkerRetainer obj =
            reinterpret_cast<MarkerRetainerVectorDef*>(self)->at(pos);
        return reinterpret_cast<RetainerMarker*>(new MarkerRetainer(obj));
    }
    void MarkerRetainerVector_push_back(
        MarkerRetainerVector* self, RetainerMarker* value)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->push_back(
            *reinterpret_cast<MarkerRetainer*>(value));
    }
    void MarkerRetainerVector_pop_back(MarkerRetainerVector* self)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->pop_back();
    }
    MarkerRetainerVectorIterator* MarkerRetainerVector_insert(
        MarkerRetainerVector*         self,
        MarkerRetainerVectorIterator* pos,
        RetainerMarker*               val)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->insert(
            *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(pos),
            *reinterpret_cast<MarkerRetainer*>(val));
    }
    void MarkerRetainerVector_clear(MarkerRetainerVector* self)
    {
        reinterpret_cast<MarkerRetainerVectorDef*>(self)->clear();
    }
    MarkerRetainerVectorIterator* MarkerRetainerVector_erase(
        MarkerRetainerVector* self, MarkerRetainerVectorIterator* pos)
    {
        MarkerRetainerVectorIteratorDef iter =
            reinterpret_cast<MarkerRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(pos));
        return reinterpret_cast<MarkerRetainerVectorIterator*>(
            new MarkerRetainerVectorIteratorDef(iter));
    }
    MarkerRetainerVectorIterator* MarkerRetainerVector_erase_range(
        MarkerRetainerVector*         self,
        MarkerRetainerVectorIterator* first,
        MarkerRetainerVectorIterator* last)
    {
        MarkerRetainerVectorIteratorDef iter =
            reinterpret_cast<MarkerRetainerVectorDef*>(self)->erase(
                *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(first),
                *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(last));
        return reinterpret_cast<MarkerRetainerVectorIterator*>(
            new MarkerRetainerVectorIteratorDef(iter));
    }
    void MarkerRetainerVectorIterator_advance(
        MarkerRetainerVectorIterator* iter, int dist)
    {
        std::advance(
            *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(iter), dist);
    }
    MarkerRetainerVectorIterator* MarkerRetainerVectorIterator_next(
        MarkerRetainerVectorIterator* iter, int dist)
    {
        std::next(
            *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(iter), dist);
    }
    MarkerRetainerVectorIterator* MarkerRetainerVectorIterator_prev(
        MarkerRetainerVectorIterator* iter, int dist)
    {
        std::prev(
            *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(iter), dist);
    }
    RetainerMarker*
    MarkerRetainerVectorIterator_value(MarkerRetainerVectorIterator* iter)
    {
        MarkerRetainer obj =
            **reinterpret_cast<MarkerRetainerVectorIteratorDef*>(iter);
        return reinterpret_cast<RetainerMarker*>(new MarkerRetainer(obj));
    }
    _Bool MarkerRetainerVectorIterator_equal(
        MarkerRetainerVectorIterator* lhs, MarkerRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(rhs);
    }
    _Bool MarkerRetainerVectorIterator_not_equal(
        MarkerRetainerVectorIterator* lhs, MarkerRetainerVectorIterator* rhs)
    {
        return *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<MarkerRetainerVectorIteratorDef*>(rhs);
    }
    void
    MarkerRetainerVectorIterator_destroy(MarkerRetainerVectorIterator* self)
    {
        delete reinterpret_cast<MarkerRetainerVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif