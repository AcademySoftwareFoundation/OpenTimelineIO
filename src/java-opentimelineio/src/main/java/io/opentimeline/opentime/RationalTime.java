package io.opentimeline.opentime;

import io.opentimeline.LibraryLoader;

/**
 * Represents an instantaneous point in time, value * (1/rate) seconds
 * from time 0 seconds.
 */
public class RationalTime implements Comparable<RationalTime> {

    static {
        LibraryLoader.load("jotio");
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

    /**
     * @return value
     */
    public double getValue() {
        return value;
    }

    /**
     * @return rate
     */
    public double getRate() {
        return rate;
    }

    /**
     * Check if the RationalTime represents a valid value and rate pair.
     *
     * @return is value and rate pair a valid RationalTime?
     */
    public boolean isInvalidTime() {
        return isInvalidTimeNative(value, rate);
    }

    private static native boolean isInvalidTimeNative(double value, double rate);

    /**
     * Returns a RationalTime object that is the sum of this and other.
     * If this and other have differing time rates, the result will have the
     * have the rate of the faster time.
     *
     * @param other other RationalTime to add
     * @return sum of the two RationalTimes
     */
    public native RationalTime add(RationalTime other);

    /**
     * Returns a RationalTime object that is this - other.
     * If this and other have differing time rates, the result will have the
     * have the rate of the faster time.
     *
     * @param other other RationalTime to add
     * @return difference of the two RationalTimes
     */
    public native RationalTime subtract(RationalTime other);

    /**
     * Returns the time for this time converted to newRate
     *
     * @param newRate new rate
     * @return time for this time converted to newRate
     */
    public native RationalTime rescaledTo(double newRate);

    /**
     * Returns the time for this time converted to new rate of a RationalTime
     *
     * @param rationalTime RationalTime for new rate
     * @return time for this time converted to new rate of a RationalTime
     */
    public native RationalTime rescaledTo(RationalTime rationalTime);

    /**
     * Returns the time value for this converted to newRate
     *
     * @param newRate new Rate
     * @return time value for this converted to newRate
     */
    public native double valueRescaledTo(double newRate);

    /**
     * Returns the time value for this converted to new rate of a RationalTime
     *
     * @param rationalTime RationalTime for new rate
     * @return time value for this converted to new rate of a RationalTime
     */
    public native double valueRescaledTo(RationalTime rationalTime);

    /**
     * Checks if the two RationalTimes equal with a default tolerance of 0.
     *
     * @param other other RationalTime
     * @return are the two RationalTimes equal with a default tolerance of 0?
     */
    public native boolean almostEqual(RationalTime other);

    /**
     * Checks if the two RationalTimes equal with a tolerance of delta.
     *
     * @param other other RationalTime
     * @param delta tolerance for equality comparison
     * @return are the two RationalTimes equal with a tolerance of delta?
     */
    public native boolean almostEqual(RationalTime other, double delta);

    /**
     * Compute duration of samples from first to last.
     * This is not the same as distance.
     * For example, the duration of a clip from frame 10 to frame 15 is 6 frames.
     * The result will be at the rate of startTime.
     *
     * @param startTime        start time of duration
     * @param endTimeExclusive end time of duration
     * @return duration
     */
    public static native RationalTime durationFromStartEndTime(RationalTime startTime, RationalTime endTimeExclusive);

    /**
     * Check if the timecode rate is valid.
     *
     * @param rate frame rate in question
     * @return is the timecode rate valid?
     */
    public static native boolean isValidTimecodeRate(double rate);

    /**
     * Creates a RationalTime from frame number and fps
     *
     * @param frame frame number
     * @param rate  rate
     * @return equivalent RationalTime
     */
    public static RationalTime fromFrames(double frame, double rate) {
        return new RationalTime((int) frame, rate);
    }

    /**
     * Creates a RationalTime from time in seconds at rate 1.
     *
     * @param seconds time in seconds
     * @return equivalent RationalTime at rate 1
     */
    public static RationalTime fromSeconds(double seconds) {
        return new RationalTime(seconds, 1);
    }

    /**
     * Convert timecode to RationalTime.
     *
     * @param timecode    a colon-delimited timecode
     * @param rate        the frame-rate to calculate timecode in terms of
     * @param errorStatus errorStatus to report error in conversion
     * @return RationalTime equivalent to timecode
     */
    public static native RationalTime fromTimecode(String timecode, double rate, ErrorStatus errorStatus);

    /**
     * Convert a time with microseconds string into a RationalTime
     *
     * @param timeString  a HH:MM:ss.ms time
     * @param rate        The frame-rate to calculate timecode in terms of
     * @param errorStatus errorStatus to report error in conversion
     * @return RationalTime equivalent to timestring
     */
    public static native RationalTime fromTimeString(String timeString, double rate, ErrorStatus errorStatus);

    /**
     * Convert RationalTime to integer frames at same rate
     *
     * @return integer frames equivalent to the RationalTime at same rate
     */
    public int toFrames() {
        return (int) getValue();
    }

    /**
     * Convert RationalTime to integer frames at new rate
     *
     * @param rate new rate
     * @return integer frames equivalent to the RationalTime at new rate
     */
    public int toFrames(double rate) {
        return (int) valueRescaledTo(rate);
    }

    /**
     * Convert RationalTime to time value in seconds
     *
     * @return time value in seconds
     */
    public double toSeconds() {
        return valueRescaledTo(1);
    }

    /**
     * Convert RationalTime to timecode
     *
     * @param rate        the frame-rate to calculate timecode in terms of
     * @param dropFrame   should the algorithm drop frames while conversion? [InferFromRate, ForceYes, ForceNo]
     * @param errorStatus errorStatus to report error in conversion
     * @return equivalent timecode
     */
    public String toTimecode(double rate, IsDropFrameRate dropFrame, ErrorStatus errorStatus) {
        return toTimecodeNative(this, rate, dropFrame.getIndex(), errorStatus);
    }

    /**
     * Convert RationalTime to timecode and automatically infer if the frame rate is a Drop FrameRate.
     *
     * @param errorStatus errorStatus to report error in conversion
     * @return equivalent timecode
     */
    public String toTimecode(ErrorStatus errorStatus) {
        return toTimecodeNative(this, getRate(), IsDropFrameRate.InferFromRate.getIndex(), errorStatus);
    }

    private static native String toTimecodeNative(RationalTime rationalTime, double rate, int dropFrameIndex, ErrorStatus errorStatus);

    /**
     * Convert to time with microseconds as formatted in FFMPEG
     *
     * @return number formatted string of the RationalTime
     */
    public native String toTimeString();

    public native boolean equals(RationalTime rationalTime);

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof RationalTime))
            return false;
        return this.equals((RationalTime) obj);
    }

    /**
     * Compare two RationalTimes
     *
     * @param rationalTime other RationalTime
     * @return <b>0</b> if equal, <b>&lt;0</b> if lhs&lt;rhs, <b>&gt;0</b> if lhs&gt;rhs
     */
    @Override
    public native int compareTo(RationalTime rationalTime);

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "value=" + this.getValue() +
                ", rate=" + this.getRate() +
                ")";
    }
}
