#include "copentimelineio/trackVector.h"
#include <opentimelineio/track.h>
#include <vector>

typedef std::vector<OTIO_NS::Track*>           TrackVectorDef;
typedef std::vector<OTIO_NS::Track*>::iterator TrackVectorIteratorDef;

#ifdef __cplusplus
extern "C"
{
#endif
    TrackVector* TrackVector_create()
    {
        return reinterpret_cast<TrackVector*>(new TrackVectorDef());
    }
    void TrackVector_destroy(TrackVector* self)
    {
        delete reinterpret_cast<TrackVectorDef*>(self);
    }
    TrackVectorIterator* TrackVector_begin(TrackVector* self)
    {
        TrackVectorIteratorDef iter =
            reinterpret_cast<TrackVectorDef*>(self)->begin();
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(iter));
    }
    TrackVectorIterator* TrackVector_end(TrackVector* self)
    {
        TrackVectorIteratorDef iter =
            reinterpret_cast<TrackVectorDef*>(self)->end();
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(iter));
    }
    int TrackVector_size(TrackVector* self)
    {
        return reinterpret_cast<TrackVectorDef*>(self)->size();
    }
    int TrackVector_max_size(TrackVector* self)
    {
        return reinterpret_cast<TrackVectorDef*>(self)->max_size();
    }
    int TrackVector_capacity(TrackVector* self)
    {
        return reinterpret_cast<TrackVectorDef*>(self)->capacity();
    }
    void TrackVector_resize(TrackVector* self, int n)
    {
        reinterpret_cast<TrackVectorDef*>(self)->resize(n);
    }
    _Bool TrackVector_empty(TrackVector* self)
    {
        return reinterpret_cast<TrackVectorDef*>(self)->empty();
    }
    void TrackVector_shrink_to_fit(TrackVector* self)
    {
        reinterpret_cast<TrackVectorDef*>(self)->shrink_to_fit();
    }
    void TrackVector_reserve(TrackVector* self, int n)
    {
        reinterpret_cast<TrackVectorDef*>(self)->reserve(n);
    }
    void TrackVector_swap(TrackVector* self, TrackVector* other)
    {
        reinterpret_cast<TrackVectorDef*>(self)->swap(
            *reinterpret_cast<TrackVectorDef*>(other));
    }
    Track* TrackVector_at(TrackVector* self, int pos)
    {
        return reinterpret_cast<Track*>(
            reinterpret_cast<TrackVectorDef*>(self)->at(pos));
    }
    void TrackVector_push_back(TrackVector* self, Track* value)
    {
        reinterpret_cast<TrackVectorDef*>(self)->push_back(
            reinterpret_cast<OTIO_NS::Track*>(value));
    }
    void TrackVector_pop_back(TrackVector* self)
    {
        reinterpret_cast<TrackVectorDef*>(self)->pop_back();
    }
    TrackVectorIterator*
    TrackVector_insert(TrackVector* self, TrackVectorIterator* pos, Track* val)
    {
        TrackVectorIteratorDef iter =
            reinterpret_cast<TrackVectorDef*>(self)->insert(
                *reinterpret_cast<TrackVectorIteratorDef*>(pos),
                reinterpret_cast<OTIO_NS::Track*>(val));
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(iter));
    }
    void TrackVector_clear(TrackVector* self)
    {
        reinterpret_cast<TrackVectorDef*>(self)->clear();
    }
    TrackVectorIterator*
    TrackVector_erase(TrackVector* self, TrackVectorIterator* pos)
    {
        TrackVectorIteratorDef iter =
            reinterpret_cast<TrackVectorDef*>(self)->erase(
                *reinterpret_cast<TrackVectorIteratorDef*>(pos));
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(iter));
    }
    TrackVectorIterator* TrackVector_erase_range(
        TrackVector*         self,
        TrackVectorIterator* first,
        TrackVectorIterator* last)
    {
        TrackVectorIteratorDef iter =
            reinterpret_cast<TrackVectorDef*>(self)->erase(
                *reinterpret_cast<TrackVectorIteratorDef*>(first),
                *reinterpret_cast<TrackVectorIteratorDef*>(last));
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(iter));
    }
    void TrackVectorIterator_advance(TrackVectorIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<TrackVectorIteratorDef*>(iter), dist);
    }
    TrackVectorIterator*
    TrackVectorIterator_next(TrackVectorIterator* iter, int dist)
    {
        TrackVectorIteratorDef it =
            std::next(*reinterpret_cast<TrackVectorIteratorDef*>(iter), dist);
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(it));
    }
    TrackVectorIterator*
    TrackVectorIterator_prev(TrackVectorIterator* iter, int dist)
    {
        TrackVectorIteratorDef it =
            std::prev(*reinterpret_cast<TrackVectorIteratorDef*>(iter), dist);
        return reinterpret_cast<TrackVectorIterator*>(
            new TrackVectorIteratorDef(it));
    }
    Track* TrackVectorIterator_value(TrackVectorIterator* iter)
    {
        OTIO_NS::Track* obj = **reinterpret_cast<TrackVectorIteratorDef*>(iter);
        return reinterpret_cast<Track*>(obj);
    }
    _Bool TrackVectorIterator_equal(
        TrackVectorIterator* lhs, TrackVectorIterator* rhs)
    {
        return *reinterpret_cast<TrackVectorIteratorDef*>(lhs) ==
               *reinterpret_cast<TrackVectorIteratorDef*>(rhs);
    }
    _Bool TrackVectorIterator_not_equal(
        TrackVectorIterator* lhs, TrackVectorIterator* rhs)
    {
        return *reinterpret_cast<TrackVectorIteratorDef*>(lhs) !=
               *reinterpret_cast<TrackVectorIteratorDef*>(rhs);
    }
    void TrackVectorIterator_destroy(TrackVectorIterator* self)
    {
        delete reinterpret_cast<TrackVectorIteratorDef*>(self);
    }
#ifdef __cplusplus
}
#endif
