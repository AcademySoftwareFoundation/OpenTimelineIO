#include "copentimelineio/anyVector.h"
#include <opentimelineio/anyVector.h>
#include <opentimelineio/version.h>

typedef std::vector<OTIO_NS::any>::iterator VectorIterator;

#ifdef __cplusplus
extern "C"
{
#endif
    AnyVector* AnyVector_create()
    {
        return reinterpret_cast<AnyVector*>(new OTIO_NS::AnyVector());
    }
    void AnyVector_destroy(AnyVector* self)
    {
        delete reinterpret_cast<OTIO_NS::AnyVector*>(self);
    }
    AnyVectorIterator* AnyVector_begin(AnyVector* self)
    {
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(
            reinterpret_cast<OTIO_NS::AnyVector*>(self)->begin()));
    }
    AnyVectorIterator* AnyVector_end(AnyVector* self)
    {
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(
            reinterpret_cast<OTIO_NS::AnyVector*>(self)->end()));
    }
    int AnyVector_size(AnyVector* self)
    {
        return reinterpret_cast<OTIO_NS::AnyVector*>(self)->size();
    }
    int AnyVector_max_size(AnyVector* self)
    {
        return reinterpret_cast<OTIO_NS::AnyVector*>(self)->max_size();
    }
    int AnyVector_capacity(AnyVector* self)
    {
        return reinterpret_cast<OTIO_NS::AnyVector*>(self)->capacity();
    }
    void AnyVector_resize(AnyVector* self, int n)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->resize(n);
    }
    _Bool AnyVector_empty(AnyVector* self)
    {
        return reinterpret_cast<OTIO_NS::AnyVector*>(self)->empty();
    }
    void AnyVector_shrink_to_fit(AnyVector* self)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->shrink_to_fit();
    }
    void AnyVector_reserve(AnyVector* self, int n)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->reserve(n);
    }
    void AnyVector_swap(AnyVector* self, AnyVector* other)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->swap(
            *reinterpret_cast<OTIO_NS::AnyVector*>(other));
    }
    Any* AnyVector_at(AnyVector* self, int pos)
    {
        OTIO_NS::any value =
            reinterpret_cast<OTIO_NS::AnyVector*>(self)->at(pos);
        return reinterpret_cast<Any*>(new OTIO_NS::any(value));
    }
    void AnyVector_push_back(AnyVector* self, Any* value)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->push_back(
            *reinterpret_cast<OTIO_NS::any*>(value));
    }
    void AnyVector_pop_back(AnyVector* self)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->pop_back();
    }
    AnyVectorIterator*
    AnyVector_insert(AnyVector* self, AnyVectorIterator* pos, Any* val)
    {
        VectorIterator it = reinterpret_cast<OTIO_NS::AnyVector*>(self)->insert(
            *reinterpret_cast<VectorIterator*>(pos),
            *reinterpret_cast<OTIO_NS::any*>(val));
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(it));
    }
    void AnyVector_clear(AnyVector* self)
    {
        reinterpret_cast<OTIO_NS::AnyVector*>(self)->clear();
    }
    AnyVectorIterator* AnyVector_erase(AnyVector* self, AnyVectorIterator* pos)
    {
        VectorIterator it = reinterpret_cast<OTIO_NS::AnyVector*>(self)->erase(
            *reinterpret_cast<VectorIterator*>(pos));
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(it));
    }
    AnyVectorIterator* AnyVector_erase_range(
        AnyVector* self, AnyVectorIterator* first, AnyVectorIterator* last)
    {
        VectorIterator it = reinterpret_cast<OTIO_NS::AnyVector*>(self)->erase(
            *reinterpret_cast<VectorIterator*>(first),
            *reinterpret_cast<VectorIterator*>(last));
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(it));
    }
    void AnyVectorIterator_advance(AnyVectorIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<VectorIterator*>(iter), dist);
    }
    AnyVectorIterator* AnyVectorIterator_next(AnyVectorIterator* iter, int dist)
    {
        VectorIterator it =
            std::next(*reinterpret_cast<VectorIterator*>(iter), dist);
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(it));
    }
    AnyVectorIterator* AnyVectorIterator_prev(AnyVectorIterator* iter, int dist)
    {
        VectorIterator it =
            std::prev(*reinterpret_cast<VectorIterator*>(iter), dist);
        return reinterpret_cast<AnyVectorIterator*>(new VectorIterator(it));
    }
    Any* AnyVectorIterator_value(AnyVectorIterator* iter)
    {
        OTIO_NS::any value = *reinterpret_cast<VectorIterator*>(iter);
        return reinterpret_cast<Any*>(new OTIO_NS::any(value));
    }
    _Bool
    AnyVectorIterator_equal(AnyVectorIterator* lhs, AnyVectorIterator* rhs)
    {
        return *reinterpret_cast<VectorIterator*>(lhs) ==
               *reinterpret_cast<VectorIterator*>(rhs);
    }
    _Bool
    AnyVectorIterator_not_equal(AnyVectorIterator* lhs, AnyVectorIterator* rhs)
    {
        return *reinterpret_cast<VectorIterator*>(lhs) ==
               *reinterpret_cast<VectorIterator*>(rhs);
    }
    void AnyVectorIterator_destroy(AnyVectorIterator* self)
    {
        delete reinterpret_cast<VectorIterator*>(self);
    }
    AnyVectorMutationStamp* AnyVectorMutationStamp_create(AnyVector* v)
    {
        return reinterpret_cast<AnyVectorMutationStamp*>(
            new OTIO_NS::AnyVector::MutationStamp(
                reinterpret_cast<OTIO_NS::AnyVector*>(v)));
    }
    void AnyVectorMutationStamp_destroy(AnyVectorMutationStamp* self)
    {
        delete reinterpret_cast<OTIO_NS::AnyVector::MutationStamp*>(self);
    }
    AnyVectorMutationStamp*
    AnyVector_get_or_create_mutation_stamp(AnyVector* self)
    {
        return reinterpret_cast<AnyVectorMutationStamp*>(
            reinterpret_cast<OTIO_NS::AnyVector*>(self)
                ->get_or_create_mutation_stamp());
    }
#ifdef __cplusplus
}
#endif
