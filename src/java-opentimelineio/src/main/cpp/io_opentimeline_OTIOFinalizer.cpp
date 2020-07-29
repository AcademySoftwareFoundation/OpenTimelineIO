#include <handle.h>
#include <io_opentimeline_OTIOFinalizer.h>
#include <utilities.h>

#include <opentimelineio/any.h>
#include <opentimelineio/version.h>
#include <otio_manager.h>
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
    std::string className = env->GetStringUTFChars(nativeClassName, 0);
    switch (stringToClassCode[className]) {
        case _Any: {
            auto obj = reinterpret_cast<OTIO_NS::any *>(nativeHandle);
            delete obj;
            break;
        }
        case _OpenTimeErrorStatus: {
            auto obj = reinterpret_cast<opentime::ErrorStatus *>(nativeHandle);
            delete obj;
            break;
        }
        case _OTIOErrorStatus: {
            auto obj = reinterpret_cast<OTIO_NS::ErrorStatus *>(nativeHandle);
            delete obj;
            break;
        }
        case _SerializableObject: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::SerializableObject> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _SerializableObjectWithMetadata: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::SerializableObjectWithMetadata> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Composable: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Composable> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        default:
            throwRuntimeException(env, "Could not find class.");
    }
}
