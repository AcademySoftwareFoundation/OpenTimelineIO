#include <jni.h>

#include <exceptions.h>
#include <handle.h>
#include <opentime/rationalTime.h>
#include <opentime/timeRange.h>
#include <opentime/timeTransform.h>
#include <opentime/version.h>
#include <opentimelineio/anyDictionary.h>
#include <opentimelineio/composable.h>
#include <opentimelineio/effect.h>
#include <opentimelineio/marker.h>
#include <opentimelineio/mediaReference.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/stack.h>
#include <opentimelineio/track.h>
#include <opentimelineio/version.h>
#include <otio_manager.h>

#ifndef _UTILITIES_H_INCLUDED_
#define _UTILITIES_H_INCLUDED_

inline void registerObjectToOTIOFactory(JNIEnv *env, jobject otioObject) {

    if (otioObject == nullptr) throwNullPointerException(env, "");

    jclass otioFactoryClass = env->FindClass("io/opentimeline/OTIOFactory");

    jmethodID registerObject = env->GetMethodID(otioFactoryClass, "registerObject",
                                                "(Lio/opentimeline/OTIOObject;)V");
    jmethodID getFactoryInstance = env->GetStaticMethodID(otioFactoryClass, "getInstance",
                                                          "()Lio/opentimeline/OTIOFactory;");
    jobject factoryInstance = env->CallStaticObjectMethod(otioFactoryClass, getFactoryInstance);

    env->CallVoidMethod(factoryInstance, registerObject, otioObject);
}

inline std::vector<OTIO_NS::SerializableObject *>
serializableObjectVectorFromArray(JNIEnv *env, jobjectArray array) {
    int arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::SerializableObject *> objectVector;
    objectVector.reserve(arrayLength);
    for (int i = 0; i < arrayLength; ++i) {
        jobject element = env->GetObjectArrayElement(array, i);
        auto elementHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableObject>>(env, element);
        auto serializableObject = elementHandle->get();
        objectVector.push_back(serializableObject);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Effect *>
effectVectorFromArray(JNIEnv *env, jobjectArray array) {
    int arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Effect *> objectVector;
    objectVector.reserve(arrayLength);
    for (int i = 0; i < arrayLength; ++i) {
        jobject element = env->GetObjectArrayElement(array, i);
        auto elementHandle =
                getHandle<managing_ptr<OTIO_NS::Effect>>(env, element);
        auto effect = elementHandle->get();
        objectVector.push_back(effect);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Marker *>
markerVectorFromArray(JNIEnv *env, jobjectArray array) {
    int arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Marker *> objectVector;
    objectVector.reserve(arrayLength);
    for (int i = 0; i < arrayLength; ++i) {
        jobject element = env->GetObjectArrayElement(array, i);
        auto elementHandle =
                getHandle<managing_ptr<OTIO_NS::Marker>>(env, element);
        auto marker = elementHandle->get();
        objectVector.push_back(marker);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Composable *>
composableVectorFromArray(JNIEnv *env, jobjectArray array) {
    int arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Composable *> objectVector;
    objectVector.reserve(arrayLength);
    for (int i = 0; i < arrayLength; ++i) {
        jobject element = env->GetObjectArrayElement(array, i);
        auto elementHandle =
                getHandle<managing_ptr<OTIO_NS::Composable>>(env, element);
        auto composable = elementHandle->get();
        objectVector.push_back(composable);
    }
    return objectVector;
}

inline std::vector<OTIO_NS::Track *>
trackVectorFromArray(JNIEnv *env, jobjectArray array) {
    int arrayLength = env->GetArrayLength(array);
    std::vector<OTIO_NS::Track *> objectVector;
    objectVector.reserve(arrayLength);
    for (int i = 0; i < arrayLength; ++i) {
        jobject element = env->GetObjectArrayElement(array, i);
        auto elementHandle =
                getHandle<managing_ptr<OTIO_NS::Track>>(env, element);
        auto track = elementHandle->get();
        objectVector.push_back(track);
    }
    return objectVector;
}

std::map<std::type_info const *, std::string> getAnyType();

inline std::string getSerializableObjectJavaClassFromNative(OTIO_NS::SerializableObject *serializableObject) {
    static std::once_flag classFlag;
    static std::unique_ptr<std::map<std::string, std::string>> class_dispatch_table;
    std::call_once(classFlag, []() {
        class_dispatch_table = std::unique_ptr<std::map<std::string, std::string>>(
                new std::map<std::string, std::string>());
        (*class_dispatch_table)["Clip"] = "io/opentimeline/opentimelineio/Clip";
        (*class_dispatch_table)["Composable"] = "io/opentimeline/opentimelineio/Composable";
        (*class_dispatch_table)["Composition"] = "io/opentimeline/opentimelineio/Composition";
        (*class_dispatch_table)["Effect"] = "io/opentimeline/opentimelineio/Effect";
        (*class_dispatch_table)["ExternalReference"] = "io/opentimeline/opentimelineio/ExternalReference";
        (*class_dispatch_table)["FreezeFrame"] = "io/opentimeline/opentimelineio/FreezeFrame";
        (*class_dispatch_table)["Gap"] = "io/opentimeline/opentimelineio/Gap";
        (*class_dispatch_table)["GeneratorReference"] = "io/opentimeline/opentimelineio/GeneratorReference";
        (*class_dispatch_table)["ImageSequenceReference"] = "io/opentimeline/opentimelineio/ImageSequenceReference";
        (*class_dispatch_table)["Item"] = "io/opentimeline/opentimelineio/Item";
        (*class_dispatch_table)["LinearTimeWarp"] = "io/opentimeline/opentimelineio/LinearTimeWarp";
        (*class_dispatch_table)["Marker"] = "io/opentimeline/opentimelineio/Marker";
        (*class_dispatch_table)["MediaReference"] = "io/opentimeline/opentimelineio/MediaReference";
        (*class_dispatch_table)["MissingReference"] = "io/opentimeline/opentimelineio/MissingReference";
        (*class_dispatch_table)["SerializableCollection"] = "io/opentimeline/opentimelineio/SerializableCollection";
        (*class_dispatch_table)["SerializableObject"] = "io/opentimeline/opentimelineio/SerializableObject";
        (*class_dispatch_table)["SerializableObjectWithMetadata"] = "io/opentimeline/opentimelineio/SerializableObjectWithMetadata";
        (*class_dispatch_table)["Stack"] = "io/opentimeline/opentimelineio/Stack";
        (*class_dispatch_table)["TimeEffect"] = "io/opentimeline/opentimelineio/TimeEffect";
        (*class_dispatch_table)["Timeline"] = "io/opentimeline/opentimelineio/Timeline";
        (*class_dispatch_table)["Track"] = "io/opentimeline/opentimelineio/Track";
        (*class_dispatch_table)["Transition"] = "io/opentimeline/opentimelineio/Transition";
        (*class_dispatch_table)["UnknownSchema"] = "io/opentimeline/opentimelineio/UnknownSchema";
    });

    return (*class_dispatch_table)[serializableObject->schema_name()];
}

/* this deepcopies any */
inline jobject
anyFromNative(JNIEnv *env, OTIO_NS::any *native) {
    if (native == nullptr)return nullptr;
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Any");
    if (cls == NULL) return NULL;

//    std::string anyType = _type_dispatch_table[&native->type()];
    std::string anyType = getAnyType()[&native->type()];
    // Get the Method ID of the constructor which takes an otioNative
    jmethodID anyInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == anyInit) return NULL;

    auto newAny = new OTIO_NS::any(*native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(newAny));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Any";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, anyInit, otioNative);

    jfieldID anyTypeStringID = env->GetFieldID(cls, "anyTypeClass", "Ljava/lang/String;");
    jstring anyTypeString = env->NewStringUTF(anyType.c_str());
    env->SetObjectField(newObj, anyTypeStringID, anyTypeString);

    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

/* this deepcopies anyDictionary */
inline jobject
anyDictionaryFromNative(JNIEnv *env, OTIO_NS::AnyDictionary *native) {
    if (native == nullptr)return nullptr;
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/AnyDictionary");
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID dictInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == dictInit) return NULL;

    auto newDict = new OTIO_NS::AnyDictionary(*native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(newDict));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.AnyDictionary";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, dictInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

/* this deepcopies anyDictionary::iterator */
inline jobject
anyDictionaryIteratorFromNative(
        JNIEnv *env, OTIO_NS::AnyDictionary::iterator *native) {
    if (native == nullptr)return nullptr;
    jclass cls =
            env->FindClass("io/opentimeline/opentimelineio/AnyDictionary$Iterator");
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID itInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == itInit) return NULL;

    auto newIt = new OTIO_NS::AnyDictionary::iterator(*native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(newIt));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.AnyDictionary.Iterator";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, itInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

/* this deepcopies anyVector */
inline jobject
anyVectorFromNative(JNIEnv *env, OTIO_NS::AnyVector *native) {
    if (native == nullptr)return nullptr;
    jclass cls = env->FindClass("io/opentimeline/opentimelineio/AnyVector");
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID vecInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == vecInit) return NULL;

    auto newVec = new OTIO_NS::AnyVector(*native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(newVec));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.AnyVector";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, vecInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

/* this deepcopies anyVector::iterator */
inline jobject
anyVectorIteratorFromNative(JNIEnv *env, OTIO_NS::AnyVector::iterator *native) {
    if (native == nullptr)return nullptr;
    jclass cls =
            env->FindClass("io/opentimeline/opentimelineio/AnyVector$Iterator");
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID itInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == itInit) return NULL;

    auto newIt = new OTIO_NS::AnyVector::iterator(*native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(newIt));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.AnyVector.Iterator";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, itInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

/* Following functions create new Retainer<T> objects thereby increasing the reference count */

inline jobject
serializableObjectFromNative(JNIEnv *env, OTIO_NS::SerializableObject *native) {
    if (native == nullptr)return nullptr;
//    jclass cls =
//            env->FindClass("io/opentimeline/opentimelineio/SerializableObject");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID soInit =
            env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == soInit) return NULL;

    auto serializableObjectManager =
            new managing_ptr<OTIO_NS::SerializableObject>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(serializableObjectManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.SerializableObject";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, soInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
effectFromNative(JNIEnv *env, OTIO_NS::Effect *native) {
    if (native == nullptr)return nullptr;
//    jclass cls =
//            env->FindClass("io/opentimeline/opentimelineio/Effect");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID effectInit =
            env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == effectInit) return NULL;

    auto effectManager =
            new managing_ptr<OTIO_NS::Effect>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(effectManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Effect";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, effectInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
markerFromNative(JNIEnv *env, OTIO_NS::Marker *native) {
    if (native == nullptr)return nullptr;
//    jclass cls =
//            env->FindClass("io/opentimeline/opentimelineio/Marker");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID markerInit =
            env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == markerInit) return NULL;

    auto effectManager =
            new managing_ptr<OTIO_NS::Marker>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(effectManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Marker";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, markerInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
composableFromNative(JNIEnv *env, OTIO_NS::Composable *native) {
    if (native == nullptr)return nullptr;
//    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Composable");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNatove
    jmethodID composableInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == composableInit) return NULL;

    auto composableManager =
            new managing_ptr<OTIO_NS::Composable>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(composableManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Composable";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, composableInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
compositionFromNative(JNIEnv *env, OTIO_NS::Composition *native) {
    if (native == nullptr)return nullptr;
//    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Composition");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID compositionInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == compositionInit) return NULL;

    auto compositionManager =
            new managing_ptr<OTIO_NS::Composable>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(compositionManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Composition";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, compositionInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
mediaReferenceFromNative(JNIEnv *env, OTIO_NS::MediaReference *native) {
    if (native == nullptr)return nullptr;
//    jclass cls =
//            env->FindClass("io/opentimeline/opentimelineio/MediaReference");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID mrInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == mrInit) return NULL;

    auto mrManager =
            new managing_ptr<OTIO_NS::MediaReference>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(mrManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.MediaReference";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, mrInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
stackFromNative(JNIEnv *env, OTIO_NS::Stack *native) {
    if (native == nullptr)return nullptr;
//    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Stack");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID stackInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == stackInit) return NULL;

    auto stackManager =
            new managing_ptr<OTIO_NS::Stack>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(stackManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Stack";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an int argument
    jobject newObj = env->NewObject(cls, stackInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobject
trackFromNative(JNIEnv *env, OTIO_NS::Track *native) {
    if (native == nullptr)return nullptr;
//    jclass cls = env->FindClass("io/opentimeline/opentimelineio/Track");
    std::string javaCls = getSerializableObjectJavaClassFromNative(native);
    jclass cls =
            env->FindClass(javaCls.c_str());
    if (cls == NULL) return NULL;

    // Get the Method ID of the constructor which takes an otioNative
    jmethodID trackInit = env->GetMethodID(cls, "<init>", "(Lio/opentimeline/OTIONative;)V");
    if (NULL == trackInit) return NULL;

    auto trackManager =
            new managing_ptr<OTIO_NS::Track>(env, native);
    jclass otioNativeClass = env->FindClass("io/opentimeline/OTIONative");
    jfieldID classNameID =
            env->GetFieldID(otioNativeClass, "className", "Ljava/lang/String;");
    jmethodID otioNativeInit =
            env->GetMethodID(otioNativeClass, "<init>", "(J)V");
    jobject otioNative = env->NewObject(
            otioNativeClass,
            otioNativeInit,
            reinterpret_cast<jlong>(trackManager));
    std::string classNameStr =
            "io.opentimeline.opentimelineio.Track";
    jstring className = env->NewStringUTF(classNameStr.c_str());
    env->SetObjectField(otioNative, classNameID, className);

    // Call back constructor to allocate a new instance, with an otioNative argument
    jobject newObj = env->NewObject(cls, trackInit, otioNative);
    registerObjectToOTIOFactory(env, newObj);
    return newObj;
}

inline jobjectArray
serializableObjectRetainerVectorToArray(
        JNIEnv *env,
        std::vector<
                OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>> &v) {
    jclass serializableObjectClass = env->FindClass(
            "io/opentimeline/opentimelineio/SerializableObject");
    jobjectArray result =
            env->NewObjectArray(v.size(), serializableObjectClass, nullptr);
    for (int i = 0; i < v.size(); i++) {
        auto newObj = serializableObjectFromNative(env, v[i]);
        registerObjectToOTIOFactory(env, newObj);
        env->SetObjectArrayElement(
                result, i, newObj);
    }
    return result;
}

inline jobjectArray
effectRetainerVectorToArray(
        JNIEnv *env,
        std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Effect>> &v) {
    jclass effectClass = env->FindClass(
            "io/opentimeline/opentimelineio/EffectObject");
    jobjectArray result =
            env->NewObjectArray(v.size(), effectClass, nullptr);
    for (int i = 0; i < v.size(); i++) {
        auto newObj = effectFromNative(env, v[i]);
        registerObjectToOTIOFactory(env, newObj);
        env->SetObjectArrayElement(
                result, i, newObj);
    }
    return result;
}

inline jobjectArray
markerRetainerVectorToArray(
        JNIEnv *env,
        std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Marker>> &v) {
    jclass markerClass = env->FindClass(
            "io/opentimeline/opentimelineio/Marker");
    jobjectArray result =
            env->NewObjectArray(v.size(), markerClass, nullptr);
    for (int i = 0; i < v.size(); i++) {
        auto newObj = markerFromNative(env, v[i]);
        registerObjectToOTIOFactory(env, newObj);
        env->SetObjectArrayElement(
                result, i, newObj);
    }
    return result;
}

inline jobjectArray
composableRetainerVectorToArray(
        JNIEnv *env,
        std::vector<OTIO_NS::SerializableObject::Retainer<OTIO_NS::Composable>> &v) {
    jclass composableClass = env->FindClass(
            "io/opentimeline/opentimelineio/Composable");
    jobjectArray result =
            env->NewObjectArray(v.size(), composableClass, nullptr);
    for (int i = 0; i < v.size(); i++) {
        auto newObj = composableFromNative(env, v[i]);
        registerObjectToOTIOFactory(env, newObj);
        env->SetObjectArrayElement(
                result, i, newObj);
    }
    return result;
}

inline jobjectArray
trackVectorToArray(JNIEnv *env, std::vector<OTIO_NS::Track *> &v) {
    jclass trackClass = env->FindClass("io/opentimeline/opentimelineio/Track");
    jobjectArray result = env->NewObjectArray(v.size(), trackClass, nullptr);
    for (int i = 0; i < v.size(); i++) {
        auto newObj = trackFromNative(env, v[i]);
        registerObjectToOTIOFactory(env, newObj);
        env->SetObjectArrayElement(result, i, newObj);
    }
    return result;
}

inline opentime::RationalTime
rationalTimeFromJObject(JNIEnv *env, jobject rtObject) {
    jclass rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID getValue = env->GetMethodID(rtClass, "getValue", "()D");
    jmethodID getRate = env->GetMethodID(rtClass, "getRate", "()D");
    double value = env->CallDoubleMethod(rtObject, getValue);
    double rate = env->CallDoubleMethod(rtObject, getRate);
    opentime::RationalTime rt(value, rate);
    return rt;
}

inline opentime::TimeRange
timeRangeFromJObject(JNIEnv *env, jobject trObject) {
    jclass trClass = env->FindClass("io/opentimeline/opentime/TimeRange");
    jmethodID getStartTime = env->GetMethodID(
            trClass, "getStartTime", "()Lio/opentimeline/opentime/RationalTime;");
    jmethodID getDuration = env->GetMethodID(
            trClass, "getDuration", "()Lio/opentimeline/opentime/RationalTime;");
    jobject startTime = env->CallObjectMethod(trObject, getStartTime);
    jobject duration = env->CallObjectMethod(trObject, getDuration);

    jclass rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID getValue = env->GetMethodID(rtClass, "getValue", "()D");
    jmethodID getRate = env->GetMethodID(rtClass, "getRate", "()D");

    double startTimeValue = env->CallDoubleMethod(startTime, getValue);
    double startTimeRate = env->CallDoubleMethod(startTime, getRate);
    double durationValue = env->CallDoubleMethod(duration, getValue);
    double durationRate = env->CallDoubleMethod(duration, getRate);

    opentime::TimeRange tr(
            opentime::RationalTime(startTimeValue, startTimeRate),
            opentime::RationalTime(durationValue, durationRate));

    return tr;
}

inline opentime::TimeTransform
timeTransformFromJObject(JNIEnv *env, jobject txObject) {
    jclass trClass = env->FindClass("io/opentimeline/opentime/TimeTransform");
    jmethodID getOffset = env->GetMethodID(
            trClass, "getOffset", "()Lio/opentimeline/opentime/RationalTime;");
    jmethodID getScale = env->GetMethodID(trClass, "getScale", "()D");
    jmethodID getRate = env->GetMethodID(trClass, "getRate", "()D");
    jobject offset = env->CallObjectMethod(txObject, getOffset);
    double scale = env->CallDoubleMethod(txObject, getScale);
    double rate = env->CallDoubleMethod(txObject, getRate);

    jclass rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID getRationalTimeValue =
            env->GetMethodID(rtClass, "getValue", "()D");
    jmethodID getRationalTimeRate = env->GetMethodID(rtClass, "getRate", "()D");

    double offsetValue = env->CallDoubleMethod(offset, getRationalTimeValue);
    double offsetRate = env->CallDoubleMethod(offset, getRationalTimeRate);

    opentime::TimeTransform timeTransform(
            opentime::RationalTime(offsetValue, offsetRate), scale, rate);
    return timeTransform;
}

inline jobject
rationalTimeToJObject(JNIEnv *env, opentime::RationalTime rationalTime) {
    jclass rtClass = env->FindClass("io/opentimeline/opentime/RationalTime");
    jmethodID rtInit = env->GetMethodID(rtClass, "<init>", "(DD)V");
    jobject rt = env->NewObject(
            rtClass, rtInit, rationalTime.value(), rationalTime.rate());
    return rt;
}

inline jobject
timeRangeToJObject(JNIEnv *env, opentime::TimeRange timeRange) {
    jclass trClass = env->FindClass("io/opentimeline/opentime/TimeRange");
    jmethodID trInit = env->GetMethodID(
            trClass,
            "<init>",
            "(Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentime/RationalTime;)V");
    jobject startTime = rationalTimeToJObject(env, timeRange.start_time());
    jobject duration = rationalTimeToJObject(env, timeRange.duration());
    jobject tr = env->NewObject(trClass, trInit, startTime, duration);
    return tr;
}

inline jobject
timeTransformToJObject(JNIEnv *env, opentime::TimeTransform timeTransform) {
    jclass txClass = env->FindClass("io/opentimeline/opentime/TimeTransform");
    jmethodID txInit = env->GetMethodID(
            txClass, "<init>", "(Lio/opentimeline/opentime/RationalTime;DD)V");
    jobject offset = rationalTimeToJObject(env, timeTransform.offset());
    jobject tx = env->NewObject(
            txClass, txInit, offset, timeTransform.scale(), timeTransform.rate());
    return tx;
}

#endif