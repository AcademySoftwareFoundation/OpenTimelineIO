#include <io_opentimeline_opentime_RationalTime.h>
#include <handle.h>
#include <utilities.h>

#include <opentime/version.h>
#include <opentime/rationalTime.h>

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    initialize
 * Signature: (DD)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentime_RationalTime_initialize
        (JNIEnv *env, jobject thisObj, jdouble value, jdouble rate) {
    opentime::RationalTime *rationalTime = new opentime::RationalTime(value, rate);
    setHandle(env, thisObj, rationalTime);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    getValue
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_getValue
        (JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    return thisHandle->value();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    getRate
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_getRate
        (JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    return thisHandle->rate();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    isInvalidTime
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_RationalTime_isInvalidTime
        (JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    return thisHandle->is_invalid_time();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    add
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_add
        (JNIEnv *env, jobject thisObj, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    auto result = (*thisHandle + *otherHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    subtract
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_subtract
        (JNIEnv *env, jobject thisObj, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    auto result = (*thisHandle - *otherHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    rescaledTo
 * Signature: (D)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_rescaledTo__D
        (JNIEnv *env, jobject thisObj, jdouble newRate) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto result = thisHandle->rescaled_to(newRate);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    rescaledTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_RationalTime_rescaledTo__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    auto result = thisHandle->rescaled_to(*otherHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    valueRescaledTo
 * Signature: (D)D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_valueRescaledTo__D
        (JNIEnv *env, jobject thisObj, jdouble newRate) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    return thisHandle->value_rescaled_to(newRate);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    valueRescaledTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentime_RationalTime_valueRescaledTo__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    return thisHandle->value_rescaled_to(*otherHandle);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    almostEqual
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_almostEqual__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    return thisHandle->almost_equal(*otherHandle, 0);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    almostEqual
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_almostEqual__Lio_opentimeline_opentime_RationalTime_2D
        (JNIEnv *env, jobject thisObj, jobject otherObject, jdouble delta) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    return thisHandle->almost_equal(*otherHandle, delta);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    durationFromStartEndTime
 * Signature: (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_durationFromStartEndTime
        (JNIEnv *env, jclass thisClass, jobject startTimeObject, jobject endTimeExclusiveObject) {
    auto startTimeHandle = getHandle<opentime::RationalTime>(env, startTimeObject);
    auto endTimeExclusiveHandle = getHandle<opentime::RationalTime>(env, endTimeExclusiveObject);
    auto result = opentime::RationalTime::duration_from_start_end_time(*startTimeHandle, *endTimeExclusiveHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    isValidTimecodeRate
 * Signature: (D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_RationalTime_isValidTimecodeRate
        (JNIEnv *env, jclass thisClass, jdouble rate) {
    return opentime::RationalTime::is_valid_timecode_rate(rate);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    fromTimecode
 * Signature: (Ljava/lang/String;DLio/opentimeline/opentime/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_fromTimecode
        (JNIEnv *env, jclass thisClass, jstring timecode, jdouble rate, jobject errorStatusObject) {
    auto errorStatusHandle = getHandle<opentime::ErrorStatus>(env, errorStatusObject);
    auto result = opentime::RationalTime::from_timecode(env->GetStringUTFChars(timecode, 0), rate, errorStatusHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    fromTimeString
 * Signature: (Ljava/lang/String;DLio/opentimeline/opentime/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_fromTimeString
        (JNIEnv *env, jclass thisClass, jstring timeString, jdouble rate, jobject errorStatusObject) {
    auto errorStatusHandle = getHandle<opentime::ErrorStatus>(env, errorStatusObject);
    auto result = opentime::RationalTime::from_time_string(env->GetStringUTFChars(timeString, 0), rate,
                                                           errorStatusHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    toTimecodeNative
 * Signature: (DILio/opentimeline/opentime/ErrorStatus;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_io_opentimeline_opentime_RationalTime_toTimecodeNative
        (JNIEnv *env, jobject thisObj, jdouble rate, jint dropFrameIndex, jobject errorStatusObject) {
    auto errorStatusHandle = getHandle<opentime::ErrorStatus>(env, errorStatusObject);
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    return env->NewStringUTF(
            thisHandle->to_timecode(rate, opentime::IsDropFrameRate(dropFrameIndex), errorStatusHandle).c_str());
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    toTimeString
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_io_opentimeline_opentime_RationalTime_toTimeString
        (JNIEnv *env, jobject thisObj) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    return env->NewStringUTF(thisHandle->to_time_string().c_str());
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    compareTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentime_RationalTime_compareTo
        (JNIEnv *env, jobject thisObj, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObj);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    if (*thisHandle < *otherHandle)
        return -1;
    else if (*thisHandle > *otherHandle)
        return 1;
    else if (*thisHandle == *otherHandle)
        return 0;

    // this should be impossible
    return -99;
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentime_RationalTime_dispose
        (JNIEnv *env, jobject thisObj) {
    opentime::RationalTime *rationalTime = getHandle<opentime::RationalTime>(env, thisObj);
    setHandle<opentime::RationalTime>(env, thisObj, nullptr);
    delete rationalTime;
}
