#include "copentimelineio/anyDictionary.h"
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/version.h>
#include <string.h>

typedef std::map<std::string, OTIO_NS::any>::iterator Iterator;

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
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->begin()));
    }
    AnyDictionaryIterator* AnyDictionary_end(AnyDictionary* self)
    {
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(
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
        Iterator it = reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->erase(
            *reinterpret_cast<Iterator*>(pos));
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(it));
    }
    AnyDictionaryIterator* AnyDictionary_erase_range(
        AnyDictionary*         self,
        AnyDictionaryIterator* first,
        AnyDictionaryIterator* last)
    {
        Iterator it = reinterpret_cast<OTIO_NS::AnyDictionary*>(self)->erase(
            *reinterpret_cast<Iterator*>(first),
            *reinterpret_cast<Iterator*>(last));
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(it));
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
    AnyDictionary_insert(AnyDictionary* self, const char* key, Any* anyObj)
    {
        Iterator it =
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)
                ->insert({ key, *reinterpret_cast<OTIO_NS::any*>(anyObj) })
                .first;
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(it));
    }
    MutationStamp* MutationStamp_create(AnyDictionary* d)
    {
        return reinterpret_cast<MutationStamp*>(
            new OTIO_NS::AnyDictionary::MutationStamp(
                reinterpret_cast<OTIO_NS::AnyDictionary*>(d)));
    }
    void MutationStamp_destroy(MutationStamp* self)
    {
        delete reinterpret_cast<OTIO_NS::AnyDictionary::MutationStamp*>(self);
    }
    MutationStamp*
    AnyDictionary_get_or_create_mutation_stamp(AnyDictionary* self)
    {
        return reinterpret_cast<MutationStamp*>(
            reinterpret_cast<OTIO_NS::AnyDictionary*>(self)
                ->get_or_create_mutation_stamp());
    }
    void AnyDictionaryIterator_advance(AnyDictionaryIterator* iter, int dist)
    {
        std::advance(*reinterpret_cast<Iterator*>(iter), dist);
    }
    AnyDictionaryIterator*
    AnyDictionaryIterator_next(AnyDictionaryIterator* iter, int dist)
    {
        Iterator it = std::next(*reinterpret_cast<Iterator*>(iter), dist);
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(it));
    }
    AnyDictionaryIterator*
    AnyDictionaryIterator_prev(AnyDictionaryIterator* iter, int dist)
    {
        Iterator it = std::prev(*reinterpret_cast<Iterator*>(iter), dist);
        return reinterpret_cast<AnyDictionaryIterator*>(new Iterator(it));
    }
    _Bool AnyDictionaryIterator_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs)
    {
        return *reinterpret_cast<Iterator*>(lhs) ==
               *reinterpret_cast<Iterator*>(rhs);
    }
    _Bool AnyDictionaryIterator_not_equal(
        AnyDictionaryIterator* lhs, AnyDictionaryIterator* rhs)
    {
        return *reinterpret_cast<Iterator*>(lhs) !=
               *reinterpret_cast<Iterator*>(rhs);
    }
    void AnyDictionaryIterator_destroy(AnyDictionaryIterator* self)
    {
        delete reinterpret_cast<Iterator*>(self);
    }

#ifdef __cplusplus
}
#endif