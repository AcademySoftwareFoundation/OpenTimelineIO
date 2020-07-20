#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_GeneratorReference.h>
#include <opentimelineio/generatorReference.h>
#include <opentimelineio/optional.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_GeneratorReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;[DLio/opentimeline/opentimelineio/AnyDictionary;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_GeneratorReference_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      name,
    jstring      generatorKind,
    jdoubleArray availableRangeArray,
    jobject      parameters,
    jobject      metadata)
{
    if(name == NULL || generatorKind == NULL || availableRangeArray == NULL ||
       parameters == NULL || metadata == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr          = env->GetStringUTFChars(name, 0);
        std::string generatorKindStr = env->GetStringUTFChars(generatorKind, 0);
        OTIO_NS::optional<opentime::TimeRange> availableRange =
            OTIO_NS::nullopt;
        if(env->GetArrayLength(availableRangeArray) != 0)
        { availableRange = timeRangeFromArray(env, availableRangeArray); }
        auto parametersHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, parameters);
        auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
        auto generatorReference = new OTIO_NS::GeneratorReference(
            nameStr,
            generatorKindStr,
            availableRange,
            *parametersHandle,
            *metadataHandle);
        setHandle(env, thisObj, generatorReference);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_GeneratorReference
 * Method:    getGeneratorKind
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_GeneratorReference_getGeneratorKind(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::GeneratorReference>(env, thisObj);
    return env->NewStringUTF(thisHandle->generator_kind().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_GeneratorReference
 * Method:    setGeneratorKind
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_GeneratorReference_setGeneratorKind(
    JNIEnv* env, jobject thisObj, jstring generatorKind)
{
    if(generatorKind == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle = getHandle<OTIO_NS::GeneratorReference>(env, thisObj);
        std::string generatorKindStr = env->GetStringUTFChars(generatorKind, 0);
        thisHandle->set_generator_kind(generatorKindStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_GeneratorReference
 * Method:    getParameters
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_GeneratorReference_getParameters(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::GeneratorReference>(env, thisObj);
    return anyDictionaryFromNative(env, &(thisHandle->parameters()));
}
