#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_MediaReference.h>
#include <opentimelineio/mediaReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jobject availableRangeObj,
        jobject metadataObj) {
    if (name == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        optional<TimeRange> availableRange = nullopt;
        if (availableRangeObj != nullptr) { availableRange = timeRangeFromJObject(env, availableRangeObj); }
        auto metadataHandle =
                getHandle<AnyDictionary>(env, metadataObj);
        auto mediaReference = new MediaReference(
                nameStr, availableRange, *metadataHandle);
        auto mrManager =
                new SerializableObject::Retainer<MediaReference>(mediaReference);
        setHandle(env, thisObj, mrManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    getAvailableRange
 * Signature: ()Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_getAvailableRange(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<MediaReference>>(env, thisObj);
    auto mr = thisHandle->value;
    auto availableRange = mr->available_range();
    jobject result = nullptr;
    if (availableRange != OTIO_NS::nullopt)
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
        JNIEnv *env, jobject thisObj, jobject availableRangeObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<MediaReference>>(env, thisObj);
    auto mr = thisHandle->value;
    optional<TimeRange> availableRange = nullopt;
    if (availableRangeObj != nullptr)
        availableRange = timeRangeFromJObject(env, availableRangeObj);
    mr->set_available_range(availableRange);
}

/*
 * Class:     io_opentimeline_opentimelineio_MediaReference
 * Method:    isMissingReference
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_MediaReference_isMissingReference(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<MediaReference>>(env, thisObj);
    auto mr = thisHandle->value;
    return mr->is_missing_reference();
}
