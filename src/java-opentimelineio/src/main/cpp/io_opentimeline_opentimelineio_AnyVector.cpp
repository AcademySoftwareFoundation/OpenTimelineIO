#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_AnyVector.h>
#include <utilities.h>

#include <opentimelineio/anyVector.h>
#include <opentimelineio/version.h>
/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    initialize
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_AnyVector_initialize(
    JNIEnv *env, jobject thisObj) {
  OTIO_NS::AnyVector *anyVector = new OTIO_NS::AnyVector();
  setHandle(env, thisObj, anyVector);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    get
 * Signature: (I)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentimelineio_AnyVector_get(
    JNIEnv *env, jobject thisObj, jint index) {
  auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  if (index >= thisHandle->size()) {
    throwIndexOutOfBoundsException(env, "");
  } else {
    return anyFromNative(env, &(thisHandle->at(index)));
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    add
 * Signature: (Lio/opentimeline/opentimelineio/Any;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_add__Lio_opentimeline_opentimelineio_Any_2(
    JNIEnv *env, jobject thisObj, jobject anyObj) {
  if (anyObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
    auto anyHandle = getHandle<OTIO_NS::any>(env, anyObj);
    thisHandle->push_back(*anyHandle);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    add
 * Signature: (ILio/opentimeline/opentimelineio/Any;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_add__ILio_opentimeline_opentimelineio_Any_2(
    JNIEnv *env, jobject thisObj, jint index, jobject anyObj) {
  if (anyObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
    auto anyHandle = getHandle<OTIO_NS::any>(env, anyObj);
    auto itPos = thisHandle->begin() + index;
    thisHandle->insert(itPos, *anyHandle);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    clear
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_AnyVector_clear(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  thisHandle->clear();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    ensureCapacity
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_ensureCapacity(JNIEnv *env,
                                                             jobject thisObj,
                                                             jint capacity) {
  auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  thisHandle->reserve(capacity);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    size
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentimelineio_AnyVector_size(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  return thisHandle->size();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    remove
 * Signature: (I)Z
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_AnyVector_remove(
    JNIEnv *env, jobject thisObj, jint index) {
  auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  if (index >= thisHandle->size()) {
    throwIndexOutOfBoundsException(env, "");
  } else {
    thisHandle->erase(thisHandle->begin() + index);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    trimToSize
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_AnyVector_trimToSize(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  thisHandle->shrink_to_fit();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_AnyVector_dispose(
    JNIEnv *env, jobject thisObj) {
  OTIO_NS::AnyVector *anyVector = getHandle<OTIO_NS::AnyVector>(env, thisObj);
  setHandle<OTIO_NS::AnyVector>(env, thisObj, nullptr);
  delete anyVector;
}
