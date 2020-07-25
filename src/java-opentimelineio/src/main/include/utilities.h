#include <jni.h>

#include <exceptions.h>
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/mediaReference.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
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

inline std::vector<OTIO_NS::Effect*>
effectVectorFromArray(JNIEnv* env, jobjectArray array)
{
    int                           arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Effect*> objectVector;
    objectVector.reserve(arrayLength);
    for(int i = 0; i < arrayLength; ++i)
    {
        jobject element       = env->GetObjectArrayElement(array, i);
        auto    elementHandle = getHandle<OTIO_NS::Effect>(env, element);
        objectVector.push_back(elementHandle);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Marker*>
markerVectorFromArray(JNIEnv* env, jobjectArray array)
{
    int                           arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Marker*> objectVector;
    objectVector.reserve(arrayLength);
    for(int i = 0; i < arrayLength; ++i)
    {
        jobject element       = env->GetObjectArrayElement(array, i);
        auto    elementHandle = getHandle<OTIO_NS::Marker>(env, element);
        objectVector.push_back(elementHandle);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Composable*>
composableVectorFromArray(JNIEnv* env, jobjectArray array)
{
    int                               arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Composable*> objectVector;
    objectVector.reserve(arrayLength);
    for(int i = 0; i < arrayLength; ++i)
    {
        jobject element       = env->GetObjectArrayElement(array, i);
        auto    elementHandle = getHandle<OTIO_NS::Composable>(env, element);
        objectVector.push_back(elementHandle);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Track*>
trackVectorFromArray(JNIEnv* env, jobjectArray array)
{
    int                          arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Track*> objectVector;
    objectVector.reserve(arrayLength);
    for(int i = 0; i < arrayLength; ++i)
    {
        jobject element       = env->GetObjectArrayElement(array, i);
        auto    elementHandle = getHandle<OTIO_NS::Track>(env, element);
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
composableFromNative(JNIEnv* env, OTIO_NS::Composable* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Composable");
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
effectRetainerFromNative(
    JNIEnv* env, OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect>* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/SerializableObject$Retainer");
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
markerRetainerFromNative(
    JNIEnv* env, OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker>* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/SerializableObject$Retainer");
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
composableRetainerFromNative(
    JNIEnv*                                                     env,
    OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/SerializableObject$Retainer");
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
compositionFromNative(JNIEnv* env, OTIO_NS::Composition* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Composition");
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
mediaReferenceFromNative(JNIEnv* env, OTIO_NS::MediaReference* native)
{
    jclass cls =
        env->FindClass("io/opentimeline/opentimelineio/MediaReference");
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
stackFromNative(JNIEnv* env, OTIO_NS::Stack* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Stack");
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
trackFromNative(JNIEnv* env, OTIO_NS::Track* native)
{
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Track");
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
        env->NewObjectArray(v.size(), serializableObjectRetainerClass, nullptr);
    for(int i = 0; i < v.size(); i++)
    {
        env->SetObjectArrayElement(
            result, i, serializableObjectRetainerFromNative(env, &v[i]));
    }
    return result;
}

inline jobjectArray
effectRetainerVectorToArray(
    JNIEnv*                                                              env,
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect>>& v)
{
    jclass effectRetainerClass =
        env->FindClass("io/opentimeline/opentimelineio/SerializableObject$Retainer");
    jobjectArray result =
        env->NewObjectArray(v.size(), effectRetainerClass, nullptr);
    for(int i = 0; i < v.size(); i++)
    {
        env->SetObjectArrayElement(
            result, i, effectRetainerFromNative(env, &v[i]));
    }
    return result;
}

inline jobjectArray
markerRetainerVectorToArray(
    JNIEnv*                                                              env,
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker>>& v)
{
    jclass markerRetainerClass =
        env->FindClass("io/opentimeline/opentimelineio/SerializableObject$Retainer");
    jobjectArray result =
        env->NewObjectArray(v.size(), markerRetainerClass, nullptr);
    for(int i = 0; i < v.size(); i++)
    {
        env->SetObjectArrayElement(
            result, i, markerRetainerFromNative(env, &v[i]));
    }
    return result;
}

inline jobjectArray
composableRetainerVectorToArray(
    JNIEnv* env,
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>>& v)
{
    jclass composableRetainerClass = env->FindClass(
        "io/opentimeline/opentimelineio/SerializableObject$Retainer");
    jobjectArray result =
        env->NewObjectArray(v.size(), composableRetainerClass, nullptr);
    for(int i = 0; i < v.size(); i++)
    {
        env->SetObjectArrayElement(
            result, i, composableRetainerFromNative(env, &v[i]));
    }
    return result;
}

inline jobjectArray
trackVectorToArray(JNIEnv* env, std::vector<OTIO_NS::Track*>& v)
{
    jclass trackClass = env->FindClass("io/opentimeline/opentimelineio/Track");
    jobjectArray result = env->NewObjectArray(v.size(), trackClass, nullptr);
    for(int i = 0; i < v.size(); i++)
    {
        env->SetObjectArrayElement(result, i, trackFromNative(env, v[i]));
    }
    return result;
}

inline opentime::RationalTime
rationalTimeFromJObject(JNIEnv* env, jobject rtObject)
{
    jclass    rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID getValue = env->GetMethodID(rtClass, "getValue", "()D");
    jmethodID getRate  = env->GetMethodID(rtClass, "getRate", "()D");
    double    value    = env->CallDoubleMethod(rtObject, getValue);
    double    rate     = env->CallDoubleMethod(rtObject, getRate);
    opentime::RationalTime rt(value, rate);
    return rt;
}

inline opentime::TimeRange
timeRangeFromJObject(JNIEnv* env, jobject trObject)
{
    jclass    trClass = env->FindClass("io/opentimeline/opentime/TimeRange");
    jmethodID getStartTime = env->GetMethodID(
        trClass, "getStartTime", "()Lio/opentimeline/opentime/RationalTime;");
    jmethodID getDuration = env->GetMethodID(
        trClass, "getDuration", "()Lio/opentimeline/opentime/RationalTime;");
    jobject startTime = env->CallObjectMethod(trObject, getStartTime);
    jobject duration  = env->CallObjectMethod(trObject, getDuration);

    jclass    rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID getValue = env->GetMethodID(rtClass, "getValue", "()D");
    jmethodID getRate  = env->GetMethodID(rtClass, "getRate", "()D");

    double startTimeValue = env->CallDoubleMethod(startTime, getValue);
    double startTimeRate  = env->CallDoubleMethod(startTime, getRate);
    double durationValue  = env->CallDoubleMethod(duration, getValue);
    double durationRate   = env->CallDoubleMethod(duration, getRate);

    opentime::TimeRange tr(
        opentime::RationalTime(startTimeValue, startTimeRate),
        opentime::RationalTime(durationValue, durationRate));

    return tr;
}

inline opentime::TimeTransform
timeTransformFromJObject(JNIEnv* env, jobject txObject)
{
    jclass trClass = env->FindClass("io/opentimeline/opentime/TimeTransform");
    jmethodID getOffset = env->GetMethodID(
        trClass, "getOffset", "()Lio/opentimeline/opentime/RationalTime;");
    jmethodID getScale = env->GetMethodID(trClass, "getScale", "()D");
    jmethodID getRate  = env->GetMethodID(trClass, "getRate", "()D");
    jobject   offset   = env->CallObjectMethod(txObject, getOffset);
    double    scale    = env->CallDoubleMethod(txObject, getScale);
    double    rate     = env->CallDoubleMethod(txObject, getRate);

    jclass    rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID getRationalTimeValue =
        env->GetMethodID(rtClass, "getValue", "()D");
    jmethodID getRationalTimeRate = env->GetMethodID(rtClass, "getRate", "()D");

    double offsetValue = env->CallDoubleMethod(offset, getRationalTimeValue);
    double offsetRate  = env->CallDoubleMethod(offset, getRationalTimeRate);

    opentime::TimeTransform timeTransform(
        opentime::RationalTime(offsetValue, offsetRate), scale, rate);
    return timeTransform;
}

inline jobject
rationalTimeToJObject(JNIEnv* env, opentime::RationalTime rationalTime)
{
    jclass    rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID rtInit  = env->GetMethodID(rtClass, "<init>", "(DD)V");
    jobject   rt      = env->NewObject(
        rtClass, rtInit, rationalTime.value(), rationalTime.rate());
    return rt;
}

inline jobject
timeRangeToJObject(JNIEnv* env, opentime::TimeRange timeRange)
{
    jclass    trClass = env->FindClass("io/opentimeline/opentime/TimeRange");
    jmethodID trInit  = env->GetMethodID(
        trClass,
        "<init>",
        "(Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)V");
    jobject startTime = rationalTimeToJObject(env, timeRange.start_time());
    jobject duration  = rationalTimeToJObject(env, timeRange.duration());
    jobject tr        = env->NewObject(trClass, trInit, startTime, duration);
    return tr;
}

inline jobject
timeTransformToJObject(JNIEnv* env, opentime::TimeTransform timeTransform)
{
    jclass txClass   = env->FindClass("io/opentimeline/opentime/TimeTransform");
    jmethodID txInit = env->GetMethodID(
        txClass, "<init>", "(Lio/opentimeline/opentime/RationalTime;DD)V");
    jobject offset = rationalTimeToJObject(env, timeTransform.offset());
    jobject tx     = env->NewObject(
        txClass, txInit, offset, timeTransform.scale(), timeTransform.rate());
    return tx;
}
#endif