#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct UnknownSchema;
    typedef struct UnknownSchema UnknownSchema;
    UnknownSchema*        UnknownSchema_create(
               const char* original_schema_name, int original_schema_version);
    const char* UnknownSchema_original_schema_name(UnknownSchema* self);
    int         UnknownSchema_original_schema_version(UnknownSchema* self);
    _Bool       UnknownSchema_is_unknown_schema(UnknownSchema* self);
#ifdef __cplusplus
}
#endif
