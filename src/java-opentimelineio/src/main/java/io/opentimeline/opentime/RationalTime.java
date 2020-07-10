package io.opentimeline.opentime;

import io.opentimeline.OTIONative;

public class RationalTime extends OTIONative implements Comparable<RationalTime> {

    public long nativeHandle;

    public RationalTime() {
        this.initialize(0, 1);
    }

    public RationalTime(double value, double rate) {
        this.initialize(value, rate);
    }

    public RationalTime(long nativeHandle) {
        this.nativeHandle = nativeHandle;
    }

    public RationalTime(RationalTimeBuilder rationalTimeBuilder) {
        this.initialize(rationalTimeBuilder.value, rationalTimeBuilder.rate);
    }

    public RationalTime(RationalTime rationalTime) {
        this.initialize(rationalTime.getValue(), rationalTime.getRate());
    }

    public static class RationalTimeBuilder {
        private double value = 0;
        private double rate = 1;

        public RationalTimeBuilder() {
        }

        public RationalTimeBuilder setValue(double value) {
            this.value = value;
            return this;
        }

        public RationalTimeBuilder setRate(double rate) {
            this.rate = rate;
            return this;
        }

        public RationalTime build() {
            return new RationalTime(this);
        }
    }

    private native void initialize(double value, double rate);

    public native double getValue();

    public native double getRate();

    public native boolean isInvalidTime();

    public native RationalTime add(RationalTime other);

    public native RationalTime subtract(RationalTime other);

    public native RationalTime rescaledTo(double newRate);

    public native RationalTime rescaledTo(RationalTime rationalTime);

    public native double valueRescaledTo(double newRate);

    public native double valueRescaledTo(RationalTime rationalTime);

    public native boolean almostEqual(RationalTime other);

    public native boolean almostEqual(RationalTime other, double delta);

    public static native RationalTime durationFromStartEndTime(RationalTime startTime, RationalTime endTimeExclusive);

    public static native boolean isValidTimecodeRate(double rate);

    public static RationalTime fromFrames(double frame, double rate) {
        return new RationalTime((int) frame, rate);
    }

    public static RationalTime fromSeconds(double seconds) {
        return new RationalTime(seconds, 1);
    }

    public static native RationalTime fromTimecode(String timecode, double rate, ErrorStatus errorStatus);

    public static native RationalTime fromTimeString(String timeString, double rate, ErrorStatus errorStatus);

    public int toFrames() {
        return (int) getValue();
    }

    public int toFrames(double rate) {
        return (int) valueRescaledTo(rate);
    }

    public double toSeconds() {
        return valueRescaledTo(1);
    }

    public String toTimecode(double rate, IsDropFrameRate dropFrame, ErrorStatus errorStatus) {
        return toTimecodeNative(rate, dropFrame.getIndex(), errorStatus);
    }

    public String toTimecode(ErrorStatus errorStatus) {
        return toTimecodeNative(getRate(), IsDropFrameRate.InferFromRate.getIndex(), errorStatus);
    }

    public native String toTimecodeNative(double rate, int dropFrameIndex, ErrorStatus errorStatus);

    public native String toTimeString();

    public boolean equals(RationalTime rationalTime) {
        return this.compareTo(rationalTime) == 0;
    }

    @Override
    public native int compareTo(RationalTime rationalTime);

    private native void dispose();

    @Override
    protected void finalize() throws Throwable {
        dispose();
    }
}
