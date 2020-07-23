#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Marker.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentime/TimeRange;Ljava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Marker_initialize(
    JNIEnv* env,
    jobject thisObj,
    jstring name,
    jobject markedRangeObj,
    jstring color,
    jobject metadataObj)
{
    if(name == NULL || markedRangeObj == NULL || color == NULL ||
       metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string         nameStr = env->GetStringUTFChars(name, 0);
        opentime::TimeRange markedRange =
            timeRangeFromJObject(env, markedRangeObj);
        std::string colorStr = env->GetStringUTFChars(color, 0);
        auto        metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto marker = new OTIO_NS::Marker(
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
 * Method:    getMarkedRange
 * Signature: ()Lio/opentimeline/opentime/TimeRange;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Marker_getMarkedRange(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Marker>(env, thisObj);
    auto result     = thisHandle->marked_range();
    return timeRangeToJObject(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Marker
 * Method:    setMarkedRange
 * Signature: (Lio/opentimeline/opentime/TimeRange;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Marker_setMarkedRange(
    JNIEnv* env, jobject thisObj, jobject markedRangeObj)
{
    auto thisHandle = getHandle<OTIO_NS::Marker>(env, thisObj);
    auto mr         = timeRangeFromJObject(env, markedRangeObj);
    thisHandle->set_marked_range(mr);
}
