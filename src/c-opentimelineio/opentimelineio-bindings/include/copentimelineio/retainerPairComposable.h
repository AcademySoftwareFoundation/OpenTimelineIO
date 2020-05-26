#pragma once

#include "composable.h"

#ifdef __cplusplus
extern "C"
{
#endif
    struct RetainerPairComposable;
    typedef struct RetainerPairComposable RetainerPairComposable;

    RetainerPairComposable* RetainerPairComposable_create(
        RetainerComposable* first, RetainerComposable* second);
    RetainerComposable*
    RetainerPairComposable_first(RetainerPairComposable* self);
    RetainerComposable*
         RetainerPairComposable_second(RetainerPairComposable* self);
    void RetainerPairComposable_destroy(RetainerPairComposable* self);

#ifdef __cplusplus
}
#endif
