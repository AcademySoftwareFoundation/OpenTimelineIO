#include <handle.h>
#include <io_opentimeline_opentime_TimeRange.h>
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    endTimeInclusive
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_endTimeInclusive
        (JNIEnv *env, jobject thisObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto result = tr.end_time_inclusive();
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    endTimeExclusive
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_endTimeExclusive
        (JNIEnv *env, jobject thisObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto result = tr.end_time_exclusive();
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    durationExtendedBy
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_durationExtendedBy
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto other = rationalTimeFromJObject(env, otherRationalTimeObj);
    auto result = tr.duration_extended_by(other);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    extendedBy
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_extendedBy
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    auto result = tr.extended_by(otherTr);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    clamped
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_clamped__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    auto result = tr.clamped(rt);
    return rationalTimeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    clamped
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_clamped__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    auto result = tr.clamped(otherTr);
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    contains
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_contains__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.contains(rt);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    contains
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_contains__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.contains(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlaps
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_overlaps__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.overlaps(rt);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlaps
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_overlaps__Lio_opentimeline_opentime_TimeRange_2D
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.overlaps(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlaps
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_overlaps__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.overlaps(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_TimeRange_2D
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.before(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.before(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_RationalTime_2D
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.before(rt, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.before(rt);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    meets
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_meets__Lio_opentimeline_opentime_TimeRange_2D
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.meets(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    meets
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_meets__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.meets(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_TimeRange_2D
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.begins(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.begins(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_RationalTime_2D
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.begins(rt, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.begins(rt);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_TimeRange_2D
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.finishes(otherTr, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_TimeRange_2
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr.finishes(otherTr);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_RationalTime_2D
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj, jdouble epsilon) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.finishes(rt, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_RationalTime_2
        (JNIEnv *env, jobject thisObj, jobject otherRationalTimeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto rt = rationalTimeFromJObject(env, otherRationalTimeObj);
    return tr.finishes(rt);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    equals
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_equals
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr == otherTr;
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    notEquals
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_notEquals
        (JNIEnv *env, jobject thisObj, jobject otherTimeRangeObj) {
    auto tr = timeRangeFromJObject(env, thisObj);
    auto otherTr = timeRangeFromJObject(env, otherTimeRangeObj);
    return tr != otherTr;
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    rangeFromStartEndTime
 * Signature: (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_rangeFromStartEndTime
        (JNIEnv *env, jclass thisClass, jobject startRationalTimeObj, jobject endRationalTimeObj) {
    auto startRT = rationalTimeFromJObject(env, startRationalTimeObj);
    auto endRT = rationalTimeFromJObject(env, endRationalTimeObj);
    auto result = opentime::TimeRange::range_from_start_end_time(startRT, endRT);
    return timeRangeToJObject(env, result);
}