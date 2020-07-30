#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Stack.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Stack
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Stack_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jobject sourceRangeObj,
        jobject metadataObj,
        jobjectArray effectsArray,
        jobjectArray markersArray) {
    if (name == nullptr || metadataObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        OTIO_NS::optional<opentime::TimeRange> sourceRange = OTIO_NS::nullopt;
        if (sourceRangeObj != nullptr) { sourceRange = timeRangeFromJObject(env, sourceRangeObj); }
        auto metadataHandle =
                getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto effects = effectVectorFromArray(env, effectsArray);
        auto markers = markerVectorFromArray(env, markersArray);
        auto stack = new OTIO_NS::Stack(
                nameStr, sourceRange, *metadataHandle, effects, markers);
        auto stackManager =
                new managing_ptr<OTIO_NS::Stack>(env, stack);
        setHandle(env, thisObj, stackManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Stack
 * Method:    rangeOfChildAtIndex
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Stack_rangeOfChildAtIndex(
        JNIEnv *env, jobject thisObj, jint index, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Stack>>(env, thisObj);
    auto stack = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = stack->range_of_child_at_index(index, errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Stack
 * Method:    trimmedRangeOfChildAtIndex
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Stack_trimmedRangeOfChildAtIndex(
        JNIEnv *env, jobject thisObj, jint index, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Stack>>(env, thisObj);
    auto stack = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result =
            stack->trimmed_range_of_child_at_index(index, errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Stack
 * Method:    getAvailableRange
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Stack_getAvailableRange(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Stack>>(env, thisObj);
    auto stack = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = stack->available_range(errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Stack
 * Method:    getRangeOfAllChildren
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Ljava/util/HashMap;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Stack_getRangeOfAllChildren(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Stack>>(env, thisObj);
    auto stack = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = stack->range_of_all_children(errorStatusHandle);

    jclass hashMapClass = env->FindClass("java/util/HashMap");
    jmethodID hashMapInit = env->GetMethodID(hashMapClass, "<init>", "(I)V");
    jobject hashMapObj =
            env->NewObject(hashMapClass, hashMapInit, result.size());
    jmethodID hashMapPut = env->GetMethodID(
            hashMapClass,
            "put",
            "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;");

    jclass composableClass =
            env->FindClass("io/opentimeline/opentimelineio/Composable");
    jmethodID composableInit =
            env->GetMethodID(composableClass, "<init>", "()V");

    for (auto it: result) {
        auto first = it.first;
        auto second = it.second;

        jobject composableObject =
                env->NewObject(composableClass, composableInit);
        auto firstManager =
                new managing_ptr<OTIO_NS::Composable>(env, first);
        setHandle(env, composableObject, firstManager);
        registerObjectToOTIOFactory(env, composableObject);
        jobject tr = timeRangeToJObject(env, second);

        env->CallObjectMethod(hashMapObj, hashMapPut, composableObject, tr);
    }

    return hashMapObj;
}
