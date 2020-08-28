#include <jni.h>

#ifndef _HANDLE_H_INCLUDED_
#define _HANDLE_H_INCLUDED_

template<typename T>
T *
getHandle(JNIEnv *env, jobject obj) {
    jclass otioObjClass = env->FindClass("io/opentimeline/OTIOObject");
    jmethodID getNativeManager = env->GetMethodID(
            otioObjClass, "getNativeManager", "()Lio/opentimeline/OTIONative;");
    jobject nativeManager = env->CallObjectMethod(obj, getNativeManager);

    jclass otioNativeClass = env->GetObjectClass(nativeManager);
    jfieldID nativeHandleFieldID =
            env->GetFieldID(otioNativeClass, "nativeHandle", "J");
    jlong nativeHandle = env->GetLongField(nativeManager, nativeHandleFieldID);
    return reinterpret_cast<T *>(nativeHandle);
}

template<typename T>
void
setHandle(JNIEnv *env, jobject obj, T *t) {

    jlong handle = reinterpret_cast<jlong>(t);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jmethodID init = env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(otioNativeClass, init, handle);

    jclass objClass = env->GetObjectClass(obj);
    jfieldID nativeManagerField = env->GetFieldID(
            objClass, "nativeManager", "Lio/opentimeline/OTIONative;");

    env->SetObjectField(obj, nativeManagerField, otioNative);
}

#endif