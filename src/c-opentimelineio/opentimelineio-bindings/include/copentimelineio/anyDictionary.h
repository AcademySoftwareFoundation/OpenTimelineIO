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
    struct MutationStamp;
    typedef struct MutationStamp MutationStamp;
    AnyDictionary*               AnyDictionary_create();
    void                         AnyDictionary_destroy(AnyDictionary* self);
    void                         AnyDictionary_clear(AnyDictionary* self);
    AnyDictionaryIterator*       AnyDictionary_begin(AnyDictionary* self);
    AnyDictionaryIterator*       AnyDictionary_end(AnyDictionary* self);
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
                   AnyDictionary_insert(AnyDictionary* self, const char* key, Any* anyObj);
    MutationStamp* MutationStamp_create(AnyDictionary* d);
    void           MutationStamp_destroy(MutationStamp* self);
    MutationStamp*
         AnyDictionary_get_or_create_mutation_stamp(AnyDictionary* self);
    void AnyDictionaryIterator_advance(AnyDictionaryIterator* iter, int dist);
    AnyDictionaryIterator*
    AnyDictionaryIterator_next(AnyDictionaryIterator* iter, int dist);
    AnyDictionaryIterator*
          AnyDictionaryIterator_prev(AnyDictionaryIterator* iter, int dist);
    _Bool AnyDictionaryIterator_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs);
    _Bool AnyDictionaryIterator_not_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs);
    void AnyDictionaryIterator_destroy(AnyDictionaryIterator* self);
#ifdef __cplusplus
}
#endif