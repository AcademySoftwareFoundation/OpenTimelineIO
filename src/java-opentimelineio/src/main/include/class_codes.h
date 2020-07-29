#include <map>
#include <jni.h>

#ifndef _CLASS_CODES_H_INCLUDED_
#define _CLASS_CODES_H_INCLUDED_

enum ClassCode {
    _OpenTimeErrorStatus,
    _Any,
    _OTIOErrorStatus,
    _SerializableObject,
    _SerializableObjectWithMetadata,
    _SerializableCollection,
    _Marker,
    _MediaReference,
    _MissingReference,
    _ExternalReference,
    _GeneratorReference,
    _Effect,
    _TimeEffect,
    _LinearTimeWarp,
    _FreezeFrame,
    _ImageSequenceReference,
    _Composable,
    _Item,
    _Composition,
    _Gap,
    _UnknownSchema,
    _Transition,
    _Clip,
    _Stack,
    _Track,
    _Timeline,
};

extern std::map<std::string, ClassCode> stringToClassCode;

extern std::map<ClassCode, std::string> classCodeToString;

void disposeObject(JNIEnv *env, jlong nativeHandle, jstring nativeClassName);

void disposeObject(JNIEnv *env, jobject object);

#endif