#pragma once

#include "serializableObject.h"
#include <vector>

#ifdef __cplusplus
extern "C"
{
#endif
    struct SerializableObjectRetainerVectorIterator;
    typedef struct SerializableObjectRetainerVectorIterator
        SerializableObjectRetainerVectorIterator;
    struct SerializableObjectRetainerVector;
    typedef struct SerializableObjectRetainerVector
                                      SerializableObjectRetainerVector;
    SerializableObjectRetainerVector* SerializableObjectRetainerVector_create();
    void                              SerializableObjectRetainerVector_destroy(
                                     SerializableObjectRetainerVector* self);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_begin(
        SerializableObjectRetainerVector* self);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_end(
        SerializableObjectRetainerVector* self);
    int SerializableObjectRetainerVector_size(
        SerializableObjectRetainerVector* self);
    int SerializableObjectRetainerVector_max_size(
        SerializableObjectRetainerVector* self);
    int SerializableObjectRetainerVector_capacity(
        SerializableObjectRetainerVector* self);
    void SerializableObjectRetainerVector_resize(
        SerializableObjectRetainerVector* self, int n);
    _Bool SerializableObjectRetainerVector_empty(
        SerializableObjectRetainerVector* self);
    void SerializableObjectRetainerVector_shrink_to_fit(
        SerializableObjectRetainerVector* self);
    void SerializableObjectRetainerVector_reserve(
        SerializableObjectRetainerVector* self, int n);
    void SerializableObjectRetainerVector_swap(
        SerializableObjectRetainerVector* self,
        SerializableObjectRetainerVector* other);
    RetainerSerializableObject* SerializableObjectRetainerVector_at(
        SerializableObjectRetainerVector* self, int pos);
    void SerializableObjectRetainerVector_push_back(
        SerializableObjectRetainerVector* self,
        RetainerSerializableObject*       value);
    void SerializableObjectRetainerVector_pop_back(
        SerializableObjectRetainerVector* self);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_insert(
        SerializableObjectRetainerVector*         self,
        SerializableObjectRetainerVectorIterator* pos,
        RetainerSerializableObject*               val);
    void SerializableObjectRetainerVector_clear(
        SerializableObjectRetainerVector* self);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_erase(
        SerializableObjectRetainerVector*         self,
        SerializableObjectRetainerVectorIterator* pos);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVector_erase_range(
        SerializableObjectRetainerVector*         self,
        SerializableObjectRetainerVectorIterator* first,
        SerializableObjectRetainerVectorIterator* last);
    void SerializableObjectRetainerVectorIterator_advance(
        SerializableObjectRetainerVectorIterator* iter, int dist);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVectorIterator_next(
        SerializableObjectRetainerVectorIterator* iter, int dist);
    SerializableObjectRetainerVectorIterator*
    SerializableObjectRetainerVectorIterator_prev(
        SerializableObjectRetainerVectorIterator* iter, int dist);
    RetainerSerializableObject* SerializableObjectRetainerVectorIterator_value(
        SerializableObjectRetainerVectorIterator* iter);
    _Bool SerializableObjectRetainerVectorIterator_equal(
        SerializableObjectRetainerVectorIterator* lhs,
        SerializableObjectRetainerVectorIterator* rhs);
    _Bool SerializableObjectRetainerVectorIterator_not_equal(
        SerializableObjectRetainerVectorIterator* lhs,
        SerializableObjectRetainerVectorIterator* rhs);
    void SerializableObjectRetainerVectorIterator_destroy(
        SerializableObjectRetainerVectorIterator* self);
#ifdef __cplusplus
}
#endif
