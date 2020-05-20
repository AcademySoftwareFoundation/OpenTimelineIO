#include "copentimelineio/anyDictionary.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/version.h>
#include <string.h>

typedef std::map<std::string, OTIO_NS::any>::iterator DictionaryIterator;

#ifdef __cplusplus
extern "C"
{
#endif
    AnyDictionary* AnyDictionary_create()
    {
        return reinterpret_cast<AnyDictionary*>(new OTIO_NS::AnyDictionary());
    }
    void AnyDictionary_destroy(AnyDictionary* self)
    {
        delete reinterpret_cast<OTIO_NS::AnyDictionary*>(self);
    }
    void AnyDictionary_clear(AnyDictionary* self)
    {
        reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->clear();
    }
    AnyDictionaryIterator* AnyDictionary_begin(AnyDictionary* self)
    {
        return reinterpret_cast<AnyDictionaryIterator*>(new DictionaryIterator(
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->begin()));
    }
    AnyDictionaryIterator* AnyDictionary_end(AnyDictionary* self)
    {
        return reinterpret_cast<AnyDictionaryIterator*>(new DictionaryIterator(
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->end()));
    }
    void AnyDictionary_swap(AnyDictionary* self, AnyDictionary* other)
    {
        reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->swap(
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(other));
    }
    AnyDictionaryIterator*
    AnyDictionary_erase(AnyDictionary* self, AnyDictionaryIterator* pos)
    {
        DictionaryIterator it =
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->erase(
                *reinterpret_cast<DictionaryIterator*>(pos));
        return reinterpret_cast<AnyDictionaryIterator*>(
            new DictionaryIterator(it));
    }
    AnyDictionaryIterator* AnyDictionary_erase_range(
        AnyDictionary*         self,
        AnyDictionaryIterator* first,
        AnyDictionaryIterator* last)
    {
        DictionaryIterator it =
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->erase(
                *reinterpret_cast<DictionaryIterator*>(first),
                *reinterpret_cast<DictionaryIterator*>(last));
        return reinterpret_cast<AnyDictionaryIterator*>(
            new DictionaryIterator(it));
    }
    int AnyDictionary_erase_key(AnyDictionary* self, const char* key)
    {
        return reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->erase(key);
    }
    int AnyDictionary_size(AnyDictionary* self)
    {
        return reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->size();
    }
    int AnyDictionary_max_size(AnyDictionary* self)
    {
        return reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->max_size();
    }
    _Bool AnyDictionary_empty(AnyDictionary* self)
    {
        return reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->empty();
    }
    AnyDictionaryIterator*
    AnyDictionary_find(AnyDictionary* self, const char* key)
    {
        DictionaryIterator iter =
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->find(key);
        return reinterpret_cast<AnyDictionaryIterator*>(
            new DictionaryIterator(iter));
    }
    AnyDictionaryIterator*
    AnyDictionary_insert(AnyDictionary* self, const char* key, Any* anyObj)
    {
        DictionaryIterator it =
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)
                ->insert({ key, *reinterpret_cast<OTIO_NS::any*>(anyObj) })
                .first;
        return reinterpret_cast<AnyDictionaryIterator*>(
            new DictionaryIterator(it));
    }
    void AnyDictionaryIterator_advance(AnyDictionaryIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<DictionaryIterator*>(iter), dist);
    }
    AnyDictionaryIterator*
    AnyDictionaryIterator_next(AnyDictionaryIterator* iter, int dist)
    {
        DictionaryIterator it =
            std::next(*reinterpret_cast<DictionaryIterator*>(iter), dist);
        return reinterpret_cast<AnyDictionaryIterator*>(
            new DictionaryIterator(it));
    }
    AnyDictionaryIterator*
    AnyDictionaryIterator_prev(AnyDictionaryIterator* iter, int dist)
    {
        DictionaryIterator it =
            std::prev(*reinterpret_cast<DictionaryIterator*>(iter), dist);
        return reinterpret_cast<AnyDictionaryIterator*>(
            new DictionaryIterator(it));
    }
    Any* AnyDictionaryIterator_value(AnyDictionaryIterator* iter)
    {
        OTIO_NS::any value = *reinterpret_cast<DictionaryIterator*>(iter);
        return reinterpret_cast<Any*>(new OTIO_NS::any(value));
    }
    _Bool AnyDictionaryIterator_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs)
    {
        return *reinterpret_cast<DictionaryIterator*>(lhs) ==
               *reinterpret_cast<DictionaryIterator*>(rhs);
    }
    _Bool AnyDictionaryIterator_not_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs)
    {
        return *reinterpret_cast<DictionaryIterator*>(lhs) !=
               *reinterpret_cast<DictionaryIterator*>(rhs);
    }
    void AnyDictionaryIterator_destroy(AnyDictionaryIterator* self)
    {
        delete reinterpret_cast<DictionaryIterator*>(self);
    }
    AnyDictionaryMutationStamp*
    AnyDictionaryMutationStamp_create(AnyDictionary* d)
    {
        return reinterpret_cast<AnyDictionaryMutationStamp*>(
            new OTIO_NS::AnyDictionary::MutationStamp(
                reinterpret_cast<OTIO_NS::AnyDictionary*>(d)));
    }
    void AnyDictionaryMutationStamp_destroy(AnyDictionaryMutationStamp* self)
    {
        delete reinterpret_cast<OTIO_NS::AnyDictionary::MutationStamp*>(self);
    }
    AnyDictionaryMutationStamp*
    AnyDictionary_get_or_create_mutation_stamp(AnyDictionary* self)
    {
        return reinterpret_cast<AnyDictionaryMutationStamp*>(
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)
                ->get_or_create_mutation_stamp());
    }

#ifdef __cplusplus
}
#endif