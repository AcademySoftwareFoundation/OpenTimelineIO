#pragma once

#include "effect.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct EffectRetainerVectorIterator;
    typedef struct EffectRetainerVectorIterator EffectRetainerVectorIterator;
    struct EffectRetainerVector;
    typedef struct EffectRetainerVector EffectRetainerVector;
    EffectRetainerVector*               EffectRetainerVector_create();
    void EffectRetainerVector_destroy(EffectRetainerVector* self);
    EffectRetainerVectorIterator*
    EffectRetainerVector_begin(EffectRetainerVector* self);
    EffectRetainerVectorIterator*
          EffectRetainerVector_end(EffectRetainerVector* self);
    int   EffectRetainerVector_size(EffectRetainerVector* self);
    int   EffectRetainerVector_max_size(EffectRetainerVector* self);
    int   EffectRetainerVector_capacity(EffectRetainerVector* self);
    void  EffectRetainerVector_resize(EffectRetainerVector* self, int n);
    _Bool EffectRetainerVector_empty(EffectRetainerVector* self);
    void  EffectRetainerVector_shrink_to_fit(EffectRetainerVector* self);
    void  EffectRetainerVector_reserve(EffectRetainerVector* self, int n);
    void  EffectRetainerVector_swap(
         EffectRetainerVector* self, EffectRetainerVector* other);
    RetainerEffect*
         EffectRetainerVector_at(EffectRetainerVector* self, int pos);
    void EffectRetainerVector_push_back(
        EffectRetainerVector* self, RetainerEffect* value);
    void EffectRetainerVector_pop_back(EffectRetainerVector* self);
    EffectRetainerVectorIterator* EffectRetainerVector_insert(
        EffectRetainerVector*         self,
        EffectRetainerVectorIterator* pos,
        RetainerEffect*               val);
    void EffectRetainerVector_clear(EffectRetainerVector* self);
    EffectRetainerVectorIterator* EffectRetainerVector_erase(
        EffectRetainerVector* self, EffectRetainerVectorIterator* pos);
    EffectRetainerVectorIterator* EffectRetainerVector_erase_range(
        EffectRetainerVector*         self,
        EffectRetainerVectorIterator* first,
        EffectRetainerVectorIterator* last);
    void EffectRetainerVectorIterator_advance(
        EffectRetainerVectorIterator* iter, int dist);
    EffectRetainerVectorIterator* EffectRetainerVectorIterator_next(
        EffectRetainerVectorIterator* iter, int dist);
    EffectRetainerVectorIterator* EffectRetainerVectorIterator_prev(
        EffectRetainerVectorIterator* iter, int dist);
    RetainerEffect*
          EffectRetainerVectorIterator_value(EffectRetainerVectorIterator* iter);
    _Bool EffectRetainerVectorIterator_equal(
        EffectRetainerVectorIterator* lhs, EffectRetainerVectorIterator* rhs);
    _Bool EffectRetainerVectorIterator_not_equal(
        EffectRetainerVectorIterator* lhs, EffectRetainerVectorIterator* rhs);
    void
    EffectRetainerVectorIterator_destroy(EffectRetainerVectorIterator* self);
#ifdef __cplusplus
}
#endif
