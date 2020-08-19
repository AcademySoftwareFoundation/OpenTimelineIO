#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_MissingReference.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_MissingReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_MissingReference_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jobject availableRangeObj,
        jobject metadataObj) {
    std::string nameStr = env->GetStringUTFChars(name, 0);
    optional<TimeRange> availableRange = nullopt;
    if (availableRangeObj != nullptr) { availableRange = timeRangeFromJObject(env, availableRangeObj); }
    auto metadataHandle = getHandle<AnyDictionary>(env, metadataObj);
    auto missingReference =
            new MissingReference(nameStr, availableRange, *metadataHandle);
    auto mrManager =
            new SerializableObject::Retainer<MissingReference>(missingReference);
    setHandle(env, thisObj, mrManager);
}

/*
 * Class:     io_opentimeline_opentimelineio_MissingReference
 * Method:    isMissingReference
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_MissingReference_isMissingReference(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<MissingReference>>(env, thisObj);
    auto mr = thisHandle->value;
    return mr->is_missing_reference();
}
