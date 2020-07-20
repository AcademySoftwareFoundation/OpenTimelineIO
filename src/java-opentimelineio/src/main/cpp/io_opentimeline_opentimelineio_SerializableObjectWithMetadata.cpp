#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_SerializableObjectWithMetadata.h>
#include <opentimelineio/serializableObjectWithMetadata.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_initialize(
    JNIEnv* env, jobject thisObj, jstring name, jobject metadataObj)
{
    if(name == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto        metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        OTIO_NS::SerializableObjectWithMetadata*
            serializableObjectWithMetadata =
                new OTIO_NS::SerializableObjectWithMetadata(
                    nameStr, *metadataHandle);
        setHandle(env, thisObj, serializableObjectWithMetadata);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    getName
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_getName(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle =
        getHandle<OTIO_NS::SerializableObjectWithMetadata>(env, thisObj);
    return env->NewStringUTF(thisHandle->name().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    setName
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_setName(
    JNIEnv* env, jobject thisObj, jstring name)
{
    if(name == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle =
            getHandle<OTIO_NS::SerializableObjectWithMetadata>(env, thisObj);
        thisHandle->set_name(env->GetStringUTFChars(name, 0));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    getMetadata
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_getMetadata(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle =
        getHandle<OTIO_NS::SerializableObjectWithMetadata>(env, thisObj);
    return anyDictionaryFromNative(
        env, new OTIO_NS::AnyDictionary(thisHandle->metadata()));
}
