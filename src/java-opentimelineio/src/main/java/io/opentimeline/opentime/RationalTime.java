package io.opentimeline.opentime;

public class RationalTime implements Comparable<RationalTime> {

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

    public RationalTime add(RationalTime other) {
        return rationalTimeFromArray(addNative(rationalTimeToArray(this), rationalTimeToArray(other)));
    }

    private static native double[] addNative(double[] rationalTime, double[] rationalTimeOther);

    public RationalTime subtract(RationalTime other) {
        return rationalTimeFromArray(subtractNative(rationalTimeToArray(this), rationalTimeToArray(other)));
    }

    private static native double[] subtractNative(double[] rationalTime, double[] rationalTimeOther);

    public RationalTime rescaledTo(double newRate) {
        return rationalTimeFromArray(rescaledToNative(rationalTimeToArray(this), newRate));
    }

    private static native double[] rescaledToNative(double[] rationalTime, double newRate);

    public RationalTime rescaledTo(RationalTime rationalTime) {
        return rationalTimeFromArray(rescaledToNative(rationalTimeToArray(this), rationalTimeToArray(rationalTime)));
    }

    private static native double[] rescaledToNative(double[] rationalTime, double[] other);

    public double valueRescaledTo(double newRate) {
        return valueRescaledToNative(rationalTimeToArray(this), newRate);
    }

    private static native double valueRescaledToNative(double[] rationalTime, double newRate);

    public double valueRescaledTo(RationalTime rationalTime) {
        return valueRescaledToNative(rationalTimeToArray(this), rationalTimeToArray(rationalTime));
    }

    private static native double valueRescaledToNative(double[] rationalTime, double[] other);

    public boolean almostEqual(RationalTime other) {
        return almostEqualNative(rationalTimeToArray(this), rationalTimeToArray(other));
    }

    private static native boolean almostEqualNative(double[] rationalTime, double[] other);

    public boolean almostEqual(RationalTime other, double delta) {
        return almostEqualNative(rationalTimeToArray(this), rationalTimeToArray(other), delta);
    }

    private static native boolean almostEqualNative(double[] rationalTime, double[] other, double delta);

    public static RationalTime durationFromStartEndTime(RationalTime startTime, RationalTime endTimeExclusive) {
        return rationalTimeFromArray(durationFromStartEndTimeNative(rationalTimeToArray(startTime), rationalTimeToArray(endTimeExclusive)));
    }

    private static native double[] durationFromStartEndTimeNative(double[] startTime, double[] endTimeExclusive);

    public static native boolean isValidTimecodeRate(double rate);

    public static RationalTime fromFrames(double frame, double rate) {
        return new RationalTime((int) frame, rate);
    }

    public static RationalTime fromSeconds(double seconds) {
        return new RationalTime(seconds, 1);
    }

    public static RationalTime fromTimecode(String timecode, double rate, ErrorStatus errorStatus) {
        return rationalTimeFromArray(fromTimecodeNative(timecode, rate, errorStatus));
    }

    private static native double[] fromTimecodeNative(String timecode, double rate, ErrorStatus errorStatus);

    public static RationalTime fromTimeString(String timeString, double rate, ErrorStatus errorStatus) {
        return rationalTimeFromArray(fromTimeStringNative(timeString, rate, errorStatus));
    }

    private static native double[] fromTimeStringNative(String timeString, double rate, ErrorStatus errorStatus);

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
        return toTimecodeNative(rationalTimeToArray(this), rate, dropFrame.getIndex(), errorStatus);
    }

    public String toTimecode(ErrorStatus errorStatus) {
        return toTimecodeNative(rationalTimeToArray(this), getRate(), IsDropFrameRate.InferFromRate.getIndex(), errorStatus);
    }

    private static native String toTimecodeNative(double[] rationalTime, double rate, int dropFrameIndex, ErrorStatus errorStatus);

    public String toTimeString() {
        return toTimeStringNative(rationalTimeToArray(this));
    }

    private static native String toTimeStringNative(double[] rationalTime);

    public boolean equals(RationalTime rationalTime) {
        return this.compareTo(rationalTime) == 0;
    }

    private static RationalTime rationalTimeFromArray(double[] rationalTime) {
        return new RationalTime(rationalTime[0], rationalTime[1]);
    }

    private static double[] rationalTimeToArray(RationalTime rationalTime) {
        return new double[]{rationalTime.getValue(), rationalTime.getRate()};
    }

    @Override
    public int compareTo(RationalTime rationalTime) {
        return compareToNative(rationalTimeToArray(this), rationalTimeToArray(rationalTime));
    }

    private native int compareToNative(double[] rationalTime, double[] other);
}
