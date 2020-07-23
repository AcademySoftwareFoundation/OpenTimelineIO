#include <handle.h>
#include <io_opentimeline_opentimelineio_Any.h>
#include <utilities.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentimelineio/any.h>
#include <opentimelineio/safely_typed_any.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeBool
 * Signature: (Z)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeBool(
    JNIEnv* env, jobject thisObj, jboolean boolParam)
{

    OTIO_NS::any anyValue =
        OTIO_NS::create_safely_typed_any(std::move(boolParam));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeInt
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeInt(
    JNIEnv* env, jobject thisObj, jint intParam)
{
    OTIO_NS::any anyValue =
        OTIO_NS::create_safely_typed_any(std::move(intParam));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeDouble
 * Signature: (D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeDouble(
    JNIEnv* env, jobject thisObj, jdouble doubleParam)
{
    OTIO_NS::any anyValue =
        OTIO_NS::create_safely_typed_any(std::move(doubleParam));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeString
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeString(
    JNIEnv* env, jobject thisObj, jstring stringParam)
{
    std::string  stringVal = env->GetStringUTFChars(stringParam, 0);
    OTIO_NS::any anyValue =
        OTIO_NS::create_safely_typed_any(std::move(stringVal));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeRationalTime
 * Signature: ([D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeRationalTime(
    JNIEnv* env, jobject thisObj, jdoubleArray rationalTime)
{
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    OTIO_NS::any anyValue     = OTIO_NS::create_safely_typed_any(std::move(rt));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeTimeRange
 * Signature: ([D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeTimeRange(
    JNIEnv* env, jobject thisObj, jdoubleArray timeRange)
{
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    OTIO_NS::any anyValue  = OTIO_NS::create_safely_typed_any(std::move(tr));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeTimeTransform
 * Signature: ([D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeTimeTransform(
    JNIEnv* env, jobject thisObj, jdoubleArray timeTransform)
{
    opentime::TimeTransform tt = timeTransformFromArray(env, timeTransform);
    OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(std::move(tt));
    setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeAnyVector
 * Signature: (Lio/opentimeline/opentimelineio/AnyVector;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeAnyVector(
    JNIEnv* env, jobject thisObj, jobject anyVectorObj)
{
    if(anyVectorObj == nullptr) { throwNullPointerException(env, ""); }
    else
    {
        auto anyVectorHandle = getHandle<OTIO_NS::AnyVector>(env, anyVectorObj);
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(*anyVectorHandle));
        setHandle(env, thisObj, new OTIO_NS::any(anyValue));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeAnyDictionary
 * Signature: (Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeAnyDictionary(
    JNIEnv* env, jobject thisObj, jobject anyDictionaryObj)
{
    if(anyDictionaryObj == nullptr) { throwNullPointerException(env, ""); }
    else
    {
        auto anyDictionaryHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, anyDictionaryObj);
        OTIO_NS::any anyValue =
            OTIO_NS::create_safely_typed_any(std::move(*anyDictionaryHandle));
        setHandle(env, thisObj, new OTIO_NS::any(anyValue));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initializeSerializableObject
 * Signature: (Lio/opentimeline/opentimelineio/SerializableObject;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initializeSerializableObject(
    JNIEnv* env, jobject thisObj, jobject serializableObjectObj)
{
    if(serializableObjectObj == nullptr) { throwNullPointerException(env, ""); }
    else
    {
        auto serializableObjectHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, serializableObjectObj);
        OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(
            std::move(*serializableObjectHandle));
        setHandle(env, thisObj, new OTIO_NS::any(anyValue));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastBoolean
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastBoolean(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    return OTIO_NS::safely_cast_bool_any(*thisHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastInt
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastInt(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    return OTIO_NS::safely_cast_int_any(*thisHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastDouble
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastDouble(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    return OTIO_NS::safely_cast_double_any(*thisHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastString
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastString(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    return env->NewStringUTF(
        OTIO_NS::safely_cast_string_any(*thisHandle).c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastRationalTimeNative
 * Signature: ()[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastRationalTimeNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    auto result     = OTIO_NS::safely_cast_rational_time_any(*thisHandle);
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastTimeRangeNative
 * Signature: ()[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastTimeRangeNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    auto result     = OTIO_NS::safely_cast_time_range_any(*thisHandle);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastTimeTransformNative
 * Signature: ()[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastTimeTransformNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    auto result     = OTIO_NS::safely_cast_time_transform_any(*thisHandle);
    return timeTransformToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastSerializableObject
 * Signature: ()Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastSerializableObject(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    auto result     = OTIO_NS::safely_cast_retainer_any(*thisHandle);
    return serializableObjectFromNative(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastAnyDictionary
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastAnyDictionary(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    auto result     = OTIO_NS::safely_cast_any_dictionary_any(*thisHandle);
    return anyDictionaryFromNative(env, &result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastAnyVector
 * Signature: ()Lio/opentimeline/opentimelineio/AnyVector;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastAnyVector(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
    auto result     = OTIO_NS::safely_cast_any_vector_any(*thisHandle);
    return anyVectorFromNative(env, &result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_dispose(JNIEnv* env, jobject thisObj)
{
    OTIO_NS::any* anyVal = getHandle<OTIO_NS::any>(env, thisObj);
    setHandle<OTIO_NS::any>(env, thisObj, nullptr);
    delete anyVal;
}
