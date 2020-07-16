#include <jni.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>

#ifndef _UTILITIES_H_INCLUDED_
#define _UTILITIES_H_INCLUDED_

inline opentime::RationalTime rationalTimeFromArray(JNIEnv *env, jdoubleArray array) {
    jdouble *elements = env->GetDoubleArrayElements(array, 0);
    jdouble value = elements[0];
    jdouble rate = elements[1];
    env->ReleaseDoubleArrayElements(array, elements, 0);
    return opentime::RationalTime(value, rate);
}

inline jdoubleArray rationalTimeToArray(JNIEnv *env, opentime::RationalTime rationalTime) {
    jdouble fill[2];
    fill[0] = rationalTime.value();
    fill[1] = rationalTime.rate();
    jdoubleArray result = env->NewDoubleArray(2);
    env->SetDoubleArrayRegion(result, 0, 2, fill);
    return result;
}

inline jobject rationalTimeFromNative(JNIEnv *env,
                                      opentime::RationalTime *native) {
    jclass cls = env->FindClass("io/opentimeline/opentime/RationalTime");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject timeRangeFromNative(JNIEnv *env, opentime::TimeRange *native) {
    jclass cls = env->FindClass("io/opentimeline/opentime/TimeRange");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject timeTransformFromNative(JNIEnv *env,
                                       opentime::TimeTransform *native) {
    jclass cls = env->FindClass("io/opentimeline/opentime/TimeTransform");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject anyFromNative(JNIEnv *env, OTIO_NS::any *native) {
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Any");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject anyDictionaryFromNative(JNIEnv *env,
                                       OTIO_NS::AnyDictionary *native) {
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/AnyDictionary");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyDictionaryIteratorFromNative(JNIEnv *env,
                                OTIO_NS::AnyDictionary::iterator *native) {
    jclass cls =
            env->FindClass("io/opentimeline/opentimelineio/AnyDictionary$Iterator");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject anyVectorFromNative(JNIEnv *env,
                                   OTIO_NS::AnyDictionary::iterator *native) {
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/AnyVector");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
anyVectorIteratorFromNative(JNIEnv *env,
                            OTIO_NS::AnyDictionary::iterator *native) {
    jclass cls =
            env->FindClass("io/opentimeline/opentimelineio/AnyVector$Iterator");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

inline jobject
serializableObjectFromNative(JNIEnv *env, OTIO_NS::SerializableObject *native) {
    jclass cls =
            env->FindClass("io/opentimeline/opentimelineio/SerializableObject");
    if (cls == NULL)
        return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit)
        return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

#endif