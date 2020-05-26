#pragma once

#include "marker.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct MarkerRetainerVectorIterator;
    typedef struct MarkerRetainerVectorIterator MarkerRetainerVectorIterator;
    struct MarkerRetainerVector;
    typedef struct MarkerRetainerVector MarkerRetainerVector;
    MarkerRetainerVector*               MarkerRetainerVector_create();
    void MarkerRetainerVector_destroy(MarkerRetainerVector* self);
    MarkerRetainerVectorIterator*
    MarkerRetainerVector_begin(MarkerRetainerVector* self);
    MarkerRetainerVectorIterator*
          MarkerRetainerVector_end(MarkerRetainerVector* self);
    int   MarkerRetainerVector_size(MarkerRetainerVector* self);
    int   MarkerRetainerVector_max_size(MarkerRetainerVector* self);
    int   MarkerRetainerVector_capacity(MarkerRetainerVector* self);
    void  MarkerRetainerVector_resize(MarkerRetainerVector* self, int n);
    _Bool MarkerRetainerVector_empty(MarkerRetainerVector* self);
    void  MarkerRetainerVector_shrink_to_fit(MarkerRetainerVector* self);
    void  MarkerRetainerVector_reserve(MarkerRetainerVector* self, int n);
    void  MarkerRetainerVector_swap(
         MarkerRetainerVector* self, MarkerRetainerVector* other);
    RetainerMarker*
         MarkerRetainerVector_at(MarkerRetainerVector* self, int pos);
    void MarkerRetainerVector_push_back(
        MarkerRetainerVector* self, RetainerMarker* value);
    void MarkerRetainerVector_pop_back(MarkerRetainerVector* self);
    MarkerRetainerVectorIterator* MarkerRetainerVector_insert(
        MarkerRetainerVector*         self,
        MarkerRetainerVectorIterator* pos,
        RetainerMarker*               val);
    void MarkerRetainerVector_clear(MarkerRetainerVector* self);
    MarkerRetainerVectorIterator* MarkerRetainerVector_erase(
        MarkerRetainerVector* self, MarkerRetainerVectorIterator* pos);
    MarkerRetainerVectorIterator* MarkerRetainerVector_erase_range(
        MarkerRetainerVector*         self,
        MarkerRetainerVectorIterator* first,
        MarkerRetainerVectorIterator* last);
    void MarkerRetainerVectorIterator_advance(
        MarkerRetainerVectorIterator* iter, int dist);
    MarkerRetainerVectorIterator* MarkerRetainerVectorIterator_next(
        MarkerRetainerVectorIterator* iter, int dist);
    MarkerRetainerVectorIterator* MarkerRetainerVectorIterator_prev(
        MarkerRetainerVectorIterator* iter, int dist);
    RetainerMarker*
          MarkerRetainerVectorIterator_value(MarkerRetainerVectorIterator* iter);
    _Bool MarkerRetainerVectorIterator_equal(
        MarkerRetainerVectorIterator* lhs, MarkerRetainerVectorIterator* rhs);
    _Bool MarkerRetainerVectorIterator_not_equal(
        MarkerRetainerVectorIterator* lhs, MarkerRetainerVectorIterator* rhs);
    void
    MarkerRetainerVectorIterator_destroy(MarkerRetainerVectorIterator* self);
#ifdef __cplusplus
}
#endif
