#include <handle.h>
#include <io_opentimeline_OTIONative.h>
#include <class_codes.h>

/*
 * Class:     io_opentimeline_OTIONative
 * Method:    close
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_OTIONative_close(JNIEnv *env, jobject thisObj) {
    disposeObject(env, thisObj);
}