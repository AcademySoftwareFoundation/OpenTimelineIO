#include <handle.h>
#include <io_opentimeline_opentime_RationalTime.h>
#include <utilities.h>

#include <opentime/rationalTime.h>
#include <opentime/version.h>

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    isInvalidTimeNative
 * Signature: (DD)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_RationalTime_isInvalidTimeNative(JNIEnv *env,
                                                               jclass thisClass,
                                                               jdouble value,
                                                               jdouble rate) {
    opentime::RationalTime rationalTime(value, rate);
    return rationalTime.is_invalid_time();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    addNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_RationalTime_addNative(JNIEnv *env, jclass thisClass,
                                                     jdoubleArray rationalTime,
                                                     jdoubleArray other) {
    return rationalTimeToArray(env, rationalTimeFromArray(env, rationalTime) + rationalTimeFromArray(env, other));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    subtractNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_RationalTime_subtractNative(JNIEnv *env, jclass thisClass,
                                                          jdoubleArray rationalTime,
                                                          jdoubleArray other) {
    return rationalTimeToArray(env, rationalTimeFromArray(env, rationalTime) - rationalTimeFromArray(env, other));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    rescaledToNative
 * Signature: ([DD)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_RationalTime_rescaledToNative___3DD(JNIEnv *env,
                                                                  jclass thisClass,
                                                                  jdoubleArray rationalTime,
                                                                  jdouble newRate) {
    return rationalTimeToArray(env, rationalTimeFromArray(env, rationalTime).rescaled_to(newRate));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    rescaledToNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_RationalTime_rescaledToNative___3D_3D(
        JNIEnv *env, jclass thisClass, jdoubleArray rationalTime, jdoubleArray other) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    opentime::RationalTime rtOther = rationalTimeFromArray(env, other);
    opentime::RationalTime result = rt.rescaled_to(rtOther);
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    valueRescaledToNative
 * Signature: ([DD)D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentime_RationalTime_valueRescaledToNative___3DD(
        JNIEnv *env, jclass thisClass, jdoubleArray rationalTime, jdouble newRate) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    return rt.value_rescaled_to(newRate);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    valueRescaledToNative
 * Signature: ([D[D)D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_valueRescaledToNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray rationalTime, jdoubleArray other) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    opentime::RationalTime rtOther = rationalTimeFromArray(env, other);
    return rt.value_rescaled_to(rtOther);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    almostEqualNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_RationalTime_almostEqualNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray rationalTime, jdoubleArray other) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    opentime::RationalTime rtOther = rationalTimeFromArray(env, other);
    return rt.almost_equal(rtOther);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    almostEqualNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_RationalTime_almostEqualNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray rationalTime, jdoubleArray other, jdouble delta) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    opentime::RationalTime rtOther = rationalTimeFromArray(env, other);
    return rt.almost_equal(rtOther, delta);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    durationFromStartEndTimeNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_RationalTime_durationFromStartEndTimeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray startTime, jdoubleArray endTime) {
    opentime::RationalTime start = rationalTimeFromArray(env, startTime);
    opentime::RationalTime end = rationalTimeFromArray(env, endTime);
    opentime::RationalTime duration = opentime::RationalTime::duration_from_start_end_time(start, end);
    return rationalTimeToArray(env, duration);
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
 * Method:    fromTimecodeNative
 * Signature: (Ljava/lang/String;DLio/opentimeline/opentime/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_RationalTime_fromTimecodeNative
        (JNIEnv *env, jclass thisClass, jstring timecode, jdouble rate, jobject errorStatusObj) {
    auto errorStatusHandle = getHandle<opentime::ErrorStatus>(env, errorStatusObj);
    std::string tc = env->GetStringUTFChars(timecode, 0);
    opentime::RationalTime result = opentime::RationalTime::from_timecode(tc, rate, errorStatusHandle);
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    fromTimeStringNative
 * Signature: (Ljava/lang/String;DLio/opentimeline/opentime/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_RationalTime_fromTimeStringNative
        (JNIEnv *env, jclass thisClass, jstring timestring, jdouble rate, jobject errorStatusObj) {
    auto errorStatusHandle = getHandle<opentime::ErrorStatus>(env, errorStatusObj);
    std::string ts = env->GetStringUTFChars(timestring, 0);
    opentime::RationalTime result = opentime::RationalTime::from_time_string(ts, rate, errorStatusHandle);
    return rationalTimeToArray(env, result);
}
/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    toTimecodeNative
 * Signature: ([DDILio/opentimeline/opentime/ErrorStatus;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_io_opentimeline_opentime_RationalTime_toTimecodeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray rationalTime, jdouble rate, jint dropFrameIndex,
         jobject errorStatusObj) {
    auto errorStatusHandle = getHandle<opentime::ErrorStatus>(env, errorStatusObj);
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    std::string tc = rt.to_timecode(rate, opentime::IsDropFrameRate(dropFrameIndex), errorStatusHandle);
    return env->NewStringUTF(tc.c_str());
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    toTimeStringNative
 * Signature: ([D)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_io_opentimeline_opentime_RationalTime_toTimeStringNative
        (JNIEnv *env, jclass thisClass, jdoubleArray rationalTime) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    std::string ts = rt.to_time_string();
    return env->NewStringUTF(ts.c_str());
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    compareToNative
 * Signature: ([D[D)I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentime_RationalTime_compareToNative
        (JNIEnv *env, jobject thisObj, jdoubleArray rationalTime, jdoubleArray other) {
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    opentime::RationalTime rtOther = rationalTimeFromArray(env, other);
    if (rt < rtOther) {
        return -1;
    } else if (rt > rtOther) {
        return 1;
    } else if (rt == rtOther) {
        return 0;
    }
    // this should never be possible
    return -99;
}
