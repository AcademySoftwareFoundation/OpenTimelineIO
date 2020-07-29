#include <handle.h>
#include <io_opentimeline_OTIONative.h>
#include <utilities.h>

#include <opentime/errorStatus.h>
#include <opentimelineio/any.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/version.h>
#include <otio_manager.h>
#include <class_codes.h>

/*
 * Class:     io_opentimeline_OTIONative
 * Method:    close
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_OTIONative_close(JNIEnv *env, jobject thisObj) {
    jclass thisClass = env->GetObjectClass(thisObj);
    jfieldID nativeHandleID = env->GetFieldID(thisClass, "nativeHandle", "J");
    jfieldID classNameID =
            env->GetFieldID(thisClass, "className", "Ljava/lang/String;");

    jlong nativeHandle = env->GetLongField(thisObj, nativeHandleID);
    jstring className = (jstring) env->GetObjectField(thisObj, classNameID);

    std::string classNameStr = env->GetStringUTFChars(className, 0);
    switch (stringToClassCode[classNameStr]) {
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