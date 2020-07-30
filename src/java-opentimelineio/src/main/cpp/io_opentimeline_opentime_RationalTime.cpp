#include <handle.h>
#include <io_opentimeline_opentime_RationalTime.h>
#include <utilities.h>
#include <opentime/rationalTime.h>

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    isInvalidTimeNative
 * Signature: (DD)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_isInvalidTimeNative(
        JNIEnv *env, jclass thisClass, jdouble value, jdouble rate) {
    opentime::RationalTime rationalTime(value, rate);
    return rationalTime.is_invalid_time();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    add
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_add
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    auto result = thisRT + otherRT;
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    subtract
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_subtract
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    auto result = thisRT - otherRT;
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    rescaledTo
 * Signature: (D)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_rescaledTo__D
        (JNIEnv *env, jobject thisObj, jdouble newRate) {
    auto rt = rationalTimeFromJObject(env, thisObj);
    auto result = rt.rescaled_to(newRate);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    rescaledTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_RationalTime_rescaledTo__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    auto result = thisRT.rescaled_to(otherRT);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    valueRescaledTo
 * Signature: (D)D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_valueRescaledTo__D
        (JNIEnv *env, jobject thisObj, jdouble newRate) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    return thisRT.value_rescaled_to(newRate);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    valueRescaledTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentime_RationalTime_valueRescaledTo__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    return thisRT.value_rescaled_to(otherRT);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    almostEqual
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_almostEqual__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    return thisRT.almost_equal(otherRT);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    almostEqual
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_almostEqual__Lio_opentimeline_opentime_RationalTime_2D
        (JNIEnv *env, jobject thisObj, jobject otherObj, jdouble delta) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    return thisRT.almost_equal(otherRT, delta);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    durationFromStartEndTime
 * Signature: (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_durationFromStartEndTime
        (JNIEnv *env, jclass thisClass, jobject startTimeObj, jobject endTimeObj) {
    auto startTime = rationalTimeFromJObject(env, startTimeObj);
    auto endTime = rationalTimeFromJObject(env, endTimeObj);
    auto result = opentime::RationalTime::duration_from_start_end_time(startTime, endTime);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    isValidTimecodeRate
 * Signature: (D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_isValidTimecodeRate(
        JNIEnv *env, jclass thisClass, jdouble rate) {
    return opentime::RationalTime::is_valid_timecode_rate(rate);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    fromTimecode
 * Signature: (Ljava/lang/String;DLio/opentimeline/opentime/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_fromTimecode
        (JNIEnv *env, jclass thisClass, jstring timecode, jdouble rate, jobject errorStatusObj) {
    auto errorStatusHandle =
            getHandle<opentime::ErrorStatus>(env, errorStatusObj);
    std::string tc = env->GetStringUTFChars(timecode, 0);
    auto result =
            opentime::RationalTime::from_timecode(tc, rate, errorStatusHandle);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    fromTimeString
 * Signature: (Ljava/lang/String;DLio/opentimeline/opentime/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_fromTimeString
        (JNIEnv *env, jclass thisClass, jstring timestring, jdouble rate, jobject errorStatusObj) {
    auto errorStatusHandle =
            getHandle<opentime::ErrorStatus>(env, errorStatusObj);
    std::string ts = env->GetStringUTFChars(timestring, 0);
    auto result =
            opentime::RationalTime::from_time_string(ts, rate, errorStatusHandle);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    toTimecodeNative
 * Signature: (Lio/opentimeline/opentime/RationalTime;DILio/opentimeline/opentime/ErrorStatus;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_io_opentimeline_opentime_RationalTime_toTimecodeNative
        (JNIEnv *env, jclass thisClass, jobject rtObj, jdouble rate, jint dropFrameIndex, jobject errorStatusObj) {
    auto errorStatusHandle =
            getHandle<opentime::ErrorStatus>(env, errorStatusObj);
    auto rt = rationalTimeFromJObject(env, rtObj);
    std::string tc = rt.to_timecode(
            rate, opentime::IsDropFrameRate(dropFrameIndex), errorStatusHandle);
    return env->NewStringUTF(tc.c_str());
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    toTimeString
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_io_opentimeline_opentime_RationalTime_toTimeString
        (JNIEnv *env, jobject thisObj) {
    auto rt = rationalTimeFromJObject(env, thisObj);
    std::string ts = rt.to_time_string();
    return env->NewStringUTF(ts.c_str());
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    equals
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_RationalTime_equals
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    return thisRT == otherRT;
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    compareTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentime_RationalTime_compareTo
        (JNIEnv *env, jobject thisObj, jobject otherObj) {
    auto thisRT = rationalTimeFromJObject(env, thisObj);
    auto otherRT = rationalTimeFromJObject(env, otherObj);
    if (thisRT < otherRT) { return -1; }
    else if (thisRT > otherRT) {
        return 1;
    } else if (thisRT == otherRT) {
        return 0;
    }
    // this should never be possible
    return -99;
}