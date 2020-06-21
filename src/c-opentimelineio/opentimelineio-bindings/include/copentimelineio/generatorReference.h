#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct GeneratorReference;
    typedef struct GeneratorReference GeneratorReference;

    GeneratorReference* GeneratorReference_create(
        const char*    name,
        const char*    generator_kind,
        TimeRange*     available_range,
        AnyDictionary* parameters,
        AnyDictionary* metadata);
    const char* GeneratorReference_generator_kind(GeneratorReference* self);
    void        GeneratorReference_set_generator_kind(
               GeneratorReference* self, const char* generator_kind);
    AnyDictionary* GeneratorReference_parameters(GeneratorReference* self);
    TimeRange*     GeneratorReference_available_range(GeneratorReference* self);
    void           GeneratorReference_set_available_range(
                  GeneratorReference* self, TimeRange* available_range);
    _Bool GeneratorReference_is_missing_reference(GeneratorReference* self);
    const char* GeneratorReference_name(GeneratorReference* self);
    void
                   GeneratorReference_set_name(GeneratorReference* self, const char* name);
    AnyDictionary* GeneratorReference_metadata(GeneratorReference* self);
    _Bool          GeneratorReference_possibly_delete(GeneratorReference* self);
    _Bool          GeneratorReference_to_json_file(
                 GeneratorReference* self,
                 const char*         file_name,
                 OTIOErrorStatus*    error_status,
                 int                 indent);
    const char* GeneratorReference_to_json_string(
        GeneratorReference* self, OTIOErrorStatus* error_status, int indent);
    _Bool GeneratorReference_is_equivalent_to(
        GeneratorReference* self, SerializableObject* other);
    GeneratorReference* GeneratorReference_clone(
        GeneratorReference* self, OTIOErrorStatus* error_status);
    const char* GeneratorReference_schema_name(GeneratorReference* self);
    int         GeneratorReference_schema_version(GeneratorReference* self);
#ifdef __cplusplus
}
#endif
