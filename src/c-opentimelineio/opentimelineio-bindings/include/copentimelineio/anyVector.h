#pragma once

#include "any.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct AnyVectorIterator;
    typedef struct AnyVectorIterator AnyVectorIterator;
    struct AnyVector;
    typedef struct AnyVector AnyVector;
    struct AnyVectorMutationStamp;
    typedef struct AnyVectorMutationStamp AnyVectorMutationStamp;
    AnyVector*                            AnyVector_create();
    void                                  AnyVector_destroy(AnyVector* self);
    AnyVectorIterator*                    AnyVector_begin(AnyVector* self);
    AnyVectorIterator*                    AnyVector_end(AnyVector* self);
    int                                   AnyVector_size(AnyVector* self);
    int                                   AnyVector_max_size(AnyVector* self);
    int                                   AnyVector_capacity(AnyVector* self);
    void  AnyVector_resize(AnyVector* self, int n);
    _Bool AnyVector_empty(AnyVector* self);
    void  AnyVector_shrink_to_fit(AnyVector* self);
    void  AnyVector_reserve(AnyVector* self, int n);
    void  AnyVector_swap(AnyVector* self, AnyVector* other);
    Any*  AnyVector_at(AnyVector* self, int pos);
    void  AnyVector_push_back(AnyVector* self, Any* value);
    void  AnyVector_pop_back(AnyVector* self);
    AnyVectorIterator*
                       AnyVector_insert(AnyVector* self, AnyVectorIterator* pos, Any* val);
    void               AnyVector_clear(AnyVector* self);
    AnyVectorIterator* AnyVector_erase(AnyVector* self, AnyVectorIterator* pos);
    AnyVectorIterator* AnyVector_erase_range(
        AnyVector* self, AnyVectorIterator* first, AnyVectorIterator* last);
    void AnyVectorIterator_advance(AnyVectorIterator* iter, int dist);
    AnyVectorIterator*
    AnyVectorIterator_next(AnyVectorIterator* iter, int dist);
    AnyVectorIterator*
    AnyVectorIterator_prev(AnyVectorIterator* iter, int dist);
    Any* AnyVectorIterator_value(AnyVectorIterator* iter);
    _Bool
    AnyVectorIterator_equal(AnyVectorIterator* lhs, AnyVectorIterator* rhs);
    _Bool
                            AnyVectorIterator_not_equal(AnyVectorIterator* lhs, AnyVectorIterator* rhs);
    void                    AnyVectorIterator_destroy(AnyVectorIterator* self);
    AnyVectorMutationStamp* MutationStamp_create(AnyVector* v);
    void                    MutationStamp_destroy(AnyVectorMutationStamp* self);
    AnyVectorMutationStamp*
    AnyVector_get_or_create_mutation_stamp(AnyVector* self);
#ifdef __cplusplus
}
#endif
