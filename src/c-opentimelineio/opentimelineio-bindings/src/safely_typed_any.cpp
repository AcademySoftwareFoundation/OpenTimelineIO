#include "copentimelineio/safely_typed_any.h"
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentimelineio/any.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/safely_typed_any.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>
#include <string.h>
#include <utility>
#include <vector>

#ifdef __cplusplus
extern "C"
{
#endif

    Any* create_safely_typed_any_bool(_Bool boolValue)
    {
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(boolValue));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_int(int intValue)
    {
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(intValue));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_int64(int64_t int64Value)
    {
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(int64Value));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_double(double doubleValue)
    {
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(doubleValue));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_string(const char* stringValue)
    {
        std::string  str = stringValue;
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(str));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_rational_time(RationalTime* rationalTimeValue)
    {
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(std::move(
            *reinterpret_cast<opentime::RationalTime*>(rationalTimeValue)));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_time_range(TimeRange* timeRangeValue)
    {
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(
            std::move(*reinterpret_cast<opentime::TimeRange*>(timeRangeValue)));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any*
    create_safely_typed_any_time_transform(TimeTransform* timeTransformValue)
    {
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(std::move(
            *reinterpret_cast<opentime::TimeTransform*>(timeTransformValue)));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_any_vector(AnyVector* anyVectorValue)
    {
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(
            std::move(*reinterpret_cast<OTIO_NS::AnyVector*>(anyVectorValue)));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any*
    create_safely_typed_any_any_dictionary(AnyDictionary* anyDictionaryValue)
    {
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(std::move(
            *reinterpret_cast<OTIO_NS::AnyDictionary*>(anyDictionaryValue)));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }
    Any* create_safely_typed_any_serializable_object(
        SerializableObject* serializableObjectValue)
    {
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(
            reinterpret_cast<OTIO_NS::SerializableObject*>(
                serializableObjectValue));
        return reinterpret_cast<Any*>(new OTIO_NS::any(anyValue));
    }

    _Bool safely_cast_bool_any(Any* a)
    {
        return OTIO_NS::safely_cast_bool_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
    }
    int safely_cast_int_any(Any* a)
    {
        return OTIO_NS::safely_cast_int_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
    }
    int64_t safely_cast_int64_any(Any* a)
    {
        return OTIO_NS::safely_cast_int64_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
    }
    double safely_cast_double_any(Any* a)
    {
        return OTIO_NS::safely_cast_double_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
    }
    const char* safely_cast_string_any(Any* a)
    {
        std::string returnStr = OTIO_NS::safely_cast_string_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
        char* charPtr = (char*) malloc((returnStr.size() + 1) * sizeof(char));
        strcpy(charPtr, returnStr.c_str());
        return charPtr;
    }
    RationalTime* safely_cast_rational_time_any(Any* a)
    {
        opentime::RationalTime rationalTime =
            OTIO_NS::safely_cast_rational_time_any(
                *reinterpret_cast<OTIO_NS::any*>(a));
        return reinterpret_cast<RationalTime*>(
            new opentime::RationalTime(rationalTime));
    }
    TimeRange* safely_cast_time_range_any(Any* a)
    {
        opentime::TimeRange timeRange = OTIO_NS::safely_cast_time_range_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
        return reinterpret_cast<TimeRange*>(new opentime::TimeRange(timeRange));
    }
    TimeTransform* safely_cast_time_transform_any(Any* a)
    {
        opentime::TimeTransform timeTransform =
            OTIO_NS::safely_cast_time_transform_any(
                *reinterpret_cast<OTIO_NS::any*>(a));
        return reinterpret_cast<TimeTransform*>(
            new opentime::TimeTransform(timeTransform));
    }
    SerializableObject* safely_cast_retainer_any(Any* a)
    {
        return reinterpret_cast<SerializableObject*>(
            OTIO_NS::safely_cast_retainer_any(
                *reinterpret_cast<OTIO_NS::any*>(a)));
    }

    AnyDictionary* safely_cast_any_dictionary_any(Any* a)
    {
        OTIO_NS::AnyDictionary anyDictionary =
            OTIO_NS::safely_cast_any_dictionary_any(
                *reinterpret_cast<OTIO_NS::any*>(a));
        return reinterpret_cast<AnyDictionary*>(
            new OTIO_NS::AnyDictionary(anyDictionary));
    }
    AnyVector* safely_cast_any_vector_any(Any* a)
    {
        OTIO_NS::AnyVector anyVector = OTIO_NS::safely_cast_any_vector_any(
            *reinterpret_cast<OTIO_NS::any*>(a));
        return reinterpret_cast<AnyVector*>(new OTIO_NS::AnyVector(anyVector));
    }
#ifdef __cplusplus
}
#endif