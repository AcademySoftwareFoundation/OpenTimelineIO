#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_FreezeFrame.h>
#include <opentimelineio/freezeFrame.h>
#include <opentimelineio/version.h>
#include <otio_manager.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

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
                getHandle<AnyDictionary>(env, metadataObj);
        auto freezeFrame = new FreezeFrame(nameStr, *metadataHandle);
        auto effectManager =
                new SerializableObject::Retainer<FreezeFrame>(freezeFrame);
        setHandle(env, thisObj, effectManager);
    }
}
