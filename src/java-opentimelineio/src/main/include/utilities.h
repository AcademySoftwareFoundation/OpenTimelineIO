#include <jni.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/version.h>

#ifndef _UTILITIES_H_INCLUDED_
#define _UTILITIES_H_INCLUDED_

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

#endif