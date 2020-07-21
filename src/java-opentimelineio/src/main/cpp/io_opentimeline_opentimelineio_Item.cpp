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
 * Signature: (Ljava/lang/String;[DLio/opentimeline/opentimelineio/AnyDictionary;[Lio/opentimeline/opentimelineio/Effect;[Lio/opentimeline/opentimelineio/Marker;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Item_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      name,
    jdoubleArray sourceRangeArray,
    jobject      metadataObj,
    jobjectArray effectsArray,
    jobjectArray markersArray)
{
    if(name == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        OTIO_NS::optional<opentime::TimeRange> sourceRange = OTIO_NS::nullopt;
        if(env->GetArrayLength(sourceRangeArray) != 0)
        { sourceRange = timeRangeFromArray(env, sourceRangeArray); }
        auto metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto effects = effectVectorFromArray(env, effectsArray);
        auto markers = markerVectorFromArray(env, markersArray);
        auto item    = new OTIO_NS::Item(
            nameStr, sourceRange, *metadataHandle, effects, markers);
        setHandle(env, thisObj, item);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    isVisible
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Item_isVisible(JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    return thisHandle->visible();
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    isOverlapping
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Item_isOverlapping(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    return thisHandle->overlapping();
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getSourceRangeNative
 * Signature: ()[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getSourceRangeNative(
    JNIEnv* env, jobject thisObj)
{
    auto         thisHandle  = getHandle<OTIO_NS::Item>(env, thisObj);
    auto         sourceRange = thisHandle->source_range();
    jdoubleArray result      = env->NewDoubleArray(0);
    if(sourceRange != OTIO_NS::nullopt)
        result = timeRangeToArray(env, sourceRange.value());
    return result;
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    setSourceRangeNative
 * Signature: ([D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Item_setSourceRangeNative(
    JNIEnv* env, jobject thisObj, jdoubleArray sourceRangeArray)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    if(env->GetArrayLength(sourceRangeArray) == 4)
        thisHandle->set_source_range(OTIO_NS::nullopt);
    else
    {
        auto sourceRange = timeRangeFromArray(env, sourceRangeArray);
        thisHandle->set_source_range(sourceRange);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getEffectsNative
 * Signature: ()[Lio/opentimeline/opentimelineio/SerializableObject/Retainer;
 */
JNIEXPORT jobjectArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getEffectsNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect>>
        effects = thisHandle->effects();
    return effectRetainerVectorToArray(env, effects);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getMarkersNative
 * Signature: ()[Lio/opentimeline/opentimelineio/SerializableObject/Retainer;
 */
JNIEXPORT jobjectArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getMarkersNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker>>
        markers = thisHandle->markers();
    return markerRetainerVectorToArray(env, markers);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getDurationNative
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getDurationNative(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = thisHandle->duration(errorStatusHandle);
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getAvailableRangeNative
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getAvailableRangeNative(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = thisHandle->available_range(errorStatusHandle);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTrimmedRangeNative
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getTrimmedRangeNative(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = thisHandle->trimmed_range(errorStatusHandle);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getVisibleRangeNative
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getVisibleRangeNative(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = thisHandle->visible_range(errorStatusHandle);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTrimmedRangeInParentNative
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getTrimmedRangeInParentNative(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result      = thisHandle->trimmed_range_in_parent(errorStatusHandle);
    auto resultArray = env->NewDoubleArray(0);
    if(result == OTIO_NS::nullopt) return resultArray;
    return timeRangeToArray(env, result.value());
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getRangeInParentNative
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getRangeInParentNative(
    JNIEnv* env, jobject thisObj, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::Item>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = thisHandle->range_in_parent(errorStatusHandle);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTransformedTimeNative
 * Signature: ([DLio/opentimeline/opentimelineio/Item;Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getTransformedTimeNative(
    JNIEnv*      env,
    jobject      thisObj,
    jdoubleArray rationalTimeArray,
    jobject      toItemObj,
    jobject      errorStatusObj)
{
    if(toItemObj == NULL) { throwNullPointerException(env, ""); }
    else
    {
        auto thisHandle   = getHandle<OTIO_NS::Item>(env, thisObj);
        auto toItemHandle = getHandle<OTIO_NS::Item>(env, toItemObj);
        auto rationalTime = rationalTimeFromArray(env, rationalTimeArray);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto result = thisHandle->transformed_time(
            rationalTime, toItemHandle, errorStatusHandle);
        return rationalTimeToArray(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Item
 * Method:    getTransformedTimeRangeNative
 * Signature: ([DLio/opentimeline/opentimelineio/Item;Lio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Item_getTransformedTimeRangeNative(
    JNIEnv*      env,
    jobject      thisObj,
    jdoubleArray timeRangeArray,
    jobject      toItemObj,
    jobject      errorStatusObj)
{
    if(toItemObj == NULL) { throwNullPointerException(env, ""); }
    else
    {
        auto thisHandle   = getHandle<OTIO_NS::Item>(env, thisObj);
        auto toItemHandle = getHandle<OTIO_NS::Item>(env, toItemObj);
        auto timeRange    = timeRangeFromArray(env, timeRangeArray);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto result = thisHandle->transformed_time_range(
            timeRange, toItemHandle, errorStatusHandle);
        return timeRangeToArray(env, result);
    }
}
