package io.opentimeline.opentime;

import io.opentimeline.OTIONative;

public class TimeTransform extends OTIONative {

    public TimeTransform() {
        this.initialize(new RationalTime(), 1, -1);
    }

    public TimeTransform(RationalTime offset, double scale, double rate) {
        this.initialize(offset, scale, rate);
    }

    public TimeTransform(TimeTransform timeTransform) {
        this.initialize(timeTransform.getOffset(), timeTransform.getScale(), timeTransform.getRate());
    }

    public TimeTransform(TimeTransform.TimeTransformBuilder timeTransformBuilder) {
        this.initialize(timeTransformBuilder.offset, timeTransformBuilder.scale, timeTransformBuilder.rate);
    }

    public TimeTransform(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public static class TimeTransformBuilder {
        private RationalTime offset = new RationalTime();
        private double scale = 1;
        private double rate = -1;

        public TimeTransformBuilder() {
        }

        public TimeTransform.TimeTransformBuilder setOffset(RationalTime offset) {
            this.offset = offset;
            return this;
        }

        public TimeTransform.TimeTransformBuilder setScale(double scale) {
            this.scale = scale;
            return this;
        }

        public TimeTransform.TimeTransformBuilder setRate(double rate) {
            this.rate = rate;
            return this;
        }

        public TimeTransform build() {
            return new TimeTransform(offset, scale, rate);
        }
    }

    private native void initialize(RationalTime offset, double scale, double rate);

    public native RationalTime getOffset();

    public native double getScale();

    public native double getRate();

    public native TimeRange appliedTo(TimeRange other);

    public native TimeTransform appliedTo(TimeTransform other);

    public native RationalTime appliedTo(RationalTime other);

    public native boolean equals(TimeTransform other);

    public native boolean notEquals(TimeTransform other);

    private native void dispose();

    @Override
    protected void finalize() throws Throwable {
        dispose();
    }
}
