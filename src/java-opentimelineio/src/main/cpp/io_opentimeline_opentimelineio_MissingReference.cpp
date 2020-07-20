#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_MissingReference.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_MissingReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;[DLio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MissingReference_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      name,
    jdoubleArray availableRangeArray,
    jobject      metadata)
{
    std::string nameStr = env->GetStringUTFChars(name, 0);
    OTIO_NS::optional<opentime::TimeRange> availableRange = OTIO_NS::nullopt;
    if(env->GetArrayLength(availableRangeArray) != 0)
    { availableRange = timeRangeFromArray(env, availableRangeArray); }
    auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
    auto missingReference =
        new OTIO_NS::MissingReference(nameStr, availableRange, *metadataHandle);
    setHandle(env, thisObj, missingReference);
}

/*
 * Class:     io_opentimeline_opentimelineio_MissingReference
 * Method:    isMissingReference
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_MissingReference_isMissingReference(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::MediaReference>(env, thisObj);
    return thisHandle->is_missing_reference();
}
