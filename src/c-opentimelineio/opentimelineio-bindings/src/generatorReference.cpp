#include "copentimelineio/generatorReference.h"
#include <opentime/timeRange.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/generatorReference.h>
#include <string.h>

#ifdef __cplusplus
extern "C"
{
#endif
    GeneratorReference* GeneratorReference_create(
        const char*    name,
        const char*    generator_kind,
        TimeRange*     available_range,
        AnyDictionary* parameters,
        AnyDictionary* metadata)
    {
        nonstd::optional<opentime::TimeRange> timeRangeOptional =
            nonstd::nullopt;
        if(available_range != NULL)
        {
            timeRangeOptional = nonstd::optional<opentime::TimeRange>(
                *reinterpret_cast<opentime::TimeRange*>(available_range));
        }
        return reinterpret_cast<GeneratorReference*>(
            new OTIO_NS::GeneratorReference(
                name,
                generator_kind,
                timeRangeOptional,
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(parameters),
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata)));
    }
    const char* GeneratorReference_generator_kind(GeneratorReference* self)
    {
        std::string returnStr =
            reinterpret_cast<OTIO_NS::GeneratorReference*>(self)
                ->generator_kind();
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    void GeneratorReference_set_generator_kind(
        GeneratorReference* self, const char* generator_kind)
    {
        reinterpret_cast<OTIO_NS::GeneratorReference*>(self)
            ->set_generator_kind(generator_kind);
    }
    AnyDictionary* GeneratorReference_parameters(GeneratorReference* self)
    {
        OTIO_NS::AnyDictionary anyDictionary =
            reinterpret_cast<OTIO_NS::GeneratorReference*>(self)->parameters();
        return reinterpret_cast<AnyDictionary*>(
            new OTIO_NS::AnyDictionary(anyDictionary));
    }
#ifdef __cplusplus
}
#endif
