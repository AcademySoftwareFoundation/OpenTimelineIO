#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Gap.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/version.h>
#include <utilities.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_Gap
 * Method:    initializeSourceRange
 * Signature: (Lio/opentimeline/opentime/TimeRange;Ljava/lang/String;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Gap_initializeSourceRange(
        JNIEnv *env,
        jobject thisObj,
        jobject sourceRangeObj,
        jstring name,
        jobjectArray effectsArray,
        jobjectArray markersArray,
        jobject metadataObj) {
    if (name == nullptr || metadataObj == nullptr || sourceRangeObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto sourceRange = timeRangeFromJObject(env, sourceRangeObj);
        auto metadataHandle =
                getHandle<AnyDictionary>(env, metadataObj);
        auto effects = effectVectorFromArray(env, effectsArray);
        auto markers = markerVectorFromArray(env, markersArray);
        auto gap = new Gap(
                sourceRange, nameStr, effects, markers, *metadataHandle);
        auto gapManager =
                new SerializableObject::Retainer<Gap>(gap);
        setHandle(env, thisObj, gapManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Gap
 * Method:    initializeDuration
 * Signature: (Lio/opentimeline/opentime/RationalTime;Ljava/lang/String;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Gap_initializeDuration(
        JNIEnv *env,
        jobject thisObj,
        jobject durationRationalTimeObj,
        jstring name,
        jobjectArray effectsArray,
        jobjectArray markersArray,
        jobject metadataObj) {
    if (name == nullptr || metadataObj == nullptr ||
        durationRationalTimeObj == nullptr) {
        throwNullPointerException(env, "");
        return;
    }
    std::string nameStr = env->GetStringUTFChars(name, 0);
    auto duration = rationalTimeFromJObject(env, durationRationalTimeObj);
    auto metadataHandle =
            getHandle<AnyDictionary>(env, metadataObj);
    auto effects = effectVectorFromArray(env, effectsArray);
    auto markers = markerVectorFromArray(env, markersArray);
    auto gap = new Gap(
            duration, nameStr, effects, markers, *metadataHandle);
    auto gapManager =
            new SerializableObject::Retainer<Gap>(gap);
    setHandle(env, thisObj, gapManager);
}

/*
 * Class:     io_opentimeline_opentimelineio_Gap
 * Method:    isVisible
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Gap_isVisible(JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<Gap>>(env, thisObj);
    auto gap = thisHandle->value;
    return gap->visible();
}
