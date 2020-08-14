#include <io_opentimeline_opentimelineio_OTIOTest.h>
#include <exceptions.h>
#include <opentimelineio/serializableCollection.h>
#include <handle.h>
#include <otio_manager.h>
#include <opentimelineio/version.h>

/*
 * Class:     io_opentimeline_opentimelineio_OTIOTest
 * Method:    testRetainers1
 * Signature: (Lio/opentimeline/opentimelineio/SerializableCollection;)I
 */
JNIEXPORT jint JNICALL Java_io_opentimeline_opentimelineio_OTIOTest_testRetainers1
        (JNIEnv *env, jclass thisClass, jobject serializableCollectionObj) {

    if (serializableCollectionObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<managing_ptr<OTIO_NS::SerializableCollection>>(env, serializableCollectionObj);
        auto sc = thisHandle->get();
        OTIO_NS::SerializableObject *so = sc->children()[0];
        int total = 0;
        for (size_t i = 0; i < 1024 * 10; i++) {
            OTIO_NS::SerializableObject::Retainer<> r(so);
            if (r.value) {
                total++;
            }
        }
        return total;
    }
}