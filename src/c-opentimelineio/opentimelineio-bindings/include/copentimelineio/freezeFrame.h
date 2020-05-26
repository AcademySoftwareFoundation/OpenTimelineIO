#pragma once

#include "anyDictionary.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct FreezeFrame;
    typedef struct FreezeFrame FreezeFrame;

    FreezeFrame* FreezeFrame_create(const char* name, AnyDictionary* metadata);
#ifdef __cplusplus
}
#endif
