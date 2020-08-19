#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_UnknownSchema.h>
#include <opentimelineio/unknownSchema.h>
#include <opentimelineio/version.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    initialize
 * Signature: (Ljava/lang/String;I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring originalSchemaName,
        jint originalSchemaVersion) {
    if (originalSchemaName == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string originalSchemaNameStr =
                env->GetStringUTFChars(originalSchemaName, 0);
        auto unknownSchema = new OTIO_NS::UnknownSchema(
                originalSchemaNameStr, originalSchemaVersion);
        auto unknownSchemaManager =
                new SerializableObject::Retainer<UnknownSchema>(unknownSchema);
        setHandle(env, thisObj, unknownSchemaManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    getOriginalSchemaName
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_getOriginalSchemaName(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<UnknownSchema>>(env, thisObj);
    auto unknownSchema = thisHandle->value;
    return env->NewStringUTF(unknownSchema->original_schema_name().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    getOriginalSchemaVersion
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_getOriginalSchemaVersion(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<UnknownSchema>>(env, thisObj);
    auto unknownSchema = thisHandle->value;
    return unknownSchema->original_schema_version();
}

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    isUnknownSchema
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_isUnknownSchema(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<UnknownSchema>>(env, thisObj);
    auto unknownSchema = thisHandle->value;
    return unknownSchema->is_unknown_schema();
}
