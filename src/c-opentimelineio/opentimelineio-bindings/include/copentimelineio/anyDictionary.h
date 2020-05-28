#pragma once
#include "any.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif

    struct AnyDictionaryIterator;
    typedef struct AnyDictionaryIterator AnyDictionaryIterator;
    struct AnyDictionary;
    typedef struct AnyDictionary AnyDictionary;
    struct AnyDictionaryMutationStamp;
    typedef struct AnyDictionaryMutationStamp AnyDictionaryMutationStamp;
    AnyDictionary*                            AnyDictionary_create();
    void                   AnyDictionary_destroy(AnyDictionary* self);
    void                   AnyDictionary_clear(AnyDictionary* self);
    AnyDictionaryIterator* AnyDictionary_begin(AnyDictionary* self);
    AnyDictionaryIterator* AnyDictionary_end(AnyDictionary* self);
    void AnyDictionary_swap(AnyDictionary* self, AnyDictionary* other);
    AnyDictionaryIterator*
                           AnyDictionary_erase(AnyDictionary* self, AnyDictionaryIterator* pos);
    AnyDictionaryIterator* AnyDictionary_erase_range(
        AnyDictionary*         self,
        AnyDictionaryIterator* first,
        AnyDictionaryIterator* last);
    int   AnyDictionary_erase_key(AnyDictionary* self, const char* key);
    int   AnyDictionary_size(AnyDictionary* self);
    int   AnyDictionary_max_size(AnyDictionary* self);
    _Bool AnyDictionary_empty(AnyDictionary* self);
    AnyDictionaryIterator*
    AnyDictionary_find(AnyDictionary* self, const char* key);
    AnyDictionaryIterator*
         AnyDictionary_insert(AnyDictionary* self, const char* key, Any* anyObj);
    void AnyDictionaryIterator_advance(AnyDictionaryIterator* iter, int dist);
    AnyDictionaryIterator*
    AnyDictionaryIterator_next(AnyDictionaryIterator* iter, int dist);
    AnyDictionaryIterator*
                AnyDictionaryIterator_prev(AnyDictionaryIterator* iter, int dist);
    const char* AnyDictionaryIterator_key(AnyDictionaryIterator* iter);
    Any*        AnyDictionaryIterator_value(AnyDictionaryIterator* iter);
    _Bool       AnyDictionaryIterator_equal(
              AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs);
    _Bool AnyDictionaryIterator_not_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs);
    void AnyDictionaryIterator_destroy(AnyDictionaryIterator* self);
    AnyDictionaryMutationStamp*
         AnyDictionaryMutationStamp_create(AnyDictionary* d);
    void AnyDictionaryMutationStamp_destroy(AnyDictionaryMutationStamp* self);
    AnyDictionaryMutationStamp*
    AnyDictionary_get_or_create_mutation_stamp(AnyDictionary* self);
#ifdef __cplusplus
}
#endif