#include <handle.h>
#include <io_opentimeline_opentime_TimeRange.h>
#include <utilities.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/version.h>

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    initialize
 * Signature:
 * (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentime_TimeRange_initialize(
    JNIEnv *env, jobject thisObj, jobject startTimeObj, jobject durationObj) {
  auto startTimeHandle = getHandle<opentime::RationalTime>(env, startTimeObj);
  auto durationHandle = getHandle<opentime::RationalTime>(env, durationObj);
  opentime::TimeRange *timeRange =
      new opentime::TimeRange(*startTimeHandle, *durationHandle);
  setHandle(env, thisObj, timeRange);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    getStartTime
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_getStartTime(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto result = thisHandle->start_time();
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    getDuration
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_getDuration(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto result = thisHandle->duration();
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    endTimeInclusive
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeRange_endTimeInclusive(JNIEnv *env,
                                                         jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto result = thisHandle->end_time_inclusive();
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    endTimeExclusive
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeRange_endTimeExclusive(JNIEnv *env,
                                                         jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto result = thisHandle->end_time_exclusive();
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    durationExtendedBy
 * Signature:
 * (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeRange_durationExtendedBy(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  auto result = thisHandle->duration_extended_by(*rationalTimeOtherHandle);
  return timeRangeFromNative(env, new opentime::TimeRange(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    extendedBy
 * Signature:
 * (Lio/opentimeline/opentime/TimeRange;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeRange_extendedBy(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  auto result = thisHandle->extended_by(*timeRangeOtherHandle);
  return timeRangeFromNative(env, new opentime::TimeRange(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    clamped
 * Signature:
 * (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeRange_clamped__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  auto result = thisHandle->clamped(*rationalTimeOtherHandle);
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    clamped
 * Signature:
 * (Lio/opentimeline/opentime/TimeRange;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeRange_clamped__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  auto result = thisHandle->clamped(*timeRangeOtherHandle);
  return timeRangeFromNative(env, new opentime::TimeRange(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    contains
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_contains__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->contains(*rationalTimeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    contains
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_contains__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->contains(*timeRangeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlaps
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_overlaps__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->overlaps(*rationalTimeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlaps
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_overlaps__Lio_opentimeline_opentime_TimeRange_2D(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj, jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->overlaps(*timeRangeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    overlaps
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_overlaps__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->overlaps(*timeRangeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_TimeRange_2D(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj, jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->before(*timeRangeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->before(*timeRangeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_RationalTime_2D(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj,
    jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->before(*rationalTimeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    before
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_before__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->before(*rationalTimeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    meets
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_meets__Lio_opentimeline_opentime_TimeRange_2D(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj, jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->meets(*timeRangeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    meets
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_meets__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->meets(*timeRangeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_TimeRange_2D(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj, jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->begins(*timeRangeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->begins(*timeRangeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_RationalTime_2D(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj,
    jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->begins(*rationalTimeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    begins
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_begins__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->begins(*rationalTimeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/TimeRange;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_TimeRange_2D(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj, jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->finishes(*timeRangeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return thisHandle->finishes(*timeRangeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/RationalTime;D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_RationalTime_2D(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj,
    jdouble epsilon) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->finishes(*rationalTimeOtherHandle, epsilon);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    finishes
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeRange_finishes__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  return thisHandle->finishes(*rationalTimeOtherHandle);
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    equals
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_equals(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return *thisHandle == *timeRangeOtherHandle;
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    notEquals
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeRange_notEquals(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeRange>(env, thisObj);
  auto timeRangeOtherHandle =
      getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  return *thisHandle != *timeRangeOtherHandle;
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    rangeFromStartEndTime
 * Signature:
 * (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeRange_rangeFromStartEndTime(
    JNIEnv *env, jclass thisClass, jobject startTimeObj, jobject endTimeObj) {
  auto startTimeHandle = getHandle<opentime::RationalTime>(env, startTimeObj);
  auto endTimeHandle = getHandle<opentime::RationalTime>(env, endTimeObj);
  auto result = opentime::TimeRange::range_from_start_end_time(*startTimeHandle,
                                                               *endTimeHandle);
  return timeRangeFromNative(env, new opentime::TimeRange(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeRange
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentime_TimeRange_dispose(JNIEnv *env, jobject thisObj) {
  opentime::TimeRange *timeRange = getHandle<opentime::TimeRange>(env, thisObj);
  setHandle<opentime::TimeRange>(env, thisObj, nullptr);
  delete timeRange;
}
