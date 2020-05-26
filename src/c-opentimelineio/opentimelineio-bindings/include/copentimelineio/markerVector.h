#pragma once

#include "marker.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct MarkerVectorIterator;
    typedef struct MarkerVectorIterator MarkerVectorIterator;
    struct MarkerVector;
    typedef struct MarkerVector MarkerVector;
    MarkerVector*               MarkerVector_create();
    void                        MarkerVector_destroy(MarkerVector* self);
    MarkerVectorIterator*       MarkerVector_begin(MarkerVector* self);
    MarkerVectorIterator*       MarkerVector_end(MarkerVector* self);
    int                         MarkerVector_size(MarkerVector* self);
    int                         MarkerVector_max_size(MarkerVector* self);
    int                         MarkerVector_capacity(MarkerVector* self);
    void                        MarkerVector_resize(MarkerVector* self, int n);
    _Bool                       MarkerVector_empty(MarkerVector* self);
    void                        MarkerVector_shrink_to_fit(MarkerVector* self);
    void                        MarkerVector_reserve(MarkerVector* self, int n);
    void    MarkerVector_swap(MarkerVector* self, MarkerVector* other);
    Marker* MarkerVector_at(MarkerVector* self, int pos);
    void    MarkerVector_push_back(MarkerVector* self, Marker* value);
    void    MarkerVector_pop_back(MarkerVector* self);
    MarkerVectorIterator* MarkerVector_insert(
        MarkerVector* self, MarkerVectorIterator* pos, Marker* val);
    void MarkerVector_clear(MarkerVector* self);
    MarkerVectorIterator*
                          MarkerVector_erase(MarkerVector* self, MarkerVectorIterator* pos);
    MarkerVectorIterator* MarkerVector_erase_range(
        MarkerVector*         self,
        MarkerVectorIterator* first,
        MarkerVectorIterator* last);
    void MarkerVectorIterator_advance(MarkerVectorIterator* iter, int dist);
    MarkerVectorIterator*
    MarkerVectorIterator_next(MarkerVectorIterator* iter, int dist);
    MarkerVectorIterator*
            MarkerVectorIterator_prev(MarkerVectorIterator* iter, int dist);
    Marker* MarkerVectorIterator_value(MarkerVectorIterator* iter);
    _Bool   MarkerVectorIterator_equal(
          MarkerVectorIterator* lhs, MarkerVectorIterator* rhs);
    _Bool MarkerVectorIterator_not_equal(
        MarkerVectorIterator* lhs, MarkerVectorIterator* rhs);
    void MarkerVectorIterator_destroy(MarkerVectorIterator* self);
#ifdef __cplusplus
}
#endif
