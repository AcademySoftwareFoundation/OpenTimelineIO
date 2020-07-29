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
        JNIEnv *env, jobject thisObj, jstring name, jobject metadataObj) {
    if (name == nullptr || metadataObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto metadataHandle =
                getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto serializableObjectWithMetadata =
                new OTIO_NS::SerializableObjectWithMetadata(
                        nameStr, *metadataHandle);
        auto serializableObjectWithMetadataManager =
                new managing_ptr<OTIO_NS::SerializableObjectWithMetadata>(env, serializableObjectWithMetadata);
        setHandle(env, thisObj, serializableObjectWithMetadataManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    getName
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_getName(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::SerializableObjectWithMetadata>>(env, thisObj);
    auto serializableObjectWithMetadata = thisHandle->get();
    return env->NewStringUTF(serializableObjectWithMetadata->name().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    setName
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_setName(
        JNIEnv *env, jobject thisObj, jstring name) {
    if (name == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableObjectWithMetadata>>(env, thisObj);
        auto serializableObjectWithMetadata = thisHandle->get();
        serializableObjectWithMetadata->set_name(env->GetStringUTFChars(name, 0));
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    getMetadata
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_getMetadata(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::SerializableObjectWithMetadata>>(env, thisObj);
    auto serializableObjectWithMetadata = thisHandle->get();
    return anyDictionaryFromNative(env, &(serializableObjectWithMetadata->metadata()));
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObjectWithMetadata
 * Method:    setMetadata
 * Signature: (Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObjectWithMetadata_setMetadata(
        JNIEnv *env, jobject thisObj, jobject metadataObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::SerializableObjectWithMetadata>>(env, thisObj);
    auto serializableObjectWithMetadata = thisHandle->get();
    auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
    serializableObjectWithMetadata->metadata() = *metadataHandle;
}
