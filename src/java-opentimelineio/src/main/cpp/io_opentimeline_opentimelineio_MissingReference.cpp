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
    OTIO_NS::optional<opentime::TimeRange> availableRange = OTIO_NS::nullopt;
    if (availableRangeObj != nullptr) { availableRange = timeRangeFromJObject(env, availableRangeObj); }
    auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
    auto missingReference =
            new OTIO_NS::MissingReference(nameStr, availableRange, *metadataHandle);
    auto mrManager =
            new managing_ptr<OTIO_NS::MissingReference>(env, missingReference);
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
            getHandle<managing_ptr<OTIO_NS::MissingReference>>(env, thisObj);
    auto mr = thisHandle->get();
    return mr->is_missing_reference();
}
