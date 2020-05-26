#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
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
#ifdef __cplusplus
}
#endif
