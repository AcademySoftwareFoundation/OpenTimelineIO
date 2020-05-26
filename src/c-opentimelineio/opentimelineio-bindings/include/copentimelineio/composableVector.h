#pragma once

#include "composable.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct ComposableVectorIterator;
    typedef struct ComposableVectorIterator ComposableVectorIterator;
    struct ComposableVector;
    typedef struct ComposableVector ComposableVector;
    ComposableVector*               ComposableVector_create();
    void                      ComposableVector_destroy(ComposableVector* self);
    ComposableVectorIterator* ComposableVector_begin(ComposableVector* self);
    ComposableVectorIterator* ComposableVector_end(ComposableVector* self);
    int                       ComposableVector_size(ComposableVector* self);
    int                       ComposableVector_max_size(ComposableVector* self);
    int                       ComposableVector_capacity(ComposableVector* self);
    void  ComposableVector_resize(ComposableVector* self, int n);
    _Bool ComposableVector_empty(ComposableVector* self);
    void  ComposableVector_shrink_to_fit(ComposableVector* self);
    void  ComposableVector_reserve(ComposableVector* self, int n);
    void ComposableVector_swap(ComposableVector* self, ComposableVector* other);
    Composable* ComposableVector_at(ComposableVector* self, int pos);
    void ComposableVector_push_back(ComposableVector* self, Composable* value);
    void ComposableVector_pop_back(ComposableVector* self);
    ComposableVectorIterator* ComposableVector_insert(
        ComposableVector* self, ComposableVectorIterator* pos, Composable* val);
    void                      ComposableVector_clear(ComposableVector* self);
    ComposableVectorIterator* ComposableVector_erase(
        ComposableVector* self, ComposableVectorIterator* pos);
    ComposableVectorIterator* ComposableVector_erase_range(
        ComposableVector*         self,
        ComposableVectorIterator* first,
        ComposableVectorIterator* last);
    void
    ComposableVectorIterator_advance(ComposableVectorIterator* iter, int dist);
    ComposableVectorIterator*
    ComposableVectorIterator_next(ComposableVectorIterator* iter, int dist);
    ComposableVectorIterator*
                ComposableVectorIterator_prev(ComposableVectorIterator* iter, int dist);
    Composable* ComposableVectorIterator_value(ComposableVectorIterator* iter);
    _Bool       ComposableVectorIterator_equal(
              ComposableVectorIterator* lhs, ComposableVectorIterator* rhs);
    _Bool ComposableVectorIterator_not_equal(
        ComposableVectorIterator* lhs, ComposableVectorIterator* rhs);
    void ComposableVectorIterator_destroy(ComposableVectorIterator* self);
#ifdef __cplusplus
}
#endif
