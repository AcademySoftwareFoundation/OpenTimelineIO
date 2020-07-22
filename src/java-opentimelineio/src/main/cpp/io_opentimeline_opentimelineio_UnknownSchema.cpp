#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_UnknownSchema.h>
#include <opentimelineio/unknownSchema.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    initialize
 * Signature: (Ljava/lang/String;I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_initialize(
    JNIEnv* env,
    jobject thisObj,
    jstring originalSchemaName,
    jint    originalSchemaVersion)
{
    if(originalSchemaName == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string originalSchemaNameStr =
            env->GetStringUTFChars(originalSchemaName, 0);
        auto unknownSchema = new OTIO_NS::UnknownSchema(
            originalSchemaNameStr, originalSchemaVersion);
        setHandle(env, thisObj, unknownSchema);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    getOriginalSchemaName
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_getOriginalSchemaName(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::UnknownSchema>(env, thisObj);
    return env->NewStringUTF(thisHandle->original_schema_name().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    getOriginalSchemaVersion
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_getOriginalSchemaVersion(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::UnknownSchema>(env, thisObj);
    return thisHandle->original_schema_version();
}

/*
 * Class:     io_opentimeline_opentimelineio_UnknownSchema
 * Method:    isUnknownSchema
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_UnknownSchema_isUnknownSchema(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::UnknownSchema>(env, thisObj);
    return thisHandle->is_unknown_schema();
}
