#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Item.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/item.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Item_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jobject sourceRangeObj,
        jobject metadataObj,
        jobjectArray effectsArray,
        jobjectArray markersArray) {
    if (name == nullptr || metadataObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        OTIO_NS::optional<opentime::TimeRange> sourceRange = OTIO_NS::nullopt;
        if (sourceRangeObj != nullptr) { sourceRange = timeRangeFromJObject(env, sourceRangeObj); }
        auto metadataHandle =
                getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto effects = effectVectorFromArray(env, effectsArray);
        auto markers = markerVectorFromArray(env, markersArray);
        auto item = new OTIO_NS::Item(
                nameStr, sourceRange, *metadataHandle, effects, markers);
        auto itemManager =
                new managing_ptr<OTIO_NS::Item>(env, item);
        setHandle(env, thisObj, itemManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    isVisible
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Item_isVisible(JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    return item->visible();
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    isOverlapping
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Item_isOverlapping(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    return item->overlapping();
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getSourceRange
 * Signature: ()Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getSourceRange(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto sourceRange = item->source_range();
    jobject result = nullptr;
    if (sourceRange != OTIO_NS::nullopt)
        result = timeRangeToJObject(env, sourceRange.value());
    return result;
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    setSourceRange
 * Signature: (Lio/opentimeline/opentime/TimeRange;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Item_setSourceRange(
        JNIEnv *env, jobject thisObj, jobject sourceRangeObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    OTIO_NS::optional<opentime::TimeRange> sourceRange = OTIO_NS::nullopt;
    if (sourceRangeObj != nullptr)
        sourceRange = timeRangeFromJObject(env, sourceRangeObj);

    item->set_source_range(sourceRange);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getEffectsNative
 * Signature: ()[Lio/opentimeline/opentimelineio/SerializableObject/Retainer;
 */
JNIEXPORT jobjectArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getEffectsNative(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect>>
            effects = item->effects();
    return effectRetainerVectorToArray(env, effects);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getMarkersNative
 * Signature: ()[Lio/opentimeline/opentimelineio/SerializableObject/Retainer;
 */
JNIEXPORT jobjectArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getMarkersNative(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker>>
            markers = item->markers();
    return markerRetainerVectorToArray(env, markers);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getDuration
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getDuration(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = item->duration(errorStatusHandle);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getAvailableRange
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getAvailableRange(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = item->available_range(errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTrimmedRange
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getTrimmedRange(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = item->trimmed_range(errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getVisibleRange
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getVisibleRange(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = item->visible_range(errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTrimmedRangeInParent
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getTrimmedRangeInParent(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = item->trimmed_range_in_parent(errorStatusHandle);
    auto resultArray = env->NewDoubleArray(0);
    if (result == OTIO_NS::nullopt) return resultArray;
    return timeRangeToJObject(env, result.value());
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getRangeInParent
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentimelineio_Item_getRangeInParent
        (JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
    auto item = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = item->range_in_parent(errorStatusHandle);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTransformedTime
 * Signature: (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentimelineio/Item;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getTransformedTime(
        JNIEnv *env,
        jobject thisObj,
        jobject rationalTimeObj,
        jobject toItemObj,
        jobject errorStatusObj) {
    if (toItemObj == nullptr || rationalTimeObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
        auto item = thisHandle->get();
        auto toItemHandle =
                getHandle<managing_ptr<OTIO_NS::Item>>(env, toItemObj);
        auto toItem = toItemHandle->get();
        auto rationalTime = rationalTimeFromJObject(env, rationalTimeObj);
        auto errorStatusHandle =
                getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto result = item->transformed_time(
                rationalTime, toItem, errorStatusHandle);
        return rationalTimeToJObject(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTransformedTimeRange
 * Signature: (Lio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/Item;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Item_getTransformedTimeRange(
        JNIEnv *env,
        jobject thisObj,
        jobject timeRangeObj,
        jobject toItemObj,
        jobject errorStatusObj) {
    if (toItemObj == nullptr || timeRangeObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::Item>>(env, thisObj);
        auto item = thisHandle->get();
        auto toItemHandle =
                getHandle<managing_ptr<OTIO_NS::Item>>(env, toItemObj);
        auto toItem = toItemHandle->get();
        auto timeRange = timeRangeFromJObject(env, timeRangeObj);
        auto errorStatusHandle =
                getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto result = item->transformed_time_range(
                timeRange, toItem, errorStatusHandle);
        return timeRangeToJObject(env, result);
    }
}
