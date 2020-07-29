#include <class_codes.h>
#include <exceptions.h>
#include <opentimelineio/version.h>
#include <opentime/errorStatus.h>
#include <opentimelineio/any.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/serializableCollection.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/serializableObjectWithMetadata.h>
#include <opentimelineio/missingReference.h>
#include <opentimelineio/externalReference.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/composition.h>
#include <opentimelineio/composable.h>
#include <otio_manager.h>

std::map<std::string, ClassCode> stringToClassCode = {
        {"io.opentimeline.opentimelineio.Any",   ClassCode::_Any},
        {"io.opentimeline.opentime.ErrorStatus", ClassCode::_OpenTimeErrorStatus},
        {"io.opentimeline.opentimelineio.ErrorStatus",
                                                 ClassCode::_OTIOErrorStatus},
        {"io.opentimeline.opentimelineio.SerializableObject",
                                                 ClassCode::_SerializableObject},
        {"io.opentimeline.opentimelineio.SerializableObjectWithMetadata",
                                                 ClassCode::_SerializableObjectWithMetadata},
        {"io.opentimeline.opentimelineio.SerializableCollection",
                                                 ClassCode::_SerializableCollection},
        {"io.opentimeline.opentimelineio.Composable",
                                                 ClassCode::_Composable},
        {"io.opentimeline.opentimelineio.Marker",
                                                 ClassCode::_Marker},
        {"io.opentimeline.opentimelineio.MediaReference",
                                                 ClassCode::_MediaReference},
        {"io.opentimeline.opentimelineio.MissingReference",
                                                 ClassCode::_MissingReference},
        {"io.opentimeline.opentimelineio.ExternalReference",
                                                 ClassCode::_ExternalReference},
};

std::map<ClassCode, std::string> classCodeToString = {
        {ClassCode::_Any,                 "io.opentimeline.opentimelineio.Any"},
        {ClassCode::_OpenTimeErrorStatus, "io.opentimeline.opentime.ErrorStatus"},
        {ClassCode::_OTIOErrorStatus,
                                          "io.opentimeline.opentimelineio.ErrorStatus"},
        {ClassCode::_SerializableObject,
                                          "io.opentimeline.opentimelineio.SerializableObject"},
        {ClassCode::_SerializableObjectWithMetadata,
                                          "io.opentimeline.opentimelineio.SerializableObjectWithMetadata"},
        {ClassCode::_SerializableCollection,
                                          "io.opentimeline.opentimelineio.SerializableCollection"},
        {ClassCode::_Composable,
                                          "io.opentimeline.opentimelineio.Composable"},
        {ClassCode::_Marker,
                                          "io.opentimeline.opentimelineio.Marler"},
        {ClassCode::_MediaReference,
                                          "io.opentimeline.opentimelineio.MediaReference"},
        {ClassCode::_MissingReference,
                                          "io.opentimeline.opentimelineio.MissingReference"},
        {ClassCode::_ExternalReference,
                                          "io.opentimeline.opentimelineio.ExternalReference"},
};

inline void disposeObject(JNIEnv *env, jlong nativeHandle, jstring nativeClassName) {
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
        case _SerializableCollection: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::SerializableCollection> *>(
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
        case _Marker: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Marker> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _MediaReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::MediaReference> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _MissingReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::MissingReference> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _ExternalReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::ExternalReference> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        default:
            throwRuntimeException(env, "Could not find class.");
    }
}

inline void disposeObject(JNIEnv *env, jobject thisObj) {
    jclass thisClass = env->GetObjectClass(thisObj);
    jfieldID nativeHandleID = env->GetFieldID(thisClass, "nativeHandle", "J");
    jfieldID classNameID =
            env->GetFieldID(thisClass, "className", "Ljava/lang/String;");

    jlong nativeHandle = env->GetLongField(thisObj, nativeHandleID);
    jstring className = (jstring) env->GetObjectField(thisObj, classNameID);

    disposeObject(env, nativeHandle, className);
}