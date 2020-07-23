#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Algorithms.h>
#include <opentimelineio/stackAlgorithm.h>
#include <opentimelineio/trackAlgorithm.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Algorithms
 * Method:    flattenStack
 * Signature: (Lio/opentimeline/opentimelineio/Stack;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/Track;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Algorithms_flattenStack(
    JNIEnv* env, jclass thisClass, jobject inStack, jobject errorStatusObj)
{
    if(inStack == nullptr || errorStatusObj)
        throwNullPointerException(env, "");
    else
    {
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto inStackHandle = getHandle<OTIO_NS::Stack>(env, inStack);
        auto result = OTIO_NS::flatten_stack(inStackHandle, errorStatusHandle);
        return trackFromNative(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Algorithms
 * Method:    flattenStackNative
 * Signature: ([Lio/opentimeline/opentimelineio/Track;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/Track;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Algorithms_flattenStackNative(
    JNIEnv*      env,
    jclass       thisClass,
    jobjectArray tracksArray,
    jobject      errorStatusObj)
{
    if(errorStatusObj == nullptr)
        throwNullPointerException(env, "");
    else
    {
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto tracksVector = trackVectorFromArray(env, tracksArray);
        auto result = OTIO_NS::flatten_stack(tracksVector, errorStatusHandle);
        return trackFromNative(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Algorithms
 * Method:    trackTrimmedToRange
 * Signature: (Lio/opentimeline/opentimelineio/Track;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/Track;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Algorithms_trackTrimmedToRange(
    JNIEnv* env,
    jclass  thisClass,
    jobject inTrack,
    jobject trimRangeObj,
    jobject errorStatusObj)
{
    if(inTrack == nullptr || trimRangeObj == nullptr ||
       errorStatusObj == nullptr)
        throwNullPointerException(env, "");
    else
    {
        auto inTrackHandle = getHandle<OTIO_NS::Track>(env, inTrack);
        auto trimRange     = timeRangeFromJObject(env, trimRangeObj);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto result = OTIO_NS::track_trimmed_to_range(
            inTrackHandle, trimRange, errorStatusHandle);
        return trackFromNative(env, result);
    }
}
