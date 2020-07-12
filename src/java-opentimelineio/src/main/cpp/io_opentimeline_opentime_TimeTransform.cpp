#include <handle.h>
#include <io_opentimeline_opentime_TimeTransform.h>
#include <utilities.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentime/RationalTime;DD)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentime_TimeTransform_initialize(
    JNIEnv *env, jobject thisObj, jobject offsetObj, jdouble scale,
    jdouble rate) {
  auto offsetHandle = getHandle<opentime::RationalTime>(env, offsetObj);
  opentime::TimeTransform *timeTransform =
      new opentime::TimeTransform(*offsetHandle, scale, rate);
  setHandle(env, thisObj, timeTransform);
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    getOffset
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_TimeTransform_getOffset(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  auto result = thisHandle->offset();
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    getScale
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_TimeTransform_getScale(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  return thisHandle->scale();
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    getRate
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_TimeTransform_getRate(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  return thisHandle->rate();
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedTo
 * Signature:
 * (Lio/opentimeline/opentime/TimeRange;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedTo__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  auto timeRangeOtherHandle = getHandle<opentime::TimeRange>(env, timeRangeOtherObj);
  auto result = thisHandle->applied_to(*timeRangeOtherHandle);
  return timeRangeFromNative(env, new opentime::TimeRange(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedTo
 * Signature:
 * (Lio/opentimeline/opentime/TimeTransform;)Lio/opentimeline/opentime/TimeTransform;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedTo__Lio_opentimeline_opentime_TimeTransform_2(
    JNIEnv *env, jobject thisObj, jobject timeTransformOtherObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  auto timeTransformOtherHandle =
      getHandle<opentime::TimeTransform>(env, timeTransformOtherObj);
  auto result = thisHandle->applied_to(*timeTransformOtherHandle);
  return timeTransformFromNative(env, new opentime::TimeTransform(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedTo
 * Signature:
 * (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedTo__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeOtherObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  auto rationalTimeOtherHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeOtherObj);
  auto result = thisHandle->applied_to(*rationalTimeOtherHandle);
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    equals
 * Signature: (Lio/opentimeline/opentime/TimeTransform;)Z
 */
JNIEXPORT jboolean JNICALL Java_io_opentimeline_opentime_TimeTransform_equals(
    JNIEnv *env, jobject thisObj, jobject otherObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  auto otherHandle = getHandle<opentime::TimeTransform>(env, otherObj);
  return *thisHandle == *otherHandle;
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    notEquals
 * Signature: (Lio/opentimeline/opentime/TimeTransform;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeTransform_notEquals(JNIEnv *env,
                                                      jobject thisObj,
                                                      jobject otherObj) {
  auto thisHandle = getHandle<opentime::TimeTransform>(env, thisObj);
  auto otherHandle = getHandle<opentime::TimeTransform>(env, otherObj);
  return *thisHandle != *otherHandle;
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentime_TimeTransform_dispose(
    JNIEnv *env, jobject thisObj) {
  opentime::TimeTransform *timeTransform =
      getHandle<opentime::TimeTransform>(env, thisObj);
  setHandle<opentime::TimeTransform>(env, thisObj, nullptr);
  delete timeTransform;
}
