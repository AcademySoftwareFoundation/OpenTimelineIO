#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_Composable.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_Composable
 * Method:    initialize
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_Composable_initialize(
        JNIEnv *env, jobject thisObj, jstring name, jobject metadataObj) {
    if (name == nullptr || metadataObj == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto metadataHandle =
                getHandle<OTIO_NS::AnyDictionary>(env, metadataObj);
        auto composable = new OTIO_NS::Composable(nameStr, *metadataHandle);
        auto composableManager =
                new managing_ptr<OTIO_NS::Composable>(env, composable);
        setHandle(env, thisObj, composableManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_Composable
 * Method:    isVisible
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Composable_isVisible(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Composable>>(env, thisObj);
    auto composable = thisHandle->get();
    return composable->visible();
}

/*
 * Class:     io_opentimeline_opentimelineio_Composable
 * Method:    isOverlapping
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_Composable_isOverlapping(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Composable>>(env, thisObj);
    auto composable = thisHandle->get();
    return composable->overlapping();
}

/*
 * Class:     io_opentimeline_opentimelineio_Composable
 * Method:    parent
 * Signature: ()Lio/opentimeline/opentimelineio/Composition;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Composable_parent(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::Composable>>(env, thisObj);
    auto composable = thisHandle->get();
    auto result = composable->parent();
    if (result == nullptr)return nullptr;
    return compositionFromNative(env, result);
}

/*
 * Class:     io_opentimeline_opentimelineio_Composable
 * Method:    getDuration
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_Composable_getDuration(
        JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
    if (errorStatusObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::Composable>>(env, thisObj);
        auto composable = thisHandle->get();
        auto errorStatusHandle =
                getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto duration = composable->duration(errorStatusHandle);
        return rationalTimeToJObject(env, duration);
    }
}