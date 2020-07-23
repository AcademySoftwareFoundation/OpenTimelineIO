#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Deserialization.h>
#include <opentimelineio/deserialization.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_Deserialization
 * Method:    deserializeJSONFromString
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/Any;Lio/opentimeline/opentimelineio/ErrorStatus;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Deserialization_deserializeJSONFromString(
    JNIEnv* env,
    jclass  thisClass,
    jstring input,
    jobject anyDestination,
    jobject errorStatusObj)
{
    if(anyDestination == nullptr || errorStatusObj == nullptr ||
       input == nullptr)
        throwNullPointerException(env, "");
    else
    {
        std::string inputStr = env->GetStringUTFChars(input, nullptr);
        auto        anyDestinationHandle =
            getHandle<OTIO_NS::any>(env, anyDestination);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        return OTIO_NS::deserialize_json_from_string(
            inputStr, anyDestinationHandle, errorStatusHandle);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Deserialization
 * Method:    deserializeJSONFromFile
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/Any;Lio/opentimeline/opentimelineio/ErrorStatus;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Deserialization_deserializeJSONFromFile(
    JNIEnv* env,
    jclass  thisClass,
    jstring fileName,
    jobject anyDestination,
    jobject errorStatusObj)
{
    if(anyDestination == nullptr || errorStatusObj == nullptr ||
       fileName == nullptr)
        throwNullPointerException(env, "");
    else
    {
        std::string fileNameStr = env->GetStringUTFChars(fileName, nullptr);
        auto        anyDestinationHandle =
            getHandle<OTIO_NS::any>(env, anyDestination);
        auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        return OTIO_NS::deserialize_json_from_string(
            fileNameStr, anyDestinationHandle, errorStatusHandle);
    }
}
