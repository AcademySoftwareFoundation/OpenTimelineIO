#pragma once

#include "serializableObject.h"

#ifdef __cplusplus
extern "C"
{
#endif
    struct SerializableObjectVectorIterator;
    typedef struct SerializableObjectVectorIterator
        SerializableObjectVectorIterator;
    struct SerializableObjectVector;
    typedef struct SerializableObjectVector SerializableObjectVector;
    SerializableObjectVector*               SerializableObjectVector_create();
    void SerializableObjectVector_destroy(SerializableObjectVector* self);
    SerializableObjectVectorIterator*
    SerializableObjectVector_begin(SerializableObjectVector* self);
    SerializableObjectVectorIterator*
         SerializableObjectVector_end(SerializableObjectVector* self);
    int  SerializableObjectVector_size(SerializableObjectVector* self);
    int  SerializableObjectVector_max_size(SerializableObjectVector* self);
    int  SerializableObjectVector_capacity(SerializableObjectVector* self);
    void SerializableObjectVector_resize(SerializableObjectVector* self, int n);
    _Bool SerializableObjectVector_empty(SerializableObjectVector* self);
    void SerializableObjectVector_shrink_to_fit(SerializableObjectVector* self);
    void
         SerializableObjectVector_reserve(SerializableObjectVector* self, int n);
    void SerializableObjectVector_swap(
        SerializableObjectVector* self, SerializableObjectVector* other);
    SerializableObject*
         SerializableObjectVector_at(SerializableObjectVector* self, int pos);
    void SerializableObjectVector_push_back(
        SerializableObjectVector* self, SerializableObject* value);
    void SerializableObjectVector_pop_back(SerializableObjectVector* self);
    SerializableObjectVectorIterator* SerializableObjectVector_insert(
        SerializableObjectVector*         self,
        SerializableObjectVectorIterator* pos,
        SerializableObject*               val);
    void SerializableObjectVector_clear(SerializableObjectVector* self);
    SerializableObjectVectorIterator* SerializableObjectVector_erase(
        SerializableObjectVector* self, SerializableObjectVectorIterator* pos);
    SerializableObjectVectorIterator* SerializableObjectVector_erase_range(
        SerializableObjectVector*         self,
        SerializableObjectVectorIterator* first,
        SerializableObjectVectorIterator* last);
    void SerializableObjectVectorIterator_advance(
        SerializableObjectVectorIterator* iter, int dist);
    SerializableObjectVectorIterator* SerializableObjectVectorIterator_next(
        SerializableObjectVectorIterator* iter, int dist);
    SerializableObjectVectorIterator* SerializableObjectVectorIterator_prev(
        SerializableObjectVectorIterator* iter, int dist);
    SerializableObject* SerializableObjectVectorIterator_value(
        SerializableObjectVectorIterator* iter);
    _Bool SerializableObjectVectorIterator_equal(
        SerializableObjectVectorIterator* lhs,
        SerializableObjectVectorIterator* rhs);
    _Bool SerializableObjectVectorIterator_not_equal(
        SerializableObjectVectorIterator* lhs,
        SerializableObjectVectorIterator* rhs);
    void SerializableObjectVectorIterator_destroy(
        SerializableObjectVectorIterator* self);
#ifdef __cplusplus
}
#endif
