#pragma once

#include "any.h"
#include "anyDictionary.h"
#include "anyVector.h"
#include "copentime/rationalTime.h"
#include "copentime/timeRange.h"
#include "copentime/timeTransform.h"
#include "serializableObject.h"
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C"
{
#endif

    Any* create_safely_typed_any_bool(_Bool boolValue);
    Any* create_safely_typed_any_int(int intValue);
    Any* create_safely_typed_any_int64(int64_t int64Value);
    Any* create_safely_typed_any_double(double doubleValue);
    Any* create_safely_typed_any_string(const char* stringValue);
    Any* create_safely_typed_any_rational_time(RationalTime* rationalTimeValue);
    Any* create_safely_typed_any_time_range(TimeRange* timeRangeValue);
    Any*
         create_safely_typed_any_time_transform(TimeTransform* timeTransformValue);
    Any* create_safely_typed_any_any_vector(AnyVector* anyVectorValue);
    Any*
         create_safely_typed_any_any_dictionary(AnyDictionary* anyDictionaryValue);
    Any* create_safely_typed_any_serializable_object(
        SerializableObject* serializableObjectValue);

    _Bool               safely_cast_bool_any(Any* a);
    int                 safely_cast_int_any(Any* a);
    int64_t             safely_cast_int64_any(Any* a);
    double              safely_cast_double_any(Any* a);
    const char*         safely_cast_string_any(Any* a);
    RationalTime*       safely_cast_rational_time_any(Any* a);
    TimeRange*          safely_cast_time_range_any(Any* a);
    TimeTransform*      safely_cast_time_transform_any(Any* a);
    SerializableObject* safely_cast_retainer_any(Any* a);

    AnyDictionary* safely_cast_any_dictionary_any(Any* a);
    AnyVector*     safely_cast_any_vector_any(Any* a);
#ifdef __cplusplus
}
#endif