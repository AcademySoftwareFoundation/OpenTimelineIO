#include <handle.h>
#include <io_opentimeline_OTIOFinalizer.h>
#include <class_codes.h>

/*
 * Class:     io_opentimeline_OTIOFinalizer
 * Method:    disposeNativeObject
 * Signature: (JLjava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_OTIOFinalizer_disposeNativeObject(
        JNIEnv *env,
        jobject thisObject,
        jlong nativeHandle,
        jstring nativeClassName) {
    disposeObject(env, nativeHandle, nativeClassName);
}
