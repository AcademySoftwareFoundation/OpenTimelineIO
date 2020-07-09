#include <jni.h>

#include <opentime/version.h>
#include <opentime/rationalTime.h>

#ifndef _UTILITIES_H_INCLUDED_
#define _UTILITIES_H_INCLUDED_

/*
jobject rationalTimeFromNative(JNIEnv *env, jobject srcObj, otio::RationalTime *native)
{
  jclass cls = env->GetObjectClass(srcObj);
  if (cls == NULL) return NULL;
   // Get the Method ID of the constructor which takes a long
   jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
   if (NULL == rtInit) return NULL;
   // Call back constructor to allocate a new instance, with an int argument
   jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));
   return newObj;
}
*/

inline jobject rationalTimeFromNative(JNIEnv *env, opentime::RationalTime *native) {
    jclass cls = env->FindClass("io/opentimeline/opentime/RationalTime");
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes a long
    jmethodID rtInit = env->GetMethodID(cls, "<init>", "(J)V");
    if (NULL == rtInit) return NULL;

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, rtInit, reinterpret_cast<jlong>(native));

    return newObj;
}

#endif