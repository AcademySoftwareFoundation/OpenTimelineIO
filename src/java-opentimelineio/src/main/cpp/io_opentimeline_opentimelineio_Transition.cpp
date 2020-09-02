#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Transition.h>
#include <opentimelineio/transition.h>
#include <opentimelineio/version.h>
#include <utilities.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jstring transitionType,
        jobject inOffsetRationalTime,
        jobject outOffsetRationalTime,
        jobject metadataObj) {
    if (name == nullptr || transitionType == nullptr ||
        inOffsetRationalTime == nullptr || outOffsetRationalTime == nullptr ||
        metadataObj == nullptr) {
        throwNullPointerException(env, "");
        return;
    }
    std::string nameStr = env->GetStringUTFChars(name, 0);
    std::string transitionTypeStr =
            env->GetStringUTFChars(transitionType, 0);
    auto inOffset = rationalTimeFromJObject(env, inOffsetRationalTime);
    auto outOffset = rationalTimeFromJObject(env, outOffsetRationalTime);
    auto metadataHandle =
            getHandle<AnyDictionary>(env, metadataObj);
    auto transition = new Transition(
            nameStr, transitionTypeStr, inOffset, outOffset, *metadataHandle);
    auto transitionManager =
            new SerializableObject::Retainer<Transition>(transition);
    setHandle(env, thisObj, transitionManager);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    isOverlapping
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Transition_isOverlapping(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    return transition->overlapping();
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getTransitionType
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Transition_getTransitionType(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    return env->NewStringUTF(transition->transition_type().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    setTransitionType
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_setTransitionType(
        JNIEnv *env, jobject thisObj, jstring transitionType) {
    if (transitionType == nullptr) {
        throwNullPointerException(env, "");
        return;
    }
    std::string transitionTypeStr =
            env->GetStringUTFChars(transitionType, nullptr);
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    transition->set_transition_type(transitionTypeStr);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getInOffset
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getInOffset(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto result = transition->in_offset();
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    setInOffset
 * Signature: (Lio/opentimeline/opentime/RationalTime;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_setInOffset(
        JNIEnv *env, jobject thisObj, jobject inOffsetRationalTime) {
    if (inOffsetRationalTime == nullptr) {
        throwNullPointerException(env, "");
        return;
    }
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto inOffset = rationalTimeFromJObject(env, inOffsetRationalTime);
    transition->set_in_offset(inOffset);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getOutOffset
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getOutOffset(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto result = transition->out_offset();
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    setOutOffset
 * Signature: (Lio/opentimeline/opentime/RationalTime;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_setOutOffset(
        JNIEnv *env, jobject thisObj, jobject outOffsetRationalTime) {
    if (outOffsetRationalTime == nullptr) {
        throwNullPointerException(env, "");
        return;
    }
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto outOffset = rationalTimeFromJObject(env, outOffsetRationalTime);
    transition->set_out_offset(outOffset);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getDuration
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getDuration(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    if (errorStatusObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = transition->duration(errorStatusHandle);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getRangeInParent
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getRangeInParent(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    if (errorStatusObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = transition->range_in_parent(errorStatusHandle);
    if (result == nullopt) return nullptr;
    return timeRangeToJObject(env, result.value());
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getTrimmedRangeInParent
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getTrimmedRangeInParent(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    if (errorStatusObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Transition>>(env, thisObj);
    auto transition = thisHandle->value;
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = transition->trimmed_range_in_parent(errorStatusHandle);
    if (result == nullopt) return nullptr;
    return timeRangeToJObject(env, result.value());
}