#include <handle.h>
#include <io_opentimeline_opentime_TimeTransform.h>
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedToTimeRangeNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedToTimeRangeNative(
    JNIEnv*      env,
    jclass       thisClass,
    jdoubleArray timeTransform,
    jdoubleArray timeRange)
{
    opentime::TimeTransform tt     = timeTransformFromArray(env, timeTransform);
    opentime::TimeRange     tr     = timeRangeFromArray(env, timeRange);
    opentime::TimeRange     result = tt.applied_to(tr);
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedToTimeTransformNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedToTimeTransformNative(
    JNIEnv*      env,
    jclass       thisClass,
    jdoubleArray timeTransform,
    jdoubleArray otherTimeTransform)
{
    opentime::TimeTransform tt = timeTransformFromArray(env, timeTransform);
    opentime::TimeTransform otherTt =
        timeTransformFromArray(env, otherTimeTransform);
    opentime::TimeTransform result = tt.applied_to(otherTt);
    return timeTransformToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedToRationalTimeNative
 * Signature: ([D[D)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedToRationalTimeNative(
    JNIEnv*      env,
    jclass       thisClass,
    jdoubleArray timeTransform,
    jdoubleArray rationalTime)
{
    opentime::TimeTransform tt     = timeTransformFromArray(env, timeTransform);
    opentime::RationalTime  rt     = rationalTimeFromArray(env, rationalTime);
    opentime::RationalTime  result = tt.applied_to(rt);
    return rationalTimeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    equalsNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeTransform_equalsNative(
    JNIEnv*      env,
    jclass       thisClass,
    jdoubleArray timeTransform,
    jdoubleArray otherTimeTransform)
{
    opentime::TimeTransform tt = timeTransformFromArray(env, timeTransform);
    opentime::TimeTransform otherTt =
        timeTransformFromArray(env, otherTimeTransform);
    return tt == otherTt;
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    notEqualsNative
 * Signature: ([D[D)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeTransform_notEqualsNative(
    JNIEnv*      env,
    jclass       thisClass,
    jdoubleArray timeTransform,
    jdoubleArray otherTimeTransform)
{
    opentime::TimeTransform tt = timeTransformFromArray(env, timeTransform);
    opentime::TimeTransform otherTt =
        timeTransformFromArray(env, otherTimeTransform);
    return tt != otherTt;
}
