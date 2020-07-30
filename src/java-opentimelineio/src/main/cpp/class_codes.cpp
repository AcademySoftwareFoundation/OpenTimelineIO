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
#include <opentimelineio/generatorReference.h>
#include <opentimelineio/imageSequenceReference.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/timeEffect.h>
#include <opentimelineio/linearTimeWarp.h>
#include <opentimelineio/freezeFrame.h>
#include <opentimelineio/composition.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/gap.h>
#include <opentimelineio/unknownSchema.h>
#include <opentimelineio/transition.h>
#include <opentimelineio/clip.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
#include <opentimelineio/timeline.h>
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
        {"io.opentimeline.opentimelineio.GeneratorReference",
                                                 ClassCode::_GeneratorReference},
        {"io.opentimeline.opentimelineio.Effect",
                                                 ClassCode::_Effect},
        {"io.opentimeline.opentimelineio.TimeEffect",
                                                 ClassCode::_TimeEffect},
        {"io.opentimeline.opentimelineio.LinearTimeWarp",
                                                 ClassCode::_LinearTimeWarp},
        {"io.opentimeline.opentimelineio.FreezeFrame",
                                                 ClassCode::_FreezeFrame},
        {"io.opentimeline.opentimelineio.ImageSequenceReference",
                                                 ClassCode::_ImageSequenceReference},
        {"io.opentimeline.opentimelineio.Item",
                                                 ClassCode::_Item},
        {"io.opentimeline.opentimelineio.Composition",
                                                 ClassCode::_Composition},
        {"io.opentimeline.opentimelineio.Gap",
                                                 ClassCode::_Gap},
        {"io.opentimeline.opentimelineio.UnknownSchema",
                                                 ClassCode::_UnknownSchema},
        {"io.opentimeline.opentimelineio.Clip",
                                                 ClassCode::_Clip},
        {"io.opentimeline.opentimelineio.Stack",
                                                 ClassCode::_Stack},
        {"io.opentimeline.opentimelineio.Track",
                                                 ClassCode::_Track},
        {"io.opentimeline.opentimelineio.Timeline",
                                                 ClassCode::_Timeline},
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
                                          "io.opentimeline.opentimelineio.Marker"},
        {ClassCode::_MediaReference,
                                          "io.opentimeline.opentimelineio.MediaReference"},
        {ClassCode::_MissingReference,
                                          "io.opentimeline.opentimelineio.MissingReference"},
        {ClassCode::_ExternalReference,
                                          "io.opentimeline.opentimelineio.ExternalReference"},
        {ClassCode::_GeneratorReference,
                                          "io.opentimeline.opentimelineio.GeneratorReference"},
        {ClassCode::_Effect,
                                          "io.opentimeline.opentimelineio.Effect"},
        {ClassCode::_TimeEffect,
                                          "io.opentimeline.opentimelineio.TimeEffect"},
        {ClassCode::_LinearTimeWarp,
                                          "io.opentimeline.opentimelineio.LinearTimeWarp"},
        {ClassCode::_FreezeFrame,
                                          "io.opentimeline.opentimelineio.FreezeFrame"},
        {ClassCode::_ImageSequenceReference,
                                          "io.opentimeline.opentimelineio.ImageSequenceReference"},
        {ClassCode::_Item,
                                          "io.opentimeline.opentimelineio.Item"},
        {ClassCode::_Composition,
                                          "io.opentimeline.opentimelineio.Composition"},
        {ClassCode::_Gap,
                                          "io.opentimeline.opentimelineio.Gap"},
        {ClassCode::_UnknownSchema,
                                          "io.opentimeline.opentimelineio.UnknownSchema"},
        {ClassCode::_Transition,
                                          "io.opentimeline.opentimelineio.Transition"},
        {ClassCode::_Clip,
                                          "io.opentimeline.opentimelineio.Clip"},
        {ClassCode::_Stack,
                                          "io.opentimeline.opentimelineio.Stack"},
        {ClassCode::_Track,
                                          "io.opentimeline.opentimelineio.Track"},
        {ClassCode::_Timeline,
                                          "io.opentimeline.opentimelineio.Timeline"},
};

void disposeObject(JNIEnv *env, jlong nativeHandle, jstring nativeClassName) {
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
        case _GeneratorReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::GeneratorReference> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Effect: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Effect> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _TimeEffect: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::TimeEffect> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _LinearTimeWarp: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::LinearTimeWarp> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _FreezeFrame: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::FreezeFrame> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _ImageSequenceReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::ImageSequenceReference> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Item: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Item> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Composition: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Composition> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Gap: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Gap> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _UnknownSchema: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::UnknownSchema> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Transition: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Transition> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Clip: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Clip> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Stack: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Stack> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Track: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Track> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        case _Timeline: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Timeline> *>(
                            nativeHandle);
            delete obj;
            break;
        }
        default:
            throwRuntimeException(env, "Could not find class.");
    }
}

void disposeObject(JNIEnv *env, jobject thisObj) {
    jclass thisClass = env->GetObjectClass(thisObj);
    jfieldID nativeHandleID = env->GetFieldID(thisClass, "nativeHandle", "J");
    jfieldID classNameID =
            env->GetFieldID(thisClass, "className", "Ljava/lang/String;");

    jlong nativeHandle = env->GetLongField(thisObj, nativeHandleID);
    jstring className = (jstring) env->GetObjectField(thisObj, classNameID);

    disposeObject(env, nativeHandle, className);
}