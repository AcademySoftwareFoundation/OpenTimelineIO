#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_ExternalReference.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_ExternalReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;[DLio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ExternalReference_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      targetURL,
    jdoubleArray availableRangeArray,
    jobject      metadata)
{
    if(targetURL == NULL || availableRangeArray == NULL || metadata == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string targetURLString = env->GetStringUTFChars(targetURL, 0);
        OTIO_NS::optional<opentime::TimeRange> availableRange =
            OTIO_NS::nullopt;
        if(env->GetArrayLength(availableRangeArray) != 0)
        { availableRange = timeRangeFromArray(env, availableRangeArray); }
        auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
        auto externalReference = new OTIO_NS::ExternalReference(
            targetURLString, availableRange, *metadataHandle);
        setHandle(env, thisObj, externalReference);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ExternalReference
 * Method:    getTargetURL
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ExternalReference_getTargetURL(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ExternalReference>(env, thisObj);
    return env->NewStringUTF(thisHandle->target_url().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ExternalReference
 * Method:    setTargetURL
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ExternalReference_setTargetURL(
    JNIEnv* env, jobject thisObj, jstring targetURL)
{
    if(targetURL == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle = getHandle<OTIO_NS::ExternalReference>(env, thisObj);
        std::string targetURLStr = env->GetStringUTFChars(targetURL, 0);
        thisHandle->set_target_url(targetURLStr);
    }
}
