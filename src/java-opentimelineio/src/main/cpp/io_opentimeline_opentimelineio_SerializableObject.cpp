#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_SerializableObject.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    initialize
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_initialize(
    JNIEnv *env, jobject thisObj) {
  OTIO_NS::SerializableObject *serializableObject =
      new OTIO_NS::SerializableObject();
  setHandle(env, thisObj, serializableObject);
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    toJSONFile
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/ErrorStatus;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_toJSONFile__Ljava_lang_String_2Lio_opentimeline_opentimelineio_ErrorStatus_2(
    JNIEnv *env, jobject thisObj, jstring fileNameStr, jobject errorStatusObj) {
  if (fileNameStr == NULL || errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return thisHandle->to_json_file(env->GetStringUTFChars(fileNameStr, 0),
                                    errorStatusHandle);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    toJSONFile
 * Signature: (Ljava/lang/String;Lio/opentimeline/opentimelineio/ErrorStatus;I)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_toJSONFile__Ljava_lang_String_2Lio_opentimeline_opentimelineio_ErrorStatus_2I(
    JNIEnv *env, jobject thisObj, jstring fileNameStr, jobject errorStatusObj,
    jint indent) {
  if (fileNameStr == NULL || errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return thisHandle->to_json_file(env->GetStringUTFChars(fileNameStr, 0),
                                    errorStatusHandle, indent);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    toJSONString
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_toJSONString__Lio_opentimeline_opentimelineio_ErrorStatus_2(
    JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
  if (errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return env->NewStringUTF(
        thisHandle->to_json_string(errorStatusHandle).c_str());
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    toJSONString
 * Signature: (Lio/opentimeline/opentimelineio/ErrorStatus;I)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_toJSONString__Lio_opentimeline_opentimelineio_ErrorStatus_2I(
    JNIEnv *env, jobject thisObj, jobject errorStatusObj, jint indent) {
  if (errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return env->NewStringUTF(
        thisHandle->to_json_string(errorStatusHandle, indent).c_str());
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    fromJSONFile
 * Signature:
 * (Ljava/lang/String;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_fromJSONFile(
    JNIEnv *env, jclass thisClass, jstring fileNameStr,
    jobject errorStatusObj) {
  if (fileNameStr == NULL || errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = OTIO_NS::SerializableObject::from_json_file(
        env->GetStringUTFChars(fileNameStr, 0), errorStatusHandle);
    return serializableObjectFromNative(env, result);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    fromJSONString
 * Signature:
 * (Ljava/lang/String;Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_fromJSONString(
    JNIEnv *env, jclass thisClass, jstring JSONStr, jobject errorStatusObj) {
  if (JSONStr == NULL || errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto result = OTIO_NS::SerializableObject::from_json_string(
        env->GetStringUTFChars(JSONStr, 0), errorStatusHandle);
    return serializableObjectFromNative(env, result);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    isEquivalentTo
 * Signature: (Lio/opentimeline/opentimelineio/SerializableObject;)Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_isEquivalentTo(
    JNIEnv *env, jobject thisObj, jobject otherObj) {
  if (otherObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
    auto otherHandle = getHandle<OTIO_NS::SerializableObject>(env, otherObj);
    return thisHandle->is_equivalent_to(*otherHandle);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    clone
 * Signature:
 * (Lio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentimelineio/SerializableObject;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_clone(
    JNIEnv *env, jobject thisObj, jobject errorStatusObj) {
  if (errorStatusObj == NULL) {
    throwNullPointerException(env, "");
  } else {
    auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    auto clonedHandle = thisHandle->clone(errorStatusHandle);
    return serializableObjectFromNative(env, clonedHandle);
  }
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    dynamicFields
 * Signature: ()Lio/opentimeline/opentimelineio/AnyDictionary;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_dynamicFields(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
  auto result = thisHandle->dynamic_fields();
  return anyDictionaryFromNative(env, &result);
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    isUnknownSchema
 * Signature: ()Z
 */
JNIEXPORT jboolean JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_isUnknownSchema(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
  return thisHandle->is_unknown_schema();
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    schemaName
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_schemaName(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
  return env->NewStringUTF(thisHandle->schema_name().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    schemaVersion
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_schemaVersion(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
  return thisHandle->schema_version();
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    currentRefCount
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_currentRefCount(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
  return thisHandle->current_ref_count();
}

/*
 * Class:     io_opentimeline_opentimelineio_SerializableObject
 * Method:    possiblyDispose
 * Signature: ()V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_SerializableObject_possiblyDispose(
    JNIEnv *env, jobject thisObj) {
  auto thisHandle = getHandle<OTIO_NS::SerializableObject>(env, thisObj);
  if (thisHandle->possibly_delete()) {
    setHandle<OTIO_NS::SerializableObject>(env, thisObj, nullptr);
  }
}
