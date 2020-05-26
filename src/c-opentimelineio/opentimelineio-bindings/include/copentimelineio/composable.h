#pragma once

#include "anyDictionary.h"
/*#include "composition.h" //importing this give an error (Composable not defined) in mapCOmposableTimeRange.h */
#include "copentime/rationalTime.h"
#include "errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct RetainerComposable;
    typedef struct RetainerComposable RetainerComposable;
    struct Composable;
    typedef struct Composable Composable;
    struct Composition; /*A workaround for now,
                         * instead of including composition.h*/
    typedef struct Composition Composition;

    RetainerComposable* RetainerComposable_create(Composable* obj);
    Composable*         RetainerComposable_take_value(RetainerComposable* self);
    void RetainerComposable_managed_destroy(RetainerComposable* self);

    Composable* Composable_create();
    Composable* Composable_create_with_name_and_metadata(
        const char* name, AnyDictionary* metadata);
    _Bool        Composable_visible(Composable* self);
    _Bool        Composable_overlapping(Composable* self);
    Composition* Composable_parent(Composable* self);
    RationalTime*
    Composable_duration(Composable* self, OTIOErrorStatus* error_status);
#ifdef __cplusplus
}
#endif