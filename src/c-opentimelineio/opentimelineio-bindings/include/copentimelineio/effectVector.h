#pragma once

#include "effect.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct EffectVectorIterator;
    typedef struct EffectVectorIterator EffectVectorIterator;
    struct EffectVector;
    typedef struct EffectVector EffectVector;
    EffectVector*               EffectVector_create();
    void                        EffectVector_destroy(EffectVector* self);
    EffectVectorIterator*       EffectVector_begin(EffectVector* self);
    EffectVectorIterator*       EffectVector_end(EffectVector* self);
    int                         EffectVector_size(EffectVector* self);
    int                         EffectVector_max_size(EffectVector* self);
    int                         EffectVector_capacity(EffectVector* self);
    void                        EffectVector_resize(EffectVector* self, int n);
    _Bool                       EffectVector_empty(EffectVector* self);
    void                        EffectVector_shrink_to_fit(EffectVector* self);
    void                        EffectVector_reserve(EffectVector* self, int n);
    void    EffectVector_swap(EffectVector* self, EffectVector* other);
    Effect* EffectVector_at(EffectVector* self, int pos);
    void    EffectVector_push_back(EffectVector* self, Effect* value);
    void    EffectVector_pop_back(EffectVector* self);
    EffectVectorIterator* EffectVector_insert(
        EffectVector* self, EffectVectorIterator* pos, Effect* val);
    void EffectVector_clear(EffectVector* self);
    EffectVectorIterator*
                          EffectVector_erase(EffectVector* self, EffectVectorIterator* pos);
    EffectVectorIterator* EffectVector_erase_range(
        EffectVector*         self,
        EffectVectorIterator* first,
        EffectVectorIterator* last);
    void EffectVectorIterator_advance(EffectVectorIterator* iter, int dist);
    EffectVectorIterator*
    EffectVectorIterator_next(EffectVectorIterator* iter, int dist);
    EffectVectorIterator*
            EffectVectorIterator_prev(EffectVectorIterator* iter, int dist);
    Effect* EffectVectorIterator_value(EffectVectorIterator* iter);
    _Bool   EffectVectorIterator_equal(
          EffectVectorIterator* lhs, EffectVectorIterator* rhs);
    _Bool EffectVectorIterator_not_equal(
        EffectVectorIterator* lhs, EffectVectorIterator* rhs);
    void EffectVectorIterator_destroy(EffectVectorIterator* self);
#ifdef __cplusplus
}
#endif
