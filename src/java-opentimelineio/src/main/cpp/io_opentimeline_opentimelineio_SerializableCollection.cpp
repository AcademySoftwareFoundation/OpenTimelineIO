#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_SerializableCollection.h>
#include <opentimelineio/serializableCollection.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    initialize
 * Signature: (Ljava/lang/String;[Lio/opentimeline/opentimelineio/SerializableObject;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableCollection_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring name,
        jobjectArray childrenArray,
        jobject metadata) {
    if (name == nullptr || childrenArray == nullptr || metadata == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string nameStr = env->GetStringUTFChars(name, 0);
        auto children = serializableObjectVectorFromArray(env, childrenArray);
        auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
        auto serializableCollection = new OTIO_NS::SerializableCollection(
                nameStr, children, *metadataHandle);
        auto serializableCollectionManager =
                new managing_ptr<OTIO_NS::SerializableCollection>(env, serializableCollection);
        setHandle(env, thisObj, serializableCollectionManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    getChildrenNative
 * Signature: ()[Lio/opentimeline/opentimelineio/SerializableObject/Retainer;
 */
JNIEXPORT jobjectArray JNICALL
Java_io_opentimeline_opentimelineio_SerializableCollection_getChildrenNative(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, thisObj);
    auto serializableCollection = thisHandle->get();
    std::vector<
            OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>
            children = serializableCollection->children();
    return serializableObjectRetainerVectorToArray(
            env,
            *(new std::vector<
                    OTIO_NS::SerializableObject::Retainer<OTIO_NS::SerializableObject>>(
                    children)));
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    setChildrenNative
 * Signature: ([Lio/opentimeline/opentimelineio/SerializableObject;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableCollection_setChildrenNative(
        JNIEnv *env, jobject thisObj, jobjectArray childrenArray) {
    if (childrenArray == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, thisObj);
        auto serializableCollection = thisHandle->get();
        auto children = serializableObjectVectorFromArray(env, childrenArray);
        serializableCollection->set_children(children);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    clearChildren
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableCollection_clearChildren(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, thisObj);
    auto serializableCollection = thisHandle->get();
    serializableCollection->clear_children();
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    setChild
 * Signature: (ILio/opentimeline/opentimelineio/SerializableObject;Lio/opentimeline/opentimelineio/ErrorStatus;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_SerializableCollection_setChild(
        JNIEnv *env,
        jobject thisObj,
        jint index,
        jobject childObj,
        jobject errorStatusObj) {
    if (childObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, thisObj);
        auto serializableCollection = thisHandle->get();
        auto errorStatusHandle =
                getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        auto childHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableObject>>(env, thisObj);
        auto child = childHandle->get();
        return serializableCollection->set_child(index, child, errorStatusHandle);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    insertChild
 * Signature: (ILio/opentimeline/opentimelineio/SerializableObject;)V
 */
JNIEXPORT void JNICALL Java_io_opentimeline_opentimelineio_SerializableCollection_insertChild
        (JNIEnv *env, jobject thisObj, jint index, jobject childObj) {
    if (childObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, thisObj);
        auto serializableCollection = thisHandle->get();
        auto childHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableObject>>(env, thisObj);
        auto child = childHandle->get();
        serializableCollection->insert_child(index, child);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableCollection
 * Method:    removeChild
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_SerializableCollection_removeChild(
        JNIEnv *env, jobject thisObj, jint index, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, thisObj);
    auto serializableCollection = thisHandle->get();
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return serializableCollection->remove_child(index, errorStatusHandle);
}
