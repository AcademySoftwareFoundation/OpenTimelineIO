#pragma once

#include "anyDictionary.h"
#include "copentime/timeRange.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct ExternalReference;
    typedef struct ExternalReference ExternalReference;
    ExternalReference*               ExternalReference_create(
                      const char*    target_url,
                      TimeRange*     available_range,
                      AnyDictionary* metadata);
    const char* ExternalReference_target_url(ExternalReference* self);
    void        ExternalReference_set_target_url(
               ExternalReference* self, const char* target_url);
#ifdef __cplusplus
}
#endif
