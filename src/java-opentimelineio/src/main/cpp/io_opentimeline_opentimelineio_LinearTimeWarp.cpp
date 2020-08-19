#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_LinearTimeWarp.h>
#include <opentimelineio/linearTimeWarp.h>
#include <opentimelineio/version.h>
#include <otio_manager.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_LinearTimeWarp
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;DLio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_LinearTimeWarp_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jstring effectName,
        jdouble timeScalar,
        jobject metadata) {
    if (name == nullptr || effectName == nullptr || metadata == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        std::string effectNameStr = env->GetStringUTFChars(effectName, 0);
        auto metadataHandle = getHandle<AnyDictionary>(env, metadata);
        auto linearTimeWarp = new LinearTimeWarp(
                nameStr, effectNameStr, timeScalar, *metadataHandle);
        auto effectManager =
                new SerializableObject::Retainer<LinearTimeWarp>(linearTimeWarp);
        setHandle(env, thisObj, effectManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_LinearTimeWarp
 * Method:    getTimeScalar
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentimelineio_LinearTimeWarp_getTimeScalar(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<LinearTimeWarp>>(env, thisObj);
    auto linearTimeWarp = thisHandle->value;
    return linearTimeWarp->time_scalar();
}

/*
 * Class:     io_opentimeline_opentimelineio_LinearTimeWarp
 * Method:    setTimeScalar
 * Signature: (D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_LinearTimeWarp_setTimeScalar(
        JNIEnv *env, jobject thisObj, jdouble timeScalar) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<LinearTimeWarp>>(env, thisObj);
    auto linearTimeWarp = thisHandle->value;
    linearTimeWarp->set_time_scalar(timeScalar);
}
