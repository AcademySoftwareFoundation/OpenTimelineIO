#include <handle.h>
#include <io_opentimeline_opentimelineio_Any.h>
#include <utilities.h>

#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>
#include <opentimelineio/any.h>
#include <opentimelineio/safely_typed_any.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (Z)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_Any_initialize__Z(
    JNIEnv *env, jobject thisObj, jboolean boolParam) {

  OTIO_NS::any anyValue =
      OTIO_NS::create_safely_typed_any(std::move(boolParam));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (I)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_Any_initialize__I(
    JNIEnv *env, jobject thisObj, jint intParam) {
  OTIO_NS::any anyValue = OTIO_NS::create_safely_typed_any(std::move(intParam));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (D)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_Any_initialize__D(
    JNIEnv *env, jobject thisObj, jdouble doubleParam) {
  OTIO_NS::any anyValue =
      OTIO_NS::create_safely_typed_any(std::move(doubleParam));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initialize__Ljava_lang_String_2(
    JNIEnv *env, jobject thisObj, jstring stringParam) {
  std::string stringVal = env->GetStringUTFChars(stringParam, 0);
  OTIO_NS::any anyValue =
      OTIO_NS::create_safely_typed_any(std::move(stringVal));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentime/RationalTime;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initialize__Lio_opentimeline_opentime_RationalTime_2(
    JNIEnv *env, jobject thisObj, jobject rationalTimeObj) {
  auto rationalTimeHandle =
      getHandle<opentime::RationalTime>(env, rationalTimeObj);
  OTIO_NS::any anyValue =
      OTIO_NS::create_safely_typed_any(std::move(*rationalTimeHandle));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentime/TimeRange;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initialize__Lio_opentimeline_opentime_TimeRange_2(
    JNIEnv *env, jobject thisObj, jobject timeRangeObj) {
  auto timeRangeHandle = getHandle<opentime::TimeRange>(env, timeRangeObj);
  OTIO_NS::any anyValue =
      OTIO_NS::create_safely_typed_any(std::move(*timeRangeHandle));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentime/TimeTransform;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_initialize__Lio_opentimeline_opentime_TimeTransform_2(
    JNIEnv *env, jobject thisObj, jobject timeTransformObj) {
  auto timeTransformHandle =
      getHandle<opentime::TimeTransform>(env, timeTransformObj);
  OTIO_NS::any anyValue =
      OTIO_NS::create_safely_typed_any(std::move(*timeTransformHandle));
  setHandle(env, thisObj, new OTIO_NS::any(anyValue));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastBoolean
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastBoolean(JNIEnv *env,
                                                          jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  return OTIO_NS::safely_cast_bool_any(*thisHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastInt
 * Signature: ()I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentimelineio_Any_safelyCastInt(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  return OTIO_NS::safely_cast_int_any(*thisHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastDouble
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastDouble(JNIEnv *env,
                                                         jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  return OTIO_NS::safely_cast_double_any(*thisHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastString
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastString(JNIEnv *env,
                                                         jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  return env->NewStringUTF(
      OTIO_NS::safely_cast_string_any(*thisHandle).c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastRationalTime
 * Signature: ()Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastRationalTime(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  auto result = OTIO_NS::safely_cast_rational_time_any(*thisHandle);
  return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastTimeRange
 * Signature: ()Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastTimeRange(JNIEnv *env,
                                                            jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  auto result = OTIO_NS::safely_cast_time_range_any(*thisHandle);
  return timeRangeFromNative(env, new opentime::TimeRange(result));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    safelyCastTimeTransform
 * Signature: ()Lio/opentimeline/opentime/TimeTransform;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Any_safelyCastTimeTransform(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::any>(env, thisObj);
  auto result = OTIO_NS::safely_cast_time_transform_any(*thisHandle);
  return timeTransformFromNative(env, new opentime::TimeTransform(result));
}

/*
 * Class:     io_opentimeline_opentimelineio_Any
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Any_dispose(JNIEnv *env, jobject thisObj) {
  OTIO_NS::any *anyVal = getHandle<OTIO_NS::any>(env, thisObj);
  setHandle<OTIO_NS::any>(env, thisObj, nullptr);
  delete anyVal;
}
