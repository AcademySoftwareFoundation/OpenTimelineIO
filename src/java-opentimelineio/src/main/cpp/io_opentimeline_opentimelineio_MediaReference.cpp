#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_MediaReference.h>
#include <opentimelineio/mediaReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;[DLio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      name,
    jdoubleArray availableRangeArray,
    jobject      metadata)
{
    if(name == NULL || availableRangeArray == NULL || metadata == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        OTIO_NS::optional<opentime::TimeRange> availableRange =
            OTIO_NS::nullopt;
        if(env->GetArrayLength(availableRangeArray) != 0)
        { availableRange = timeRangeFromArray(env, availableRangeArray); }
        auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
        auto mediaReference = new OTIO_NS::MediaReference(
            nameStr, availableRange, *metadataHandle);
        setHandle(env, thisObj, mediaReference);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    getAvailableRangeNative
 * Signature: ()[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_getAvailableRangeNative(
    JNIEnv* env, jobject thisObj)
{
    auto         thisHandle = getHandle<OTIO_NS::MediaReference>(env, thisObj);
    auto         availableRange = thisHandle->available_range();
    jdoubleArray result         = env->NewDoubleArray(0);
    if(availableRange != OTIO_NS::nullopt)
    { result = timeRangeToArray(env, availableRange.value()); }
    return result;
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    setAvailableRangeNative
 * Signature: ([D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_setAvailableRangeNative(
    JNIEnv* env, jobject thisObj, jdoubleArray availableRangeArray)
{
    auto thisHandle = getHandle<OTIO_NS::MediaReference>(env, thisObj);
    OTIO_NS::optional<opentime::TimeRange> availableRange = OTIO_NS::nullopt;
    if(env->GetArrayLength(availableRangeArray) != 0)
    { availableRange = timeRangeFromArray(env, availableRangeArray); }
    thisHandle->set_available_range(availableRange);
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    isMissingReference
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_isMissingReference(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::MediaReference>(env, thisObj);
    return thisHandle->is_missing_reference();
}
