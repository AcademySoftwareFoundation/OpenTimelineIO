#include <handle.h>
#include <io_opentimeline_opentimelineio_SerializableObject_Retainer.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    initialize
 * Signature: (Lio/opentimeline/opentimelineio/SerializableObject;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_initialize(
    JNIEnv* env, jobject thisObj, jobject)
{
    auto serializableObjectRetainer =
        new OTIO_NS::SerializableObject::Retainer<>();
    setHandle(env, thisObj, serializableObjectRetainer);
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    value
 * Signature: ()Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_value(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<
        OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>(
        env, thisObj);
    return serializableObjectFromNative(env, thisHandle->value);
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    takeValue
 * Signature: ()Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_takeValue(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<
        OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>(
        env, thisObj);
    return serializableObjectFromNative(env, thisHandle->take_value());
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_dispose(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<
        OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>(
        env, thisObj);
    delete thisHandle;
    setHandle<
        OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>(
        env, thisObj, nullptr);
}
