#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Serialization.h>
#include <opentimelineio/serialization.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Serialization
 * Method:    serializeJSONToStringNative
 * Signature: (Lio/opentimeline/opentimelineio/Any;Lio/opentimeline/opentimelineio/ErrorStatus;I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Serialization_serializeJSONToStringNative(
    JNIEnv* env,
    jclass  thisClass,
    jobject anyValueObj,
    jobject errorStatusObj,
    jint    indent)
{
    if(anyValueObj == nullptr || errorStatusObj == nullptr)
        throwNullPointerException(env, "");
    else
    {
        auto anyValueHandle = getHandle<OTIO_NS::any>(env, anyValueObj);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        return env->NewStringUTF(OTIO_NS::serialize_json_to_string(
                                     anyValueHandle, errorStatusHandle, indent)
                                     .c_str());
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Serialization
 * Method:    serializeJSONToFileNative
 * Signature: (Lio/opentimeline/opentimelineio/Any;Ljava/lang/String;Lio/opentimeline/opentimelineio/ErrorStatus;I)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Serialization_serializeJSONToFileNative(
    JNIEnv* env,
    jclass  thisClass,
    jobject anyValueObj,
    jstring fileName,
    jobject errorStatusObj,
    jint    indent)
{
    if(anyValueObj == nullptr || fileName == nullptr ||
       errorStatusObj == nullptr)
        throwNullPointerException(env, "");
    else
    {
        auto anyValueHandle = getHandle<OTIO_NS::any>(env, anyValueObj);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        std::string fileNameStr = env->GetStringUTFChars(fileName, nullptr);
        return OTIO_NS::serialize_json_to_file(
            anyValueHandle, fileNameStr, errorStatusHandle, indent);
    }
}
