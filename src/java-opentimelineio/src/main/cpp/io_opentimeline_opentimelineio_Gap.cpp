#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Gap.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Gap
 * Method:    initializeSourceRange
 * Signature: ([DLjava/lang/String;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Gap_initializeSourceRange(
    JNIEnv*      env,
    jobject      thisObj,
    jdoubleArray sourceRangeArray,
    jstring      name,
    jobjectArray effectsArray,
    jobjectArray markersArray,
    jobject      metadataObj)
{
    if(name == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr     = env->GetStringUTFChars(name, 0);
        auto        sourceRange = timeRangeFromArray(env, sourceRangeArray);
        auto        metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto effects = effectVectorFromArray(env, effectsArray);
        auto markers = markerVectorFromArray(env, markersArray);
        auto gap     = new OTIO_NS::Gap(
            sourceRange, nameStr, effects, markers, *metadataHandle);
        setHandle(env, thisObj, gap);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Gap
 * Method:    initializeDuration
 * Signature: ([DLjava/lang/String;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Gap_initializeDuration(
    JNIEnv*      env,
    jobject      thisObj,
    jdoubleArray durationRationalTimeArray,
    jstring      name,
    jobjectArray effectsArray,
    jobjectArray markersArray,
    jobject      metadataObj)
{
    if(name == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto duration = rationalTimeFromArray(env, durationRationalTimeArray);
        auto metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto effects = effectVectorFromArray(env, effectsArray);
        auto markers = markerVectorFromArray(env, markersArray);
        auto gap     = new OTIO_NS::Gap(
            duration, nameStr, effects, markers, *metadataHandle);
        setHandle(env, thisObj, gap);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Gap
 * Method:    isVisible
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Gap_isVisible(JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Gap>(env, thisObj);
    return thisHandle->visible();
}
