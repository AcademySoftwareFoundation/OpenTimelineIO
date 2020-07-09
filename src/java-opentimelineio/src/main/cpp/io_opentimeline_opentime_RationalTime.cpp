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
        (JNIEnv *env, jobject thisObject, jdouble value, jdouble rate) {
    opentime::RationalTime *rationalTime = new opentime::RationalTime(value, rate);
    setHandle(env, thisObject, rationalTime);
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    getValue
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_getValue
        (JNIEnv *env, jobject thisObject) {
    auto objectHandle = getHandle<opentime::RationalTime>(env, thisObject);
    return objectHandle->value();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    getRate
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL Java_io_opentimeline_opentime_RationalTime_getRate
        (JNIEnv *env, jobject thisObject) {
    auto objectHandle = getHandle<opentime::RationalTime>(env, thisObject);
    return objectHandle->rate();
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    add
 * Signature: (Lio/opentimeline/opentime/RationalTime;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL Java_io_opentimeline_opentime_RationalTime_add
        (JNIEnv *env, jobject thisObject, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObject);
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
        (JNIEnv *env, jobject thisObject, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObject);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    auto result = (*thisHandle - *otherHandle);
    return rationalTimeFromNative(env, new opentime::RationalTime(result));
}

/*
 * Class:     io_opentimeline_opentime_RationalTime
 * Method:    compareTo
 * Signature: (Lio/opentimeline/opentime/RationalTime;)I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentime_RationalTime_compareTo
        (JNIEnv *env, jobject thisObject, jobject otherObject) {
    auto thisHandle = getHandle<opentime::RationalTime>(env, thisObject);
    auto otherHandle = getHandle<opentime::RationalTime>(env, otherObject);
    if (thisHandle < otherHandle)
        return -1;
    else if (thisHandle > otherHandle)
        return 1;
    else if (thisHandle == otherHandle)
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
        (JNIEnv *env, jobject thisObject) {
    opentime::RationalTime *rationalTime = getHandle<opentime::RationalTime>(env, thisObject);
    setHandle<opentime::RationalTime>(env, thisObject, nullptr);
    delete rationalTime;
}
