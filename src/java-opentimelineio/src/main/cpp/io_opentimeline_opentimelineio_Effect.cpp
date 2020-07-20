#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Effect.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Effect
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Effect_initialize(
    JNIEnv* env,
    jobject thisObj,
    jstring name,
    jstring effectName,
    jobject metadataObj)
{
    if(name == NULL || effectName == NULL || metadataObj == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string nameStr       = env->GetStringUTFChars(name, 0);
        std::string effectNameStr = env->GetStringUTFChars(effectName, 0);
        auto        metadataHandle =
            getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto effect =
            new OTIO_NS::Effect(nameStr, effectNameStr, *metadataHandle);
        setHandle(env, thisObj, effect);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Effect
 * Method:    getEffectName
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_Effect_getEffectName(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::Effect>(env, thisObj);
    return env->NewStringUTF(thisHandle->effect_name().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_Effect
 * Method:    setEffectName
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Effect_setEffectName(
    JNIEnv* env, jobject thisObj, jstring effectName)
{
    if(effectName == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle = getHandle<OTIO_NS::Effect>(env, thisObj);
        thisHandle->set_effect_name(env->GetStringUTFChars(effectName, 0));
    }
}
