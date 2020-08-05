package io.opentimeline.opentime;

import io.opentimeline.LibraryLoader;
import io.opentimeline.OTIOObject;

public class TimeTransform {

    static {
        if (!LibraryLoader.load(OTIOObject.class, "jotio"))
            System.loadLibrary("jotio");
    }

    private final RationalTime offset;
    private final double scale;
    private final double rate;

    public TimeTransform() {
        offset = new RationalTime();
        scale = 1;
        rate = -1;
    }

    public TimeTransform(RationalTime offset, double scale, double rate) {
        this.offset = offset;
        this.scale = scale;
        this.rate = rate;
    }

    public TimeTransform(TimeTransform timeTransform) {
        this.offset = timeTransform.getOffset();
        this.scale = timeTransform.getScale();
        this.rate = timeTransform.getRate();
    }

    public TimeTransform(TimeTransform.TimeTransformBuilder timeTransformBuilder) {
        this.offset = timeTransformBuilder.offset;
        this.scale = timeTransformBuilder.scale;
        this.rate = timeTransformBuilder.rate;
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

    public RationalTime getOffset() {
        return offset;
    }

    public double getScale() {
        return scale;
    }

    public double getRate() {
        return rate;
    }

    public native TimeRange appliedTo(TimeRange other);

    public native TimeTransform appliedTo(TimeTransform other);

    public native RationalTime appliedTo(RationalTime other);

    public native boolean equals(TimeTransform other);

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof TimeTransform))
            return false;
        return this.equals((TimeTransform) obj);
    }

    public native boolean notEquals(TimeTransform other);
}
