#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_AnyVector.h>
#include <utilities.h>

#include <opentimelineio/anyVector.h>
#include <opentimelineio/version.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    initialize
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_initialize(
        JNIEnv *env, jobject thisObj) {
    auto *anyVector = new AnyVector();
    setHandle(env, thisObj, anyVector);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    getArray
 * Signature: ()[Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobjectArray JNICALL Java_io_opentimeline_opentimelineio_AnyVector_getArray
        (JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    jclass anyClass = env->FindClass(
            "io/opentimeline/opentimelineio/Any");
    jobjectArray result =
            env->NewObjectArray(thisHandle->size(), anyClass, nullptr);
    for (int i = 0; i < thisHandle->size(); i++) {
        auto newObj = anyFromNative(env, &thisHandle->at(i));
        registerObjectToOTIOFactory(env, newObj);
        env->SetObjectArrayElement(
                result, i, newObj);
    }
    return result;
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    get
 * Signature: (I)Lio/opentimeline/opentimelineio/Any;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_get(
        JNIEnv *env, jobject thisObj, jint index) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    if (index >= thisHandle->size()) {
        throwIndexOutOfBoundsException(env, "");
        return nullptr;
    }
    return anyFromNative(env, &(thisHandle->at(index)));
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    add
 * Signature: (Lio/opentimeline/opentimelineio/Any;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentimelineio_AnyVector_add__Lio_opentimeline_opentimelineio_Any_2
        (JNIEnv *env, jobject thisObj, jobject anyObj) {
    if (anyObj == nullptr) {
        throwNullPointerException(env, "");
        return false;
    }
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    auto anyHandle = getHandle<any>(env, anyObj);
    thisHandle->push_back(*anyHandle);
    return true;
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    add
 * Signature: (ILio/opentimeline/opentimelineio/Any;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentimelineio_AnyVector_add__ILio_opentimeline_opentimelineio_Any_2
        (JNIEnv *env, jobject thisObj, jint index, jobject anyObj) {
    if (anyObj == nullptr) {
        throwNullPointerException(env, "");
        return false;
    }
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    auto anyHandle = getHandle<any>(env, anyObj);
    auto itPos = thisHandle->begin() + index;
    thisHandle->insert(itPos, *anyHandle);
    return true;
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    clear
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_clear(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    thisHandle->clear();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    ensureCapacity
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_ensureCapacity(
        JNIEnv *env, jobject thisObj, jint capacity) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    thisHandle->reserve(capacity);
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    size
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_size(JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    return thisHandle->size();
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    remove
 * Signature: (I)Z
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_remove(
        JNIEnv *env, jobject thisObj, jint index) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    if (index >= thisHandle->size()) { throwIndexOutOfBoundsException(env, ""); }
    else {
        thisHandle->erase(thisHandle->begin() + index);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_AnyVector
 * Method:    trimToSize
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_AnyVector_trimToSize(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<AnyVector>(env, thisObj);
    thisHandle->shrink_to_fit();
}
