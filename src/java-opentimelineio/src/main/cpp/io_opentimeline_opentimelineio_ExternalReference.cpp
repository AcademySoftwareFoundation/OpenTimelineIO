#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_ExternalReference.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_ExternalReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ExternalReference_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring targetURL,
        jobject availableRangeObj,
        jobject metadataObj) {
    if (targetURL == nullptr || metadataObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string targetURLString = env->GetStringUTFChars(targetURL, 0);
        optional<TimeRange> availableRange = nullopt;
        if (availableRangeObj != nullptr) { availableRange = timeRangeFromJObject(env, availableRangeObj); }
        auto metadataHandle =
                getHandle<AnyDictionary>(env, metadataObj);
        auto externalReference = new ExternalReference(
                targetURLString, availableRange, *metadataHandle);
        auto mrManager =
                new SerializableObject::Retainer<ExternalReference>(externalReference);
        setHandle(env, thisObj, mrManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ExternalReference
 * Method:    getTargetURL
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ExternalReference_getTargetURL(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ExternalReference>>(env, thisObj);
    auto mr = thisHandle->value;
    return env->NewStringUTF(mr->target_url().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ExternalReference
 * Method:    setTargetURL
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ExternalReference_setTargetURL(
        JNIEnv *env, jobject thisObj, jstring targetURL) {
    if (targetURL == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<SerializableObject::Retainer<ExternalReference>>(env, thisObj);
        auto mr = thisHandle->value;
        std::string targetURLStr = env->GetStringUTFChars(targetURL, 0);
        mr->set_target_url(targetURLStr);
    }
}
