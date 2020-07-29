#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Transition.h>
#include <opentimelineio/transition.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_initialize(
    JNIEnv* env,
    jobject thisObj,
    jstring name,
    jstring transitionType,
    jobject inOffsetRationalTime,
    jobject outOffsetRationalTime,
    jobject metadataObj)
{
    if(name == nullptr || transitionType == nullptr ||
       inOffsetRationalTime == nullptr || outOffsetRationalTime == nullptr ||
       metadataObj == nullptr)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        std::string transitionTypeStr =
            env->GetStringUTFChars(transitionType, 0);
        auto inOffset  = rationalTimeFromJObject(env, inOffsetRationalTime);
        auto outOffset = rationalTimeFromJObject(env, outOffsetRationalTime);
        auto metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto transition = new OTIO_NS::Transition(
            nameStr, transitionTypeStr, inOffset, outOffset, *metadataHandle);
        auto transitionManager =
                new managing_ptr<OTIO_NS::Transition>(env, transition);
        setHandle(env, thisObj, transitionManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    isOverlapping
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Transition_isOverlapping(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    return transition->overlapping();
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getTransitionType
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Transition_getTransitionType(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    return env->NewStringUTF(transition->transition_type().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    setTransitionType
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_setTransitionType(
    JNIEnv* env, jobject thisObj, jstring transitionType)
{
    std::string transitionTypeStr =
        env->GetStringUTFChars(transitionType, nullptr);
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    transition->set_transition_type(transitionTypeStr);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getInOffset
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getInOffset(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    auto result     = transition->in_offset();
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    setInOffset
 * Signature: (Lio/opentimeline/opentime/RationalTime;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_setInOffset(
    JNIEnv* env, jobject thisObj, jobject inOffsetRationalTime)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    auto inOffset   = rationalTimeFromJObject(env, inOffsetRationalTime);
    transition->set_in_offset(inOffset);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getOutOffset
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getOutOffset(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    auto result     = transition->out_offset();
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    setOutOffset
 * Signature: (Lio/opentimeline/opentime/RationalTime;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Transition_setOutOffset(
    JNIEnv* env, jobject thisObj, jobject outOffsetRationalTime)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    auto outOffset  = rationalTimeFromJObject(env, outOffsetRationalTime);
    transition->set_out_offset(outOffset);
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getDuration
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getDuration(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
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
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = transition->range_in_parent(errorStatusHandle);
    if(result == OTIO_NS::nullopt) return nullptr;
    return timeRangeToJObject(env, result.value());
}

/*
 * Class:     io_opentimeline_opentimelineio_Transition
 * Method:    getTrimmedRangeInParent
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Transition_getTrimmedRangeInParent(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Transition>>(env, thisObj);
    auto transition = thisHandle->get();
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = transition->trimmed_range_in_parent(errorStatusHandle);
    if(result == OTIO_NS::nullopt) return nullptr;
    return timeRangeToJObject(env, result.value());
}