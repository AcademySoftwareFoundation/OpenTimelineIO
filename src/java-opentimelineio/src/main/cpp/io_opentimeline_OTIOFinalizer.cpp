#include <handle.h>
#include <io_opentimeline_OTIOFinalizer.h>
#include <utilities.h>

#include <opentimelineio/any.h>
#include <opentimelineio/version.h>

enum ClassCode {
    _OpenTimeErrorStatus,
    _Any,
    _OTIOErrorStatus,
};

std::map<std::string, ClassCode> stringToClassCode = {
        {"io.opentimeline.opentimelineio.Any",         ClassCode::_Any},
        {"io.opentimeline.opentime.ErrorStatus",       ClassCode::_OpenTimeErrorStatus},
        {"io.opentimeline.opentimelineio.ErrorStatus", ClassCode::_OTIOErrorStatus},
};

std::map<ClassCode, std::string> classCodeToString = {
        {ClassCode::_Any,                 "io.opentimeline.opentimelineio.Any"},
        {ClassCode::_OpenTimeErrorStatus, "io.opentimeline.opentime.ErrorStatus"},
        {ClassCode::_OTIOErrorStatus,     "io.opentimeline.opentimelineio.ErrorStatus"},
};

/*
 * Class:     io_opentimeline_OTIOFinalizer
 * Method:    disposeNativeObject
 * Signature: (JLjava/lang/String;)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_OTIOFinalizer_disposeNativeObject
        (JNIEnv *env, jobject thisObject, jlong nativeHandle, jstring nativeClassName) {
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
        default:
            throwRuntimeException(env, "Could not find class.");
    }
}

