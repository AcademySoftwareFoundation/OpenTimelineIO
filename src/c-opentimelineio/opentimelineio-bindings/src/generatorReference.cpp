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
        std::string name_str = std::string();
        if(name != NULL) name_str = name;

        std::string generator_kind_str = std::string();
        if(generator_kind != NULL) generator_kind_str = generator_kind;

        OTIO_NS::AnyDictionary parametersDictionary = OTIO_NS::AnyDictionary();
        if(parameters != NULL)
            parametersDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(parameters);

        OTIO_NS::AnyDictionary metadataDictionary = OTIO_NS::AnyDictionary();
        if(metadata != NULL)
            metadataDictionary =
                *reinterpret_cast<OTIO_NS::AnyDictionary*>(metadata);

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
                parametersDictionary,
                metadataDictionary));
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
