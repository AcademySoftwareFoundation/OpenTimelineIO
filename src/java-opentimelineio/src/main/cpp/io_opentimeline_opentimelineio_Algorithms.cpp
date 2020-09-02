#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Algorithms.h>
#include <opentimelineio/stackAlgorithm.h>
#include <opentimelineio/trackAlgorithm.h>
#include <opentimelineio/version.h>
#include <utilities.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_Algorithms
 * Method:    flattenStack
 * Signature: (Lio/opentimeline/opentimelineio/Stack;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/Track;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentimelineio_Algorithms_flattenStack
        (JNIEnv *env, jobject thisObj, jobject inStack, jobject errorStatusObj) {
    if (inStack == nullptr || errorStatusObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto inStackHandle =
            getHandle<SerializableObject::Retainer<OTIO_NS::Stack>>(env, inStack);
    auto stack = inStackHandle->value;
    auto result = OTIO_NS::flatten_stack(stack, errorStatusHandle);
    return trackFromNative(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Algorithms
 * Method:    flattenStackNative
 * Signature: ([Lio/opentimeline/opentimelineio/Track;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/Track;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentimelineio_Algorithms_flattenStackNative
        (JNIEnv *env, jobject thisObj, jobjectArray tracksArray, jobject errorStatusObj) {
    if (errorStatusObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto tracksVector = trackVectorFromArray(env, tracksArray);
    auto result = flatten_stack(tracksVector, errorStatusHandle);
    return trackFromNative(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Algorithms
 * Method:    trackTrimmedToRange
 * Signature: (Lio/opentimeline/opentimelineio/Track;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/Track;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentimelineio_Algorithms_trackTrimmedToRange
        (JNIEnv *env, jobject thisObj, jobject inTrack, jobject trimRangeObj, jobject errorStatusObj) {
    if (inTrack == nullptr || trimRangeObj == nullptr ||
        errorStatusObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    }
    auto inTrackHandle =
            getHandle<SerializableObject::Retainer<Track>>(env, inTrack);
    auto track = inTrackHandle->value;
    auto trimRange = timeRangeFromJObject(env, trimRangeObj);
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = track_trimmed_to_range(
            track, trimRange, errorStatusHandle);
    return trackFromNative(env, result);
}
