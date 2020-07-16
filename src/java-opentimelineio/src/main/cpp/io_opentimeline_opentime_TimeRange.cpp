#include <handle.h>
#include <io_opentimeline_opentime_TimeRange.h>
#include <utilities.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/version.h>

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    endTimeInclusiveNative
 * Signature: ([D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_endTimeInclusiveNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime result = tr.end_time_inclusive();
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    endTimeExclusiveNative
 * Signature: ([D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_endTimeExclusiveNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime result = tr.end_time_exclusive();
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    durationExtendedByNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_durationExtendedByNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    opentime::TimeRange result = tr.duration_extended_by(other);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    extendedByNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_extendedByNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    opentime::TimeRange result = tr.extended_by(otherTr);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    clampedRationalTimeNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_clampedRationalTimeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    opentime::RationalTime result = tr.clamped(other);
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    clampedTimeRangeNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_clampedTimeRangeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    opentime::TimeRange result = tr.clamped(otherTr);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    containsRationalTimeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_containsRationalTimeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.contains(other);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    containsTimeRangeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_containsTimeRangeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.contains(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlapsRationalTimeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_overlapsRationalTimeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.overlaps(other);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlapsTimeRangeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_overlapsTimeRangeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.overlaps(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlapsTimeRangeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_overlapsTimeRangeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.overlaps(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beforeTimeRangeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beforeTimeRangeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.before(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beforeTimeRangeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beforeTimeRangeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.before(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beforeRationalTimeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beforeRationalTimeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.before(other, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beforeRationalTimeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beforeRationalTimeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.before(other);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    meetsNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_meetsNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.meets(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    meetsNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_meetsNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.meets(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beginsTimeRangeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beginsTimeRangeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.begins(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beginsTimeRangeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beginsTimeRangeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.begins(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beginsRationalTimeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beginsRationalTimeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.begins(other, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    beginsRationalTimeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_beginsRationalTimeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.begins(other);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishesTimeRangeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishesTimeRangeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.finishes(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishesTimeRangeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishesTimeRangeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr.finishes(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishesRationalTimeNative
 * Signature: ([D[DD)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishesRationalTimeNative___3D_3DD
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime, jdouble epsilon) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.finishes(other, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishesRationalTimeNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishesRationalTimeNative___3D_3D
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherRationalTime) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::RationalTime other = rationalTimeFromArray(env, otherRationalTime);
    return tr.finishes(other);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    equalsNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_equalsNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr == otherTr;
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    notEqualsNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_notEqualsNative
        (JNIEnv *env, jclass thisClass, jdoubleArray timeRange, jdoubleArray otherTimeRange) {
    opentime::TimeRange tr = timeRangeFromArray(env, timeRange);
    opentime::TimeRange otherTr = timeRangeFromArray(env, otherTimeRange);
    return tr != otherTr;
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    rangeFromStartEndTimeNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL Java_io_opentimeline_opentime_TimeRange_rangeFromStartEndTimeNative
        (JNIEnv *env, jclass thisClass, jdoubleArray startRationalTime, jdoubleArray endRationalTime){
    opentime::RationalTime startTime = rationalTimeFromArray(env, startRationalTime);
    opentime::RationalTime endTime = rationalTimeFromArray(env, endRationalTime);
    opentime::TimeRange result = opentime::TimeRange::range_from_start_end_time(startTime, endTime);
    return timeRangeToArray(env, result);
}
