#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_FreezeFrame.h>
#include <opentimelineio/freezeFrame.h>
#include <opentimelineio/version.h>
#include <otio_manager.h>

/*
 * Class:     io_opentimeline_opentimelineio_FreezeFrame
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_FreezeFrame_initialize(
        JNIEnv *env, jobject thisObj, jstring name, jobject metadataObj) {
    if (name == nullptr || metadataObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto metadataHandle =
                getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto freezeFrame = new OTIO_NS::FreezeFrame(nameStr, *metadataHandle);
        auto effectManager =
                new managing_ptr<OTIO_NS::FreezeFrame>(env, freezeFrame);
        setHandle(env, thisObj, effectManager);
    }
}
