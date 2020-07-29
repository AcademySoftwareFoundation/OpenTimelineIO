#include <handle.h>
#include <io_opentimeline_opentimelineio_ErrorStatus.h>
#include <utilities.h>

#include <opentimelineio/errorStatus.h>
#include <opentimelineio/version.h>
/*
 * Class:     io_opentimeline_opentimelineio_ErrorStatus
 * Method:    initialize
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ErrorStatus_initialize(
    JNIEnv* env, jobject thisObj)
{
    OTIO_NS::ErrorStatus* errorStatus = new OTIO_NS::ErrorStatus();
    setHandle(env, thisObj, errorStatus);
}

/*
 * Class:     io_opentimeline_opentimelineio_ErrorStatus
 * Method:    outcomeToStringNative
 * Signature: (I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ErrorStatus_outcomeToStringNative(
    JNIEnv* env, jclass thisClass, jint outcome)
{
    return env->NewStringUTF(OTIO_NS::ErrorStatus::outcome_to_string(
                                 OTIO_NS::ErrorStatus::Outcome(outcome))
                                 .c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ErrorStatus
 * Method:    getOutcomeNative
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ErrorStatus_getOutcomeNative(
    JNIEnv* env, jobject thisObj)
{
    auto objectHandle = getHandle<OTIO_NS::ErrorStatus>(env, thisObj);
    return int(objectHandle->outcome);
}
