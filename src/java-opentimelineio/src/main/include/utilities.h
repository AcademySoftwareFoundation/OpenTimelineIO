#include <jni.h>

#include <exceptions.h>
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>

#ifndef _UTILITIES_H_INCLUDED_
#    define _UTILITIES_H_INCLUDED_

inline opentime::RationalTime
rationalTimeFromArray(JNIEnv* env, jdoubleArray array)
{
    if(env->GetArrayLength(array) != 2)
    { throwRuntimeException(env, "Unable to convert array to RationalTime"); }
    else
    {
        jdouble* elements = env->GetDoubleArrayElements(array, 0);
        jdouble  value    = elements[0];
        jdouble  rate     = elements[1];
        env->ReleaseDoubleArrayElements(array, elements, 0);
        return opentime::RationalTime(value, rate);
    }
}

inline jdoubleArray
rationalTimeToArray(JNIEnv* env, opentime::RationalTime rationalTime)
{
    jdouble fill[2];
    fill[0]             = rationalTime.value();
    fill[1]             = rationalTime.rate();
    jdoubleArray result = env->NewDoubleArray(2);
    env->SetDoubleArrayRegion(result, 0, 2, fill);
    return result;
}

inline opentime::TimeRange
timeRangeFromArray(JNIEnv* env, jdoubleArray array)
{
    if(env->GetArrayLength(array) != 4)
    { throwRuntimeException(env, "Unable to convert array to TimeRange"); }
    else
    {
        jdouble* elements   = env->GetDoubleArrayElements(array, 0);
        jdouble  startValue = elements[0];
        jdouble  startRate  = elements[1];
        jdouble  durValue   = elements[2];
        jdouble  durRate    = elements[3];
        env->ReleaseDoubleArrayElements(array, elements, 0);
        return opentime::TimeRange(
            opentime::RationalTime(startValue, startRate),
            opentime::RationalTime(durValue, durRate));
    }
}

inline std::vector<OTIO_NS::SerializableObject*>
serializableObjectVectorFromArray(JNIEnv* env, jobjectArray array)
{
    int arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::SerializableObject*> objectVector;
    objectVector.reserve(arrayLength);
    for(int i = 0; i < arrayLength; ++i)
    {
        jobject element = env->GetObjectArrayElement(array, i);
        auto    elementHandle =
            getHandle<OTIO_NS::SerializableObject>(env, element);
        objectVector.push_back(elementHandle);
    }
    return objectVector;
}

inline jdoubleArray
timeRangeToArray(JNIEnv* env, opentime::TimeRange timeRange)
{
    jdouble fill[4];
    fill[0]             = timeRange.start_time().value();
    fill[1]             = timeRange.start_time().rate();
    fill[2]             = timeRange.duration().value();
    fill[3]             = timeRange.duration().rate();
    jdoubleArray result = env->NewDoubleArray(4);
    env->SetDoubleArrayRegion(result, 0, 4, fill);
    return result;
}

inline opentime::TimeTransform
timeTransformFromArray(JNIEnv* env, jdoubleArray array)
{
    if(env->GetArrayLength(array) != 4)
    {
        throwRuntimeException(env, "Unable to convert array to TimeTransform");
    }
    else
    {
        jdouble* elements    = env->GetDoubleArrayElements(array, 0);
        jdouble  offsetValue = elements[0];
        jdouble  offsetRate  = elements[1];
        jdouble  scale       = elements[2];
        jdouble  rate        = elements[3];
        env->ReleaseDoubleArrayElements(array, elements, 0);
        return opentime::TimeTransform(
            opentime::RationalTime(offsetValue, offsetRate), scale, rate);
    }
}

inline jdoubleArray
timeTransformToArray(JNIEnv* env, opentime::TimeTransform timeTransform)
{
    jdouble fill[4];
    fill[0]             = timeTransform.offset().value();
    fill[1]             = timeTransform.offset().rate();
    fill[2]             = timeTransform.scale();
    fill[3]             = timeTransform.rate();
    jdoubleArray result = env->NewDoubleArray(4);
    env->SetDoubleArrayRegion(result, 0, 4, fill);
    return result;
}

inline jobject
rationalTimeFromNative(JNIEnv* env, opentime::RationalTime* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentime/RationalTime");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
timeRangeFromNative(JNIEnv* env, opentime::TimeRange* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentime/TimeRange");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
timeTransformFromNative(JNIEnv* env, opentime::TimeTransform* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentime/TimeTransform");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyFromNative(JNIEnv* env, OTIO_NS::any* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Any");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyDictionaryFromNative(JNIEnv* env, OTIO_NS::AnyDictionary* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/AnyDictionary");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyDictionaryIteratorFromNative(
    JNIEnv* env, OTIO_NS::AnyDictionary::iterator* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/AnyDictionary$Iterator");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyVectorFromNative(JNIEnv* env, OTIO_NS::AnyVector* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/AnyVector");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyVectorIteratorFromNative(JNIEnv* env, OTIO_NS::AnyVector::iterator* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/AnyVector$Iterator");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
serializableObjectFromNative(JNIEnv* env, OTIO_NS::SerializableObject* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/SerializableObject");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
serializableObjectRetainerFromNative(
    JNIEnv*                                                             env,
    OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>* native)
{
    jclass cls = env->FindClass(
        "io/opentimeline/opentimelineio/SerializableObject$Retainer");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
composableFromNative(JNIEnv* env, OTIO_NS::Composable* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/Composable");
    if(cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if(NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj =
        env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobjectArray
serializableObjectRetainerVectorToArray(
    JNIEnv* env,
    std::vector<
        OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>& v)
{
    jclass serializableObjectRetainerClass = env->FindClass(
        "io/opentimeline/opentimelineio/SerializableObject$Retainer");
    jobjectArray result =
        env->NewObjectArray(v.size(), serializableObjectRetainerClass, 0);
    for(int i = 0; i < v.size(); i++)
    {
        env->SetObjectArrayElement(
            result, i, serializableObjectRetainerFromNative(env, &v[i]));
    }
    return result;
}

#endif