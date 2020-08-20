#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_ImageSequenceReference.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/imageSequenceReference.h>
#include <opentimelineio/version.h>
#include <utilities.h>
#include <otio_manager.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIDIILio/opentimeline/opentime/TimeRange;Lio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_initialize(
        JNIEnv *env,
        jobject thisObj,
        jstring targetURLBase,
        jstring namePrefix,
        jstring nameSuffix,
        jint startFrame,
        jint frameStep,
        jdouble rate,
        jint frameZeroPadding,
        jint missingFramePolicyIndex,
        jobject availableRangeObj,
        jobject metadataObj) {
    if (targetURLBase == nullptr || namePrefix == nullptr ||
        nameSuffix == nullptr)
        throwNullPointerException(env, "");
    else {
        std::string targetURLBaseStr = env->GetStringUTFChars(targetURLBase, 0);
        std::string namePrefixStr = env->GetStringUTFChars(namePrefix, 0);
        std::string nameSuffixStr = env->GetStringUTFChars(nameSuffix, 0);
        optional<TimeRange> availableRange = nullopt;
        if (availableRangeObj != nullptr) { availableRange = timeRangeFromJObject(env, availableRangeObj); }
        auto metadataHandle =
                getHandle<AnyDictionary>(env, metadataObj);
        auto imageSequenceReference = new ImageSequenceReference(
                targetURLBaseStr,
                namePrefixStr,
                nameSuffixStr,
                startFrame,
                frameStep,
                rate,
                frameZeroPadding,
                ImageSequenceReference::MissingFramePolicy(
                        missingFramePolicyIndex),
                availableRange,
                *metadataHandle);
        auto imageSequenceReferenceManager =
                new SerializableObject::Retainer<ImageSequenceReference>(imageSequenceReference);
        setHandle(env, thisObj, imageSequenceReferenceManager);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getTargetURLBase
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getTargetURLBase(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return env->NewStringUTF(imageSequenceReference->target_url_base().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setTargetURLBase
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setTargetURLBase(
        JNIEnv *env, jobject thisObj, jstring targetURLBase) {
    if (targetURLBase == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
        auto imageSequenceReference = thisHandle->value;
        std::string targetURLBaseStr = env->GetStringUTFChars(targetURLBase, 0);
        imageSequenceReference->set_target_url_base(targetURLBaseStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getNamePrefix
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getNamePrefix(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return env->NewStringUTF(imageSequenceReference->name_prefix().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setNamePrefix
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setNamePrefix(
        JNIEnv *env, jobject thisObj, jstring namePrefix) {
    if (namePrefix == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
        auto imageSequenceReference = thisHandle->value;
        std::string namePrefixStr = env->GetStringUTFChars(namePrefix, 0);
        imageSequenceReference->set_name_prefix(namePrefixStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getNameSuffix
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getNameSuffix(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return env->NewStringUTF(imageSequenceReference->name_suffix().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setNameSuffix
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setNameSuffix(
        JNIEnv *env, jobject thisObj, jstring nameSuffix) {
    if (nameSuffix == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
        auto imageSequenceReference = thisHandle->value;
        std::string nameSuffixStr = env->GetStringUTFChars(nameSuffix, 0);
        imageSequenceReference->set_name_prefix(nameSuffixStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getStartFrame
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getStartFrame(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return imageSequenceReference->start_frame();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setStartFrame
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setStartFrame(
        JNIEnv *env, jobject thisObj, jint startFrame) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    imageSequenceReference->set_start_frame(startFrame);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getFrameStep
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getFrameStep(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return imageSequenceReference->frame_step();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setFrameStep
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setFrameStep(
        JNIEnv *env, jobject thisObj, jint frameStep) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    imageSequenceReference->set_frame_step(frameStep);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getRate
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getRate(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return imageSequenceReference->rate();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setRate
 * Signature: (D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setRate(
        JNIEnv *env, jobject thisObj, jdouble rate) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    imageSequenceReference->set_rate(rate);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getFrameZeroPadding
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getFrameZeroPadding(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return imageSequenceReference->frame_zero_padding();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setFrameZeroPadding
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setFrameZeroPadding(
        JNIEnv *env, jobject thisObj, jint frameZeroPadding) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    imageSequenceReference->set_frame_zero_padding(frameZeroPadding);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getMissingFramePolicyNative
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getMissingFramePolicyNative(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return (int) (imageSequenceReference->missing_frame_policy());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setMissingFramePolicyNative
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setMissingFramePolicyNative(
        JNIEnv *env, jobject thisObj, jint missingFramePolicyIndex) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    imageSequenceReference->set_missing_frame_policy(
            ImageSequenceReference::MissingFramePolicy(
                    missingFramePolicyIndex));
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getEndFrame
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getEndFrame(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return imageSequenceReference->end_frame();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getNumberOfImagesInSequence
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getNumberOfImagesInSequence(
        JNIEnv *env, jobject thisObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    return imageSequenceReference->number_of_images_in_sequence();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getFrameForTime
 * Signature: (Lio/opentimeline/opentime/RationalTime;Lio/opentimeline/opentimelineio/ErrorStatus;)I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getFrameForTime(
        JNIEnv *env,
        jobject thisObj,
        jobject rationalTimeObj,
        jobject errorStatusObj) {
    if (rationalTimeObj == nullptr)
        throwNullPointerException(env, "");
    else {
        auto thisHandle =
                getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
        auto imageSequenceReference = thisHandle->value;
        opentime::RationalTime rt =
                rationalTimeFromJObject(env, rationalTimeObj);
        auto errorStatusHandle =
                getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
        return imageSequenceReference->frame_for_time(rt, errorStatusHandle);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getTargetURLForImageNumber
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getTargetURLForImageNumber(
        JNIEnv *env, jobject thisObj, jint imageNumber, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return env->NewStringUTF(
            imageSequenceReference->target_url_for_image_number(imageNumber, errorStatusHandle)
                    .c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    presentationTimeForImageNumber
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)Lio/opentimeline/opentime/RationalTime;
 */
JNIEXPORT jobject JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_presentationTimeForImageNumber(
        JNIEnv *env, jobject thisObj, jint imageNumber, jobject errorStatusObj) {
    auto thisHandle =
            getHandle<SerializableObject::Retainer<ImageSequenceReference>>(env, thisObj);
    auto imageSequenceReference = thisHandle->value;
    auto errorStatusHandle =
            getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    RationalTime rt = imageSequenceReference->presentation_time_for_image_number(
            imageNumber, errorStatusHandle);
    return rationalTimeToJObject(env, rt);
}
