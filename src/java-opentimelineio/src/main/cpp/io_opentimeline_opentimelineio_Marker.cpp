#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Marker.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    initialize
 * Signature: (Ljava/lang/String;[DLjava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Marker_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      name,
    jdoubleArray markedRangeArray,
    jstring      color,
    jobject      metadata)
{
    if(name == NULL || markedRangeArray == NULL || color == NULL ||
       metadata == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string         nameStr = env->GetStringUTFChars(name, 0);
        opentime::TimeRange markedRange =
            timeRangeFromArray(env, markedRangeArray);
        std::string colorStr = env->GetStringUTFChars(color, 0);
        auto metadataHandle  = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
        auto marker          = new OTIO_NS::Marker(
            nameStr, markedRange, colorStr, *metadataHandle);
        setHandle(env, thisObj, marker);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    getColor
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Marker_getColor(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Marker>(env, thisObj);
    return env->NewStringUTF(thisHandle->color().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    setColor
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Marker_setColor(
    JNIEnv* env, jobject thisObj, jstring color)
{
    if(color == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle = getHandle<OTIO_NS::Marker>(env, thisObj);
        thisHandle->set_color(env->GetStringUTFChars(color, 0));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    getMarkedRangeNative
 * Signature: ()[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_Marker_getMarkedRangeNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Marker>(env, thisObj);
    auto result     = thisHandle->marked_range();
    return timeRangeToArray(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    setMarkedRangeNative
 * Signature: ([D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Marker_setMarkedRangeNative(
    JNIEnv* env, jobject thisObj, jdoubleArray markedRange)
{
    auto thisHandle = getHandle<OTIO_NS::Marker>(env, thisObj);
    auto mr         = timeRangeFromArray(env, markedRange);
    thisHandle->set_marked_range(mr);
}
