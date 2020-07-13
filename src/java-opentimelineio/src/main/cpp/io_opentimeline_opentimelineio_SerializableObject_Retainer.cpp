#include <handle.h>
#include <io_opentimeline_opentimelineio_SerializableObject.h>
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
    JNIEnv *, jobject, jobject);

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    value
 * Signature: ()Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_value(
    JNIEnv *, jobject);

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    takeValue
 * Signature: ()Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_takeValue(
    JNIEnv *, jobject);

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject_Retainer
 * Method:    dispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_00024Retainer_dispose(
    JNIEnv *, jobject);
