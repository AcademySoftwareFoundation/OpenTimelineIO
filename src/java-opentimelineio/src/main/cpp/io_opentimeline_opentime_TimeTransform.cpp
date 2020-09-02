#include <handle.h>
#include <io_opentimeline_opentime_TimeTransform.h>
#include <opentime/timeTransform.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedTo
 * Signature: (Lio/opentimeline/opentime/TimeRange;)Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedTo__Lio_opentimeline_opentime_TimeRange_2(
        JNIEnv *env, jobject thisObj, jobject timeRange) {
    if (timeRange == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    } else {
        auto tt = timeTransformFromJObject(env, thisObj);
        auto tr = timeRangeFromJObject(env, timeRange);
        auto result = tt.applied_to(tr);
        return timeRangeToJObject(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedTo
 * Signature: (Lio/opentimeline/opentime/TimeTransform;)Lio/opentimeline/opentime/TimeTransform;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedTo__Lio_opentimeline_opentime_TimeTransform_2(
        JNIEnv *env, jobject thisObj, jobject otherTimeTransform) {
    if (otherTimeTransform == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    } else {
        auto tt = timeTransformFromJObject(env, thisObj);
        auto otherTT = timeTransformFromJObject(env, otherTimeTransform);
        auto result = tt.applied_to(otherTT);
        return timeTransformToJObject(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    appliedTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentime_TimeTransform_appliedTo__Lio_opentimeline_opentime_RationalTime_2(
        JNIEnv *env, jobject thisObj, jobject rationalTimeObj) {
    if (rationalTimeObj == nullptr) {
        throwNullPointerException(env, "");
        return nullptr;
    } else {
        auto tt = timeTransformFromJObject(env, thisObj);
        auto rt = rationalTimeFromJObject(env, rationalTimeObj);
        auto result = tt.applied_to(rt);
        return rationalTimeToJObject(env, result);
    }
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    equals
 * Signature: (Lio/opentimeline/opentime/TimeTransform;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeTransform_equals(
        JNIEnv *env, jobject thisObj, jobject otherTimeTransform) {
    if (otherTimeTransform == nullptr) {
        throwNullPointerException(env, "");
        return false;
    }
    auto tt = timeTransformFromJObject(env, thisObj);
    auto otherTT = timeTransformFromJObject(env, otherTimeTransform);
    return tt == otherTT;
}

/*
 * Class:     io_opentimeline_opentime_TimeTransform
 * Method:    notEquals
 * Signature: (Lio/opentimeline/opentime/TimeTransform;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentime_TimeTransform_notEquals(
        JNIEnv *env, jobject thisObj, jobject otherTimeTransform) {
    if (otherTimeTransform == nullptr) {
        throwNullPointerException(env, "");
        return false;
    }
    auto tt = timeTransformFromJObject(env, thisObj);
    auto otherTT = timeTransformFromJObject(env, otherTimeTransform);
    return tt != otherTT;
}