#pragma once

#include "composable.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct ComposableRetainerVectorIterator;
    typedef struct ComposableRetainerVectorIterator
        ComposableRetainerVectorIterator;
    struct ComposableRetainerVector;
    typedef struct ComposableRetainerVector ComposableRetainerVector;

    ComposableRetainerVector* ComposableRetainerVector_create();
    void ComposableRetainerVector_destroy(ComposableRetainerVector* self);
    ComposableRetainerVectorIterator*
    ComposableRetainerVector_begin(ComposableRetainerVector* self);
    ComposableRetainerVectorIterator*
         ComposableRetainerVector_end(ComposableRetainerVector* self);
    int  ComposableRetainerVector_size(ComposableRetainerVector* self);
    int  ComposableRetainerVector_max_size(ComposableRetainerVector* self);
    int  ComposableRetainerVector_capacity(ComposableRetainerVector* self);
    void ComposableRetainerVector_resize(ComposableRetainerVector* self, int n);
    _Bool ComposableRetainerVector_empty(ComposableRetainerVector* self);
    void ComposableRetainerVector_shrink_to_fit(ComposableRetainerVector* self);
    void
         ComposableRetainerVector_reserve(ComposableRetainerVector* self, int n);
    void ComposableRetainerVector_swap(
        ComposableRetainerVector* self, ComposableRetainerVector* other);
    RetainerComposable*
         ComposableRetainerVector_at(ComposableRetainerVector* self, int pos);
    void ComposableRetainerVector_push_back(
        ComposableRetainerVector* self, RetainerComposable* value);
    void ComposableRetainerVector_pop_back(ComposableRetainerVector* self);
    ComposableRetainerVectorIterator* ComposableRetainerVector_insert(
        ComposableRetainerVector*         self,
        ComposableRetainerVectorIterator* pos,
        RetainerComposable*               val);
    void ComposableRetainerVector_clear(ComposableRetainerVector* self);
    ComposableRetainerVectorIterator* ComposableRetainerVector_erase(
        ComposableRetainerVector* self, ComposableRetainerVectorIterator* pos);
    ComposableRetainerVectorIterator* ComposableRetainerVector_erase_range(
        ComposableRetainerVector*         self,
        ComposableRetainerVectorIterator* first,
        ComposableRetainerVectorIterator* last);
    void ComposableRetainerVectorIterator_advance(
        ComposableRetainerVectorIterator* iter, int dist);
    ComposableRetainerVectorIterator* ComposableRetainerVectorIterator_next(
        ComposableRetainerVectorIterator* iter, int dist);
    ComposableRetainerVectorIterator* ComposableRetainerVectorIterator_prev(
        ComposableRetainerVectorIterator* iter, int dist);
    RetainerComposable* ComposableRetainerVectorIterator_value(
        ComposableRetainerVectorIterator* iter);
    _Bool ComposableRetainerVectorIterator_equal(
        ComposableRetainerVectorIterator* lhs,
        ComposableRetainerVectorIterator* rhs);
    _Bool ComposableRetainerVectorIterator_not_equal(
        ComposableRetainerVectorIterator* lhs,
        ComposableRetainerVectorIterator* rhs);
    void ComposableRetainerVectorIterator_destroy(
        ComposableRetainerVectorIterator* self);
#ifdef __cplusplus
}
#endif
