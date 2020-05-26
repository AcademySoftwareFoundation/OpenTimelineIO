#pragma once

#include "track.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct TrackVectorIterator;
    typedef struct TrackVectorIterator TrackVectorIterator;
    struct TrackVector;
    typedef struct TrackVector TrackVector;
    TrackVector*               TrackVector_create();
    void                       TrackVector_destroy(TrackVector* self);
    TrackVectorIterator*       TrackVector_begin(TrackVector* self);
    TrackVectorIterator*       TrackVector_end(TrackVector* self);
    int                        TrackVector_size(TrackVector* self);
    int                        TrackVector_max_size(TrackVector* self);
    int                        TrackVector_capacity(TrackVector* self);
    void                       TrackVector_resize(TrackVector* self, int n);
    _Bool                      TrackVector_empty(TrackVector* self);
    void                       TrackVector_shrink_to_fit(TrackVector* self);
    void                       TrackVector_reserve(TrackVector* self, int n);
    void   TrackVector_swap(TrackVector* self, TrackVector* other);
    Track* TrackVector_at(TrackVector* self, int pos);
    void   TrackVector_push_back(TrackVector* self, Track* value);
    void   TrackVector_pop_back(TrackVector* self);
    TrackVectorIterator*
         TrackVector_insert(TrackVector* self, TrackVectorIterator* pos, Track* val);
    void TrackVector_clear(TrackVector* self);
    TrackVectorIterator*
                         TrackVector_erase(TrackVector* self, TrackVectorIterator* pos);
    TrackVectorIterator* TrackVector_erase_range(
        TrackVector*         self,
        TrackVectorIterator* first,
        TrackVectorIterator* last);
    void TrackVectorIterator_advance(TrackVectorIterator* iter, int dist);
    TrackVectorIterator*
    TrackVectorIterator_next(TrackVectorIterator* iter, int dist);
    TrackVectorIterator*
           TrackVectorIterator_prev(TrackVectorIterator* iter, int dist);
    Track* TrackVectorIterator_value(TrackVectorIterator* iter);
    _Bool  TrackVectorIterator_equal(
         TrackVectorIterator* lhs, TrackVectorIterator* rhs);
    _Bool TrackVectorIterator_not_equal(
        TrackVectorIterator* lhs, TrackVectorIterator* rhs);
    void TrackVectorIterator_destroy(TrackVectorIterator* self);
#ifdef __cplusplus
}
#endif
