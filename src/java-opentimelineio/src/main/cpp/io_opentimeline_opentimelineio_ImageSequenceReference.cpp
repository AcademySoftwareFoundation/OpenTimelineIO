#include <exceptions.h>
#include <handle.h>
#include <io_opentimeline_opentimelineio_ImageSequenceReference.h>
#include <opentimelineio/errorStatus.h>
#include <opentimelineio/imageSequenceReference.h>
#include <opentimelineio/version.h>
#include <utilities.h>

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    initialize
 * Signature: (Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;IIDII[DLio/opentimeline/opentimelineio/AnyDictionary;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_initialize(
    JNIEnv*      env,
    jobject      thisObj,
    jstring      targetURLBase,
    jstring      namePrefix,
    jstring      nameSuffix,
    jint         startFrame,
    jint         frameStep,
    jdouble      rate,
    jint         frameZeroPadding,
    jint         missingFramePolicyIndex,
    jdoubleArray availableRangeArray,
    jobject      metadata)
{
    if(targetURLBase == NULL || namePrefix == NULL || nameSuffix == NULL ||
       availableRangeArray == NULL)
        throwNullPointerException(env, "");
    else
    {
        std::string targetURLBaseStr = env->GetStringUTFChars(targetURLBase, 0);
        std::string namePrefixStr    = env->GetStringUTFChars(namePrefix, 0);
        std::string nameSuffixStr    = env->GetStringUTFChars(nameSuffix, 0);
        OTIO_NS::optional<opentime::TimeRange> availableRange =
            OTIO_NS::nullopt;
        if(env->GetArrayLength(availableRangeArray) != 0)
        { availableRange = timeRangeFromArray(env, availableRangeArray); }
        auto metadataHandle = getHandle<OTIO_NS::AnyDictionary>(env, metadata);
        auto imageSequenceReference = new OTIO_NS::ImageSequenceReference(
            targetURLBaseStr,
            namePrefixStr,
            nameSuffixStr,
            startFrame,
            frameStep,
            rate,
            frameZeroPadding,
            OTIO_NS::ImageSequenceReference::MissingFramePolicy(
                missingFramePolicyIndex),
            availableRange,
            *metadataHandle);
        setHandle(env, thisObj, imageSequenceReference);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getTargetURLBase
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getTargetURLBase(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return env->NewStringUTF(thisHandle->target_url_base().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setTargetURLBase
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setTargetURLBase(
    JNIEnv* env, jobject thisObj, jstring targetURLBase)
{
    if(targetURLBase == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle =
            getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
        std::string targetURLBaseStr = env->GetStringUTFChars(targetURLBase, 0);
        thisHandle->set_target_url_base(targetURLBaseStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getNamePrefix
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getNamePrefix(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return env->NewStringUTF(thisHandle->name_prefix().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setNamePrefix
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setNamePrefix(
    JNIEnv* env, jobject thisObj, jstring namePrefix)
{
    if(namePrefix == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle =
            getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
        std::string namePrefixStr = env->GetStringUTFChars(namePrefix, 0);
        thisHandle->set_name_prefix(namePrefixStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getNameSuffix
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getNameSuffix(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return env->NewStringUTF(thisHandle->name_suffix().c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setNameSuffix
 * Signature: (Ljava/lang/String;)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setNameSuffix(
    JNIEnv* env, jobject thisObj, jstring nameSuffix)
{
    if(nameSuffix == NULL)
        throwNullPointerException(env, "");
    else
    {
        auto thisHandle =
            getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
        std::string nameSuffixStr = env->GetStringUTFChars(nameSuffix, 0);
        thisHandle->set_name_prefix(nameSuffixStr);
    }
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getStartFrame
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getStartFrame(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return thisHandle->start_frame();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setStartFrame
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setStartFrame(
    JNIEnv* env, jobject thisObj, jint startFrame)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    thisHandle->set_start_frame(startFrame);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getFrameStep
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getFrameStep(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return thisHandle->frame_step();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setFrameStep
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setFrameStep(
    JNIEnv* env, jobject thisObj, jint frameStep)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    thisHandle->set_frame_step(frameStep);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getRate
 * Signature: ()D
 */
JNIEXPORT jdouble JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getRate(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return thisHandle->rate();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setRate
 * Signature: (D)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setRate(
    JNIEnv* env, jobject thisObj, jdouble rate)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    thisHandle->set_rate(rate);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getFrameZeroPadding
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getFrameZeroPadding(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return thisHandle->frame_zero_padding();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setFrameZeroPadding
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setFrameZeroPadding(
    JNIEnv* env, jobject thisObj, jint frameZeroPadding)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    thisHandle->set_frame_zero_padding(frameZeroPadding);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getMissingFramePolicyNative
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getMissingFramePolicyNative(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return (int) (thisHandle->missing_frame_policy());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    setMissingFramePolicyNative
 * Signature: (I)V
 */
JNIEXPORT void JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_setMissingFramePolicyNative(
    JNIEnv* env, jobject thisObj, jint missingFramePolicyIndex)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    thisHandle->set_missing_frame_policy(
        OTIO_NS::ImageSequenceReference::MissingFramePolicy(
            missingFramePolicyIndex));
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getEndFrame
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getEndFrame(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return thisHandle->end_frame();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getNumberOfImagesInSequence
 * Signature: ()I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getNumberOfImagesInSequence(
    JNIEnv* env, jobject thisObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    return thisHandle->number_of_images_in_sequence();
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getFrameForTimeNative
 * Signature: ([DLio/opentimeline/opentimelineio/ErrorStatus;)I
 */
JNIEXPORT jint JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getFrameForTimeNative(
    JNIEnv*      env,
    jobject      thisObj,
    jdoubleArray rationalTime,
    jobject      errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    opentime::RationalTime rt = rationalTimeFromArray(env, rationalTime);
    auto                   errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return thisHandle->frame_for_time(rt, errorStatusHandle);
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    getTargetURLForImageNumber
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_getTargetURLForImageNumber(
    JNIEnv* env, jobject thisObj, jint imageNumber, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    return env->NewStringUTF(
        thisHandle->target_url_for_image_number(imageNumber, errorStatusHandle)
            .c_str());
}

/*
 * Class:     io_opentimeline_opentimelineio_ImageSequenceReference
 * Method:    presentationTimeForImageNumberNative
 * Signature: (ILio/opentimeline/opentimelineio/ErrorStatus;)[D
 */
JNIEXPORT jdoubleArray JNICALL
Java_io_opentimeline_opentimelineio_ImageSequenceReference_presentationTimeForImageNumberNative(
    JNIEnv* env, jobject thisObj, jint imageNumber, jobject errorStatusObj)
{
    auto thisHandle = getHandle<OTIO_NS::ImageSequenceReference>(env, thisObj);
    auto errorStatusHandle =
        getHandle<OTIO_NS::ErrorStatus>(env, errorStatusObj);
    opentime::RationalTime rt = thisHandle->presentation_time_for_image_number(
        imageNumber, errorStatusHandle);
    return rationalTimeToArray(env, rt);
}
