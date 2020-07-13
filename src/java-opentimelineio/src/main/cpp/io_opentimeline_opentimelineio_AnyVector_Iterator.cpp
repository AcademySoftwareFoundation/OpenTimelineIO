#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_AnyVector_Iterator.h>
#include <utilities.h>

#include <opentimelineio/anyVector.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector_Iterator
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentimelineio/AnyVector;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_00024Iterator_initialize(
    JNIEnv *env, jobject thisObj, jobject vectorObj) {
  auto vectorHandle = getHandle<OTIO_NS::AnyVector>(env, vectorObj);
  OTIO_NS::AnyVector::iterator *it =
      new OTIO_NS::AnyVector::iterator(vectorHandle->begin());
  setHandle(env, thisObj, it);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector_Iterator
 * Method:    nextNative
 * Signature:
 * (Lio/opentimeline/opentimelineio/AnyVector;)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_00024Iterator_nextNative(
    JNIEnv *env, jobject thisObj, jobject vectorObj) {
  auto vectorHandle = getHandle<OTIO_NS::AnyVector>(env, vectorObj);
  auto thisHandle = getHandle<OTIO_NS::AnyVector::iterator>(env, thisObj);
  if (*thisHandle == vectorHandle->end()) {
    throwIndexOutOfBoundsException(env, "");
  } else {
    auto result = &(**thisHandle);
    (*thisHandle)++;
    return anyFromNative(env, result);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector_Iterator
 * Method:    previousNative
 * Signature:
 * (Lio/opentimeline/opentimelineio/AnyVector;)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_00024Iterator_previousNative(
    JNIEnv *env, jobject thisObj, jobject vectorObj) {
  auto vectorHandle = getHandle<OTIO_NS::AnyVector>(env, vectorObj);
  auto thisHandle = getHandle<OTIO_NS::AnyVector::iterator>(env, thisObj);
  if (*thisHandle == vectorHandle->begin()) {
    throwIndexOutOfBoundsException(env, "");
  } else {
    (*thisHandle)--;
    return anyFromNative(env, &(**thisHandle));
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector_Iterator
 * Method:    hasNextNative
 * Signature: (Lio/opentimeline/opentimelineio/AnyVector;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_00024Iterator_hasNextNative(
    JNIEnv *env, jobject thisObj, jobject vectorObj) {
  auto vectorHandle = getHandle<OTIO_NS::AnyVector>(env, vectorObj);
  auto thisHandle = getHandle<OTIO_NS::AnyVector::iterator>(env, thisObj);
  if (*thisHandle == vectorHandle->end()) {
    return false;
  } else {
    return true;
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector_Iterator
 * Method:    hasPreviousNative
 * Signature: (Lio/opentimeline/opentimelineio/AnyVector;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_00024Iterator_hasPreviousNative(
    JNIEnv *env, jobject thisObj, jobject vectorObj) {
  auto vectorHandle = getHandle<OTIO_NS::AnyVector>(env, vectorObj);
  auto thisHandle = getHandle<OTIO_NS::AnyVector::iterator>(env, thisObj);
  if (*thisHandle == vectorHandle->begin()) {
    return false;
  } else {
    return true;
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector_Iterator
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_00024Iterator_dispose(
    JNIEnv *env, jobject thisObj) {
  OTIO_NS::AnyVector::iterator *it =
      getHandle<OTIO_NS::AnyVector::iterator>(env, thisObj);
  setHandle<OTIO_NS::AnyVector::iterator>(env, thisObj, nullptr);
  delete it;
}