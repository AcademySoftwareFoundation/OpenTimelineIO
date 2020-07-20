#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_TimeEffect.h>
#include <opentimelineio/timeEffect.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_TimeEffect
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_TimeEffect_initialize(
    JNIEnv* env,
    jobject thisObj,
    jstring name,
    jstring effectName,
    jobject metadataObj)
{
    std::string nameStr       = env->GetStringUTFChars(name, 0);
    std::string effectNameStr = env->GetStringUTFChars(effectName, 0);
    auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
    auto effect =
        new OTIO_NS::TimeEffect(nameStr, effectNameStr, *metadataHandle);
    setHandle(env, thisObj, effect);
}
