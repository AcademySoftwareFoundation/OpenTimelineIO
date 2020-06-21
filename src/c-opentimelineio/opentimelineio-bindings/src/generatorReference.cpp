#include "copentimelineio/generatorReference.h"
#include <copentimelineio/mediaReference.h>
#include <copentimelineio/serializableObjectWithMetadata.h>
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
    TimeRange* GeneratorReference_available_range(GeneratorReference* self)
    {
        return MediaReference_available_range((MediaReference*) self);
    }
    void GeneratorReference_set_available_range(
        GeneratorReference* self, TimeRange* available_range)
    {
        MediaReference_set_available_range(
            (MediaReference*) self, available_range);
    }
    _Bool GeneratorReference_is_missing_reference(GeneratorReference* self)
    {
        return MediaReference_is_missing_reference((MediaReference*) self);
    }
    const char* GeneratorReference_name(GeneratorReference* self)
    {
        return SerializableObjectWithMetadata_name(
            (SerializableObjectWithMetadata*) self);
    }
    void GeneratorReference_set_name(GeneratorReference* self, const char* name)
    {
        SerializableObjectWithMetadata_set_name(
            (SerializableObjectWithMetadata*) self, name);
    }
    AnyDictionary* GeneratorReference_metadata(GeneratorReference* self)
    {
        return SerializableObjectWithMetadata_metadata(
            (SerializableObjectWithMetadata*) self);
    }
    _Bool GeneratorReference_possibly_delete(GeneratorReference* self)
    {
        return SerializableObject_possibly_delete((SerializableObject*) self);
    }
    _Bool GeneratorReference_to_json_file(
        GeneratorReference* self,
        const char*         file_name,
        OTIOErrorStatus*    error_status,
        int                 indent)
    {
        return SerializableObject_to_json_file(
            (SerializableObject*) self, file_name, error_status, indent);
    }
    const char* GeneratorReference_to_json_string(
        GeneratorReference* self, OTIOErrorStatus* error_status, int indent)
    {
        return SerializableObject_to_json_string(
            (SerializableObject*) self, error_status, indent);
    }
    _Bool GeneratorReference_is_equivalent_to(
        GeneratorReference* self, SerializableObject* other)
    {
        return SerializableObject_is_equivalent_to(
            (SerializableObject*) self, other);
    }
    GeneratorReference* GeneratorReference_clone(
        GeneratorReference* self, OTIOErrorStatus* error_status)
    {
        return (GeneratorReference*) SerializableObject_clone(
            (SerializableObject*) self, error_status);
    }
    const char* GeneratorReference_schema_name(GeneratorReference* self)
    {
        return SerializableObject_schema_name((SerializableObject*) self);
    }
    int GeneratorReference_schema_version(GeneratorReference* self)
    {
        return SerializableObject_schema_version((SerializableObject*) self);
    }
#ifdef __cplusplus
}
#endif
