#include <jni.h>
#include <opentimelineio/serializableObject.h>
#include <opentimelineio/version.h>

#ifndef _OTIO_MANAGER_H_INCLUDED_
#define _OTIO_MANAGER_H_INCLUDED_

void install_external_keepalive_monitor(
    JNIEnv* env, OTIO_NS::SerializableObject* so, bool apply_now);

template <typename T> struct managing_ptr
{
    managing_ptr(JNIEnv* env, T* ptr) : _retainer(ptr)
    {
        install_external_keepalive_monitor(env, ptr, false);
    }

    T* get() const { return _retainer.value; }

    OTIO_NS::SerializableObject::Retainer<> _retainer;
};

#endif