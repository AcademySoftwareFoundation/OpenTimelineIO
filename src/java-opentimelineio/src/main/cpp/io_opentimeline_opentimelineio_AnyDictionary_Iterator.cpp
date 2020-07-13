#include <handle.h>
#include <io_opentimeline_opentimelineio_AnyDictionary_Iterator.h>
#include <utilities.h>

#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_initialize(
    JNIEnv *env, jobject thisObj, jobject dictionaryObj) {
  auto dictionaryHandle = getHandle<OTIO_NS::AnyDictionary>(env, dictionaryObj);
  OTIO_NS::AnyDictionary::iterator *it =
      new OTIO_NS::AnyDictionary::iterator(dictionaryHandle->begin());
  setHandle(env, thisObj, it);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    nextNative
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary/Iterator;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_nextNative(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  (*thisHandle)++;
  return anyDictionaryIteratorFromNative(
      env, new OTIO_NS::AnyDictionary::iterator(*thisHandle));
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    previousNative
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary/Iterator;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_previousNative(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  (*thisHandle)--;
  return anyDictionaryIteratorFromNative(
      env, new OTIO_NS::AnyDictionary::iterator(*thisHandle));
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    hasNextNative
 * Signature: (Lio/opentimeline/opentimelineio/AnyDictionary;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_hasNextNative(
    JNIEnv *env, jobject thisObj, jobject dictionaryObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  auto dictionaryHandle = getHandle<OTIO_NS::AnyDictionary>(env, dictionaryObj);
  return !(*thisHandle == dictionaryHandle->end());
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    hasPreviousNative
 * Signature: (Lio/opentimeline/opentimelineio/AnyDictionary;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_hasPreviousNative(
    JNIEnv *env, jobject thisObj, jobject dictionaryObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  auto dictionaryHandle = getHandle<OTIO_NS::AnyDictionary>(env, dictionaryObj);
  return !(*thisHandle == dictionaryHandle->begin());
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    getKey
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_getKey(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  return env->NewStringUTF((*thisHandle)->first.c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    getValue
 * Signature: ()Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_getValue(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  return anyFromNative(env, &((*thisHandle)->second));
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary_Iterator
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_00024Iterator_dispose(
    JNIEnv *env, jobject thisObj) {
  OTIO_NS::AnyDictionary::iterator *it =
      getHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj);
  setHandle<OTIO_NS::AnyDictionary::iterator>(env, thisObj, nullptr);
  delete it;
}
