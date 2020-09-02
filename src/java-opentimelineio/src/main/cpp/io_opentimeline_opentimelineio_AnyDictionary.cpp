#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_AnyDictionary.h>
#include <utilities.h>

#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/version.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    initialize
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_initialize(
        JNIEnv *env, jobject thisObj) {
    auto *anyDictionary = new OTIO_NS::AnyDictionary();
    setHandle(env, thisObj, anyDictionary);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    containsKey
 * Signature: (Ljava/lang/String;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_containsKey(
        JNIEnv *env, jobject thisObj, jstring keyStr) {
    if (keyStr == nullptr) {
        throwNullPointerException(env, "");
        return false;
    }
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    return !(
            thisHandle->find(env->GetStringUTFChars(keyStr, 0)) ==
            thisHandle->end());
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    get
 * Signature: (Ljava/lang/String;)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_get(
        JNIEnv *env, jobject thisObj, jstring keyStr) {
    if (keyStr == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    auto result = thisHandle->at(env->GetStringUTFChars(keyStr, 0));
    return anyFromNative(env, new any(result));
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    size
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_size(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    return thisHandle->size();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    put
 * Signature:
 * (Ljava/lang/String;Lio/opentimeline/opentimelineio/Any;)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_put(
        JNIEnv *env, jobject thisObj, jstring keyStr, jobject valueAnyObj) {
    if (keyStr == nullptr || valueAnyObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    auto valueAnyHandle = getHandle<any>(env, valueAnyObj);
    std::pair<AnyDictionary::iterator, bool> resultPair =
            thisHandle->insert(std::pair<std::string, any>(
                    env->GetStringUTFChars(keyStr, 0), *valueAnyHandle));
    if (resultPair.second) { return nullptr; }
    else {
        return anyFromNative(
                env, new any(resultPair.first->second));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    replace
 * Signature:
 * (Ljava/lang/String;Lio/opentimeline/opentimelineio/Any;)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_replace(
        JNIEnv *env, jobject thisObj, jstring keyStr, jobject valueAnyObj) {
    if (keyStr == nullptr || valueAnyObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    auto valueAnyHandle = getHandle<any>(env, valueAnyObj);
    if (thisHandle->find(env->GetStringUTFChars(keyStr, 0)) ==
        thisHandle->end()) { return nullptr; }
    else {
        auto prev = new any(
                (*thisHandle)[env->GetStringUTFChars(keyStr, 0)]);
        (*thisHandle)[env->GetStringUTFChars(keyStr, 0)] = *valueAnyHandle;
        return anyFromNative(env, prev);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    clear
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_clear(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    thisHandle->clear();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyDictionary
 * Method:    remove
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_AnyDictionary_remove(
        JNIEnv *env, jobject thisObj, jstring keyStr) {
    auto thisHandle = getHandle<AnyDictionary>(env, thisObj);
    return thisHandle->erase(env->GetStringUTFChars(keyStr, 0));
}

