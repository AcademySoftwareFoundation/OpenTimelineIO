package io.opentimeline.opentime;

import io.opentimeline.LibraryLoader;
import io.opentimeline.OTIOObject;

/**
 * It is possible to construct TimeRange object with a negative duration.
 * However, the logical predicates are written as if duration is positive,
 * and have undefined behavior for negative durations.
 * <p>
 * The duration on a TimeRange indicates a time range that is inclusive of the start time,
 * and exclusive of the end time. All of the predicates are computed accordingly.
 * <p>
 * <p>
 * This default epsilon value is used in comparison between floating numbers.
 * It is computed to be twice 192khz, the fastest commonly used audio rate.
 * It can be changed in the future if necessary due to higher sampling rates
 * or some other kind of numeric tolerance detected in the library.
 */
public class TimeRange {

    static {
        if (!LibraryLoader.load(OTIOObject.class, "jotio"))
            System.loadLibrary("jotio");
    }

    private final RationalTime startTime;
    private final RationalTime duration;

    public TimeRange() {
        startTime = new RationalTime();
        duration = new RationalTime();
    }

    public TimeRange(RationalTime startTime) {
        this.startTime = startTime;
        duration = new RationalTime(0, startTime.getRate());
    }

    public TimeRange(RationalTime startTime, RationalTime duration) {
        this.startTime = startTime;
        this.duration = duration;
    }

    public TimeRange(TimeRangeBuilder timeRangeBuilder) {
        if (timeRangeBuilder.startTime == null && timeRangeBuilder.duration == null) {
            this.startTime = new RationalTime();
            this.duration = new RationalTime();
        } else if (timeRangeBuilder.startTime == null) {
            this.startTime = new RationalTime(0, timeRangeBuilder.duration.getRate());
            this.duration = timeRangeBuilder.duration;
        } else if (timeRangeBuilder.duration == null) {
            this.startTime = timeRangeBuilder.startTime;
            this.duration = new RationalTime(0, timeRangeBuilder.startTime.getRate());
        } else {
            this.startTime = timeRangeBuilder.startTime;
            this.duration = timeRangeBuilder.duration;
        }
    }

    public TimeRange(TimeRange timeRange) {
        this.startTime = timeRange.getStartTime();
        this.duration = timeRange.getDuration();
    }

    public static class TimeRangeBuilder {
        private RationalTime startTime = null;
        private RationalTime duration = null;

        public TimeRangeBuilder() {
        }

        public TimeRange.TimeRangeBuilder setStartTime(RationalTime startTime) {
            this.startTime = startTime;
            return this;
        }

        public TimeRange.TimeRangeBuilder setDuration(RationalTime duration) {
            this.duration = duration;
            return this;
        }

        public TimeRange build() {
            if (startTime == null && duration == null) {
                return new TimeRange();
            } else if (startTime == null) {
                return new TimeRange(new RationalTime(0, duration.getRate()), duration);
            } else if (duration == null) {
                return new TimeRange(startTime, new RationalTime(0, startTime.getRate()));
            } else {
                return new TimeRange(startTime, duration);
            }
        }
    }

    public RationalTime getStartTime() {
        return startTime;
    }

    public RationalTime getDuration() {
        return duration;
    }

    public native RationalTime endTimeInclusive();

    public native RationalTime endTimeExclusive();

    public native TimeRange durationExtendedBy(RationalTime other);

    public native TimeRange extendedBy(TimeRange other);

    public native RationalTime clamped(RationalTime other);

    public native TimeRange clamped(TimeRange other);

    /**
     * These relations implement James F. Allen's thirteen basic time interval relations.
     * Detailed background can be found here: https://dl.acm.org/doi/10.1145/182.358434
     * Allen, James F. "Maintaining knowledge about temporal intervals".
     * Communications of the ACM 26(11) pp.832-843, Nov. 1983.
     */

    /**
     * In the relations that follow, epsilon indicates the tolerance,in the sense that if abs(a-b) < epsilon,
     * we consider a and b to be equal
     */

    /**
     * The start of <b>this</b> precedes <b>other</b>.
     * <b>other</b> precedes the end of this.
     * other
     * ↓
     * *
     * [      this      ]
     *
     * @param other
     */
    public native boolean contains(RationalTime other);

    /**
     * The start of <b>this</b> precedes start of <b>other</b>.
     * The end of <b>this</b> antecedes end of <b>other</b>.
     * [ other ]
     * [      this      ]
     * The converse would be <em>other.contains(this)</em>
     *
     * @param other
     */
    public native boolean contains(TimeRange other);

    /**
     * <b>this</b> contains <b>other</b>.
     * other
     * ↓
     * *
     * [    this    ]
     *
     * @param other
     */
    public native boolean overlaps(RationalTime other);

    /**
     * The start of <b>this</b> strictly precedes end of <b>other</b> by a value >= <b>epsilon</b>.
     * The end of <b>this</b> strictly antecedes start of <b>other</b> by a value >= <b>epsilon</b>.
     * [ this ]
     * [ other ]
     * The converse would be <em>other.overlaps(this)</em>
     *
     * @param other
     * @param epsilon
     */
    public native boolean overlaps(TimeRange other, double epsilon);

    /**
     * The start of <b>this</b> strictly precedes end of <b>other</b> by a value >= <b>epsilon</b>.
     * The end of <b>this</b> strictly antecedes start of <b>other</b> by a value >= <b>epsilon</b>.
     * [ this ]
     * [ other ]
     * The converse would be <em>other.overlaps(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean overlaps(TimeRange other);

    /**
     * The end of <b>this</b> strictly precedes the start of <b>other</b> by a value >= <b>epsilon</b>.
     * [ this ]    [ other ]
     * The converse would be <em>other.before(this)</em>
     *
     * @param other
     * @param epsilon
     */
    public native boolean before(TimeRange other, double epsilon);

    /**
     * The end of <b>this</b> strictly precedes the start of <b>other</b> by a value >= <b>epsilon</b>.
     * [ this ]    [ other ]
     * The converse would be <em>other.before(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean before(TimeRange other);

    /**
     * The end of <b>this</b> strictly precedes <b>other</b> by a value >= <b>epsilon</b>.
     * other
     * ↓
     * [ this ]    *
     *
     * @param other
     * @param epsilon
     */
    public native boolean before(RationalTime other, double epsilon);
    /**
     * The end of <b>this</b> strictly precedes <b>other</b> by a value >= <b>epsilon</b>.
     * other
     * ↓
     * [ this ]    *
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean before(RationalTime other);

    /**
     * The end of <b>this</b> strictly equals the start of <b>other</b> and
     * the start of <b>this</b> strictly equals the end of <b>other</b>.
     * [this][other]
     * The converse would be <em>other.meets(this)</em>
     *
     * @param other
     * @param epsilon
     */
    public native boolean meets(TimeRange other, double epsilon);

    /**
     * The end of <b>this</b> strictly equals the start of <b>other</b> and
     * the start of <b>this</b> strictly equals the end of <b>other</b>.
     * [this][other]
     * The converse would be <em>other.meets(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean meets(TimeRange other);

    /**
     * The start of <b>this</b> strictly equals the start of <b>other</b>.
     * The end of <b>this</b> strictly precedes the end of <b>other</b> by a value >= <b>epsilon</b>.
     * [ this ]
     * [    other    ]
     * The converse would be <em>other.begins(this)</em>
     *
     * @param other
     * @param epsilon
     */
    public native boolean begins(TimeRange other, double epsilon);

    /**
     * The start of <b>this</b> strictly equals the start of <b>other</b>.
     * The end of <b>this</b> strictly precedes the end of <b>other</b> by a value >= <b>epsilon</b>.
     * [ this ]
     * [    other    ]
     * The converse would be <em>other.begins(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean begins(TimeRange other);

    /**
     * The start of <b>this</b> strictly equals <b>other</b>.
     * other
     * ↓
     * *
     * [ this ]
     *
     * @param other
     */
    public native boolean begins(RationalTime other, double epsilon);

    /**
     * The start of <b>this</b> strictly equals <b>other</b>.
     * other
     * ↓
     * *
     * [ this ]
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean begins(RationalTime other);

    /**
     * The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value >= <b>epsilon</b>.
     * The end of <b>this</b> strictly equals the end of <b>other</b>.
     * [ this ]
     * [     other    ]
     * The converse would be <em>other.finishes(this)</em>
     *
     * @param other
     * @param epsilon
     */
    public native boolean finishes(TimeRange other, double epsilon);

    /**
     * The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value >= <b>epsilon</b>.
     * The end of <b>this</b> strictly equals the end of <b>other</b>.
     * [ this ]
     * [     other    ]
     * The converse would be <em>other.finishes(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other
     */
    public native boolean finishes(TimeRange other);

    /**
     * The end of <b>this</b> strictly equals <b>other</b>.
     * other
     * ↓
     * *
     * [ this ]
     *
     * @param other
     * @param epsilon
     */
    public native boolean finishes(RationalTime other, double epsilon);

    /**
     * The end of <b>this</b> strictly equals <b>other</b>.
     * other
     * ↓
     * *
     * [ this ]
     *
     * @param other
     */
    public native boolean finishes(RationalTime other);

    public native boolean equals(TimeRange other);

    public native boolean notEquals(TimeRange other);

    public native static TimeRange rangeFromStartEndTime(RationalTime startTime, RationalTime endTime);

    public static double[] timeRangeToArray(TimeRange timeRange) {
        if (timeRange == null) throw new NullPointerException();
        return new double[]{
                timeRange.getStartTime().getValue(), timeRange.getStartTime().getRate(),
                timeRange.getDuration().getValue(), timeRange.getDuration().getRate()
        };
    }

    public static TimeRange timeRangeFromArray(double[] timeRange) {
        if (timeRange.length != 4) throw new RuntimeException("Unable to convert array to TimeRange");
        return new TimeRange(
                new RationalTime(timeRange[0], timeRange[1]),
                new RationalTime(timeRange[2], timeRange[3]));
    }
}
