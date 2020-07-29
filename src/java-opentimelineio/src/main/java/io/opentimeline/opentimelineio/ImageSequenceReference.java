package io.opentimeline.opentimelineio;

import io.opentimeline.OTIONative;
import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;

public class ImageSequenceReference extends MediaReference {

    public enum MissingFramePolicy {
        error,
        hold,
        black,
    }

    protected ImageSequenceReference() {
    }

    ImageSequenceReference(OTIONative otioNative) {
        this.nativeManager = otioNative;
    }

    public ImageSequenceReference(
            String targetURLBase,
            String namePrefix,
            String nameSuffix,
            int startFrame,
            int frameStep,
            double rate,
            int frameZeroPadding,
            MissingFramePolicy missingFramePolicy,
            TimeRange availableRange,
            AnyDictionary metadata) {
        this.initObject(
                targetURLBase,
                namePrefix,
                nameSuffix,
                startFrame,
                frameStep,
                rate,
                frameZeroPadding,
                missingFramePolicy,
                availableRange,
                metadata);
    }

    public ImageSequenceReference(ImageSequenceReference.ImageSequenceReferenceBuilder imageSequenceReferenceBuilder) {
        this.initObject(
                imageSequenceReferenceBuilder.targetURLBase,
                imageSequenceReferenceBuilder.namePrefix,
                imageSequenceReferenceBuilder.nameSuffix,
                imageSequenceReferenceBuilder.startFrame,
                imageSequenceReferenceBuilder.frameStep,
                imageSequenceReferenceBuilder.rate,
                imageSequenceReferenceBuilder.frameZeroPadding,
                imageSequenceReferenceBuilder.missingFramePolicy,
                imageSequenceReferenceBuilder.availableRange,
                imageSequenceReferenceBuilder.metadata);
    }

    private void initObject(String targetURLBase,
                            String namePrefix,
                            String nameSuffix,
                            int startFrame,
                            int frameStep,
                            double rate,
                            int frameZeroPadding,
                            MissingFramePolicy missingFramePolicy,
                            TimeRange availableRange,
                            AnyDictionary metadata) {
        this.initialize(
                targetURLBase,
                namePrefix,
                nameSuffix,
                startFrame,
                frameStep,
                rate,
                frameZeroPadding,
                missingFramePolicy.ordinal(),
                availableRange,
                metadata);
        this.nativeManager.className = this.getClass().getCanonicalName();
    }

    private native void initialize(String targetURLBase,
                                   String namePrefix,
                                   String nameSuffix,
                                   int startFrame,
                                   int frameStep,
                                   double rate,
                                   int frameZeroPadding,
                                   int missingFramePolicy,
                                   TimeRange availableRange,
                                   AnyDictionary metadata);

    public static class ImageSequenceReferenceBuilder {
        String targetURLBase = "";
        String namePrefix = "";
        String nameSuffix = "";
        int startFrame = 1;
        int frameStep = 1;
        double rate = 1;
        int frameZeroPadding = 0;
        MissingFramePolicy missingFramePolicy = MissingFramePolicy.error;
        TimeRange availableRange = null;
        AnyDictionary metadata = new AnyDictionary();

        public ImageSequenceReferenceBuilder() {
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setTargetURLBase(String targetURLBase) {
            this.targetURLBase = targetURLBase;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setNamePrefix(String namePrefix) {
            this.namePrefix = namePrefix;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setNameSuffix(String nameSuffix) {
            this.nameSuffix = nameSuffix;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setStartFrame(int startFrame) {
            this.startFrame = startFrame;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setFrameStep(int frameStep) {
            this.frameStep = frameStep;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setRate(double rate) {
            this.rate = rate;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setFrameZeroPadding(int frameZeroPadding) {
            this.frameZeroPadding = frameZeroPadding;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setMissingFramePolicy(MissingFramePolicy missingFramePolicy) {
            this.missingFramePolicy = missingFramePolicy;
            return this;
        }

        public ImageSequenceReference.ImageSequenceReferenceBuilder setAvailableRange(TimeRange availableRange) {
            this.availableRange = availableRange;
            return this;
        }


        public ImageSequenceReference.ImageSequenceReferenceBuilder setMetadata(AnyDictionary metadata) {
            this.metadata = metadata;
            return this;
        }

        public ImageSequenceReference build() {
            return new ImageSequenceReference(this);
        }
    }

    public native String getTargetURLBase();

    public native void setTargetURLBase(String targetURLBase);

    public native String getNamePrefix();

    public native void setNamePrefix(String namePrefix);

    public native String getNameSuffix();

    public native void setNameSuffix(String nameSuffix);

    public native int getStartFrame();

    public native void setStartFrame(int startFrame);

    public native int getFrameStep();

    public native void setFrameStep(int frameStep);

    public native double getRate();

    public native void setRate(double rate);

    public native int getFrameZeroPadding();

    public native void setFrameZeroPadding(int frameZeroPadding);

    public MissingFramePolicy getMissingFramePolicy() {
        return MissingFramePolicy.values()[getMissingFramePolicyNative()];
    }

    private native int getMissingFramePolicyNative();

    public void setMissingFramePolicy(MissingFramePolicy missingFramePolicy) {
        this.setMissingFramePolicyNative(missingFramePolicy.ordinal());
    }

    private native void setMissingFramePolicyNative(int missingFramePolicy);

    public native int getEndFrame();

    public native int getNumberOfImagesInSequence();

    public native int getFrameForTime(RationalTime rationalTime, ErrorStatus errorStatus);

    public native String getTargetURLForImageNumber(int imageNumber, ErrorStatus errorStatus);

    public native RationalTime presentationTimeForImageNumber(int imageNumber, ErrorStatus errorStatus);
}
