#include <handle.h>
#include <io_opentimeline_OTIONative.h>
#include <class_codes.h>
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
#include <exceptions.h>

/*
 * Class:     io_opentimeline_OTIONative
 * Method:    getOTIOObjectNativeHandle
 * Signature: ()J
 */
JNIEXPORT jlong JNICALL Java_io_opentimeline_OTIONative_getOTIOObjectNativeHandle
        (JNIEnv *env, jobject thisObj) {
    jclass thisClass = env->GetObjectClass(thisObj);
    jfieldID nativeHandleID = env->GetFieldID(thisClass, "nativeHandle", "J");
    jfieldID classNameID =
            env->GetFieldID(thisClass, "className", "Ljava/lang/String;");
    jlong nativeHandle = env->GetLongField(thisObj, nativeHandleID);
    jstring nativeClassName = (jstring) env->GetObjectField(thisObj, classNameID);
    std::string className = env->GetStringUTFChars(nativeClassName, 0);
    switch (stringToClassCode[className]) {
        case _Any: {
            auto obj = reinterpret_cast<OTIO_NS::any *>(nativeHandle);
            return reinterpret_cast<long>(obj);
        }
        case _AnyDictionary: {
            auto obj = reinterpret_cast<OTIO_NS::AnyDictionary *>(nativeHandle);
            return reinterpret_cast<long>(obj);
        }
        case _OpenTimeErrorStatus: {
            auto obj = reinterpret_cast<opentime::ErrorStatus *>(nativeHandle);
            return reinterpret_cast<long>(obj);
        }
        case _OTIOErrorStatus: {
            auto obj = reinterpret_cast<OTIO_NS::ErrorStatus *>(nativeHandle);
            return reinterpret_cast<long>(obj);
        }
        case _SerializableObject: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::SerializableObject> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _SerializableObjectWithMetadata: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::SerializableObjectWithMetadata> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _SerializableCollection: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::SerializableCollection> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Composable: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Composable> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Marker: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Marker> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _MediaReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::MediaReference> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _MissingReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::MissingReference> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _ExternalReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::ExternalReference> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _GeneratorReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::GeneratorReference> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Effect: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Effect> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _TimeEffect: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::TimeEffect> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _LinearTimeWarp: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::LinearTimeWarp> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _FreezeFrame: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::FreezeFrame> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _ImageSequenceReference: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::ImageSequenceReference> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Item: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Item> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Composition: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Composition> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Gap: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Gap> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _UnknownSchema: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::UnknownSchema> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Transition: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Transition> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Clip: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Clip> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Stack: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Stack> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Track: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Track> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        case _Timeline: {
            auto obj =
                    reinterpret_cast<managing_ptr<OTIO_NS::Timeline> *>(
                            nativeHandle);
            auto result = obj->get();
            return reinterpret_cast<long>(result);
        }
        default:
            throwRuntimeException(env, "Could not find class.");
    }
}

/*
 * Class:     io_opentimeline_OTIONative
 * Method:    close
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_OTIONative_close(JNIEnv *env, jobject thisObj) {
    disposeObject(env, thisObj);
}