#pragma once

#include "copentime/rationalTime.h"
#include "copentimelineio/anyDictionary.h"
#include "copentimelineio/errorStatus.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C"
{
#endif
    struct Composable;
    typedef struct Composable Composable;
    Composable*               Composable_create();
    Composable*               Composable_create_with_name_and_metadata(
                      const char* name, AnyDictionary* metadata);
    _Bool Composable_visible(Composable* self);
    _Bool Composable_overlapping(Composable* self);
    /*Composition* Composable_parent(Composable* self);*/
    RationalTime*
    Composable_duration(Composable* self, OTIOErrorStatus* error_status);
#ifdef __cplusplus
}
#endif