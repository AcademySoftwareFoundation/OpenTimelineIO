#include <jni.h>

#ifndef _EXCEPTIONS_H_INCLUDED_
#define _EXCEPTIONS_H_INCLUDED_

inline jint throwNullPointerException(JNIEnv *env, const char *message) {
  const char *className = "java/lang/NullPointerException";
  jclass exClass = env->FindClass(className);
  return env->ThrowNew(exClass, message);
}

inline jint throwNoSuchElementException(JNIEnv *env, const char *message) {
  const char *className = "java/util/NoSuchElementException";
  jclass exClass = env->FindClass(className);
  return env->ThrowNew(exClass, message);
}

inline jint throwIndexOutOfBoundsException(JNIEnv *env, const char *message) {
  const char *className = "java/util/IndexOutOfBoundsException";
  jclass exClass = env->FindClass(className);
  return env->ThrowNew(exClass, message);
}

#endif