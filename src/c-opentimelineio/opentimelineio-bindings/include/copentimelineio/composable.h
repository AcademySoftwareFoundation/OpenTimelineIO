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
    Composable*         RetainerComposable_value(RetainerComposable* self);
    void RetainerComposable_managed_destroy(RetainerComposable* self);

    Composable* Composable_create();
    Composable* Composable_create_with_name_and_metadata(
        const char* name, AnyDictionary* metadata);
    _Bool        Composable_visible(Composable* self);
    _Bool        Composable_overlapping(Composable* self);
    Composition* Composable_parent(Composable* self);
    RationalTime*
                   Composable_duration(Composable* self, OTIOErrorStatus* error_status);
    const char*    Composable_name(Composable* self);
    AnyDictionary* Composable_metadata(Composable* self);
    void           Composable_set_name(Composable* self, const char* name);
    _Bool          Composable_possibly_delete(Composable* self);
    _Bool          Composable_to_json_file(
                 Composable*      self,
                 const char*      file_name,
                 OTIOErrorStatus* error_status,
                 int              indent);
    const char* Composable_to_json_string(
        Composable* self, OTIOErrorStatus* error_status, int indent);
    _Bool
    Composable_is_equivalent_to(Composable* self, SerializableObject* other);
    Composable*
                Composable_clone(Composable* self, OTIOErrorStatus* error_status);
    const char* Composable_schema_name(Composable* self);
    int         Composable_schema_version(Composable* self);
#ifdef __cplusplus
}
#endif