#pragma once

#include "errorStatus.h"
#include "any.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    const char* serialize_json_to_string(
        Any* value, OTIOErrorStatus* error_status, int indent = 4);
    _Bool serialize_json_to_file(
        Any*             value,
        const char*      file_name,
        OTIOErrorStatus* error_status,
        int              indent = 4);
#ifdef __cplusplus
}
#endif