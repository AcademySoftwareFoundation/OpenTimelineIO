#include <handle.h>
#include <io_opentimeline_opentime_ErrorStatus.h>
#include <opentime/errorStatus.h>

/*
 * Class:     io_opentimeline_opentime_ErrorStatus
 * Method:    initialize
 * Signature: (ILjava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentime_ErrorStatus_initialize(
    JNIEnv* env, jobject thisObj, jint outcome, jstring details)
{
    opentime::ErrorStatus* errorStatus = new opentime::ErrorStatus(
        opentime::ErrorStatus::Outcome(outcome),
        env->GetStringUTFChars(details, 0));
    setHandle(env, thisObj, errorStatus);
}

/*
 * Class:     io_opentimeline_opentime_ErrorStatus
 * Method:    outcomeToStringNative
 * Signature: (I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentime_ErrorStatus_outcomeToStringNative(
    JNIEnv* env, jclass thisClass, jint outcome)
{
    return env->NewStringUTF(opentime::ErrorStatus::outcome_to_string(
                                 opentime::ErrorStatus::Outcome(outcome))
                                 .c_str());
}

/*
 * Class:     io_opentimeline_opentime_ErrorStatus
 * Method:    getOutcomeNative
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentime_ErrorStatus_getOutcomeNative(
    JNIEnv* env, jobject thisObj)
{
    auto objectHandle = getHandle<opentime::ErrorStatus>(env, thisObj);
    return int(objectHandle->outcome);
}

/*
 * Class:     io_opentimeline_opentime_ErrorStatus
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentime_ErrorStatus_dispose(JNIEnv* env, jobject thisObj)
{
    opentime::ErrorStatus* errorStatus =
        getHandle<opentime::ErrorStatus>(env, thisObj);
    setHandle<opentime::ErrorStatus>(env, thisObj, nullptr);
    delete errorStatus;
}