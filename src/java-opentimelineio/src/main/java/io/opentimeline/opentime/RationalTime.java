package io.opentimeline.opentime;

import io.opentimeline.LibraryLoader;
import io.opentimeline.OTIOObject;

public class RationalTime implements Comparable<RationalTime> {

    static {
        if (!LibraryLoader.load(OTIOObject.class, "jotio"))
            System.loadLibrary("jotio");
    }

    private final double value;
    private final double rate;

    public RationalTime() {
        value = 0;
        rate = 1;
    }

    public RationalTime(double value, double rate) {
        this.value = value;
        this.rate = rate;
    }

    public RationalTime(RationalTimeBuilder rationalTimeBuilder) {
        this.value = rationalTimeBuilder.value;
        this.rate = rationalTimeBuilder.rate;
    }

    public RationalTime(RationalTime rationalTime) {
        this.value = rationalTime.getValue();
        this.rate = rationalTime.getRate();
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

    public double getValue() {
        return value;
    }

    public double getRate() {
        return rate;
    }

    public boolean isInvalidTime() {
        return isInvalidTimeNative(value, rate);
    }

    private static native boolean isInvalidTimeNative(double value, double rate);

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
        return toTimecodeNative(this, rate, dropFrame.getIndex(), errorStatus);
    }

    public String toTimecode(ErrorStatus errorStatus) {
        return toTimecodeNative(this, getRate(), IsDropFrameRate.InferFromRate.getIndex(), errorStatus);
    }

    private static native String toTimecodeNative(RationalTime rationalTime, double rate, int dropFrameIndex, ErrorStatus errorStatus);

    public native String toTimeString();

    public native boolean equals(RationalTime rationalTime);

    public static RationalTime rationalTimeFromArray(double[] rationalTime) {
        if (rationalTime.length != 2) throw new RuntimeException("Unable to convert array to RationalTime");
        return new RationalTime(rationalTime[0], rationalTime[1]);
    }

    public static double[] rationalTimeToArray(RationalTime rationalTime) {
        if (rationalTime == null) throw new NullPointerException();
        return new double[]{rationalTime.getValue(), rationalTime.getRate()};
    }

    @Override
    public native int compareTo(RationalTime rationalTime);
}
