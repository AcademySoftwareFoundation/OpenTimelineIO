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
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_initialize(
    JNIEnv* env,
    jobject thisObj,
    jstring name,
    jobject availableRangeObj,
    jobject metadataObj)
{
    if(name == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        OTIO_NS::optional<opentime::TimeRange> availableRange =
            OTIO_NS::nullopt;
        if(availableRangeObj != nullptr)
        { availableRange = timeRangeFromJObject(env, availableRangeObj); }
        auto metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto mediaReference = new OTIO_NS::MediaReference(
            nameStr, availableRange, *metadataHandle);
        setHandle(env, thisObj, mediaReference);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    getAvailableRange
 * Signature: ()Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_getAvailableRange(
    JNIEnv* env, jobject thisObj)
{
    auto    thisHandle     = getHandle<OTIO_NS::MediaReference>(env, thisObj);
    auto    availableRange = thisHandle->available_range();
    jobject result         = nullptr;
    if(availableRange != OTIO_NS::nullopt)
        result = timeRangeToJObject(env, availableRange.value());
    return result;
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    setAvailableRange
 * Signature: (Lio/opentimeline/opentime/TimeRange;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_setAvailableRange(
    JNIEnv* env, jobject thisObj, jobject availableRangeObj)
{
    auto thisHandle = getHandle<OTIO_NS::MediaReference>(env, thisObj);
    OTIO_NS::optional<opentime::TimeRange> availableRange = OTIO_NS::nullopt;
    if(availableRangeObj != nullptr)
        availableRange = timeRangeFromJObject(env, availableRangeObj);
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
