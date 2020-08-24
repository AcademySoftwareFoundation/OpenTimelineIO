package io.opentimeline.opentime;

import io.opentimeline.LibraryLoader;
import io.opentimeline.OTIOObject;

/**
 * Contains a range of time, starting (and including) startTime and
 * lasting duration.value * (1/duration.rate) seconds.
 * <p>
 * It is possible to construct TimeRange object with a negative duration.
 * However, the logical predicates are written as if duration is positive,
 * and have undefined behavior for negative durations.
 * <p>
 * The duration on a TimeRange indicates a time range that is inclusive of the start time,
 * and exclusive of the end time. All of the predicates are computed accordingly.
 * <p>
 * This default epsilon value is used in comparison between floating numbers.
 * It is computed to be twice 192khz, the fastest commonly used audio rate.
 * It can be changed in the future if necessary due to higher sampling rates
 * or some other kind of numeric tolerance detected in the library.
 */
public class TimeRange {

    static {
        LibraryLoader.load("jotio");
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

    /**
     * The time of the last sample that contains data in the TimeRange.
     * If the TimeRange goes from (0, 24) w/ duration (10, 24), this will be
     * (9, 24)
     * If the TimeRange goes from (0, 24) w/ duration (10.5, 24):
     * (10, 24)
     * In other words, the last frame with data (however fractional).
     *
     * @return time of the last sample that contains data in the TimeRange
     */
    public native RationalTime endTimeInclusive();

    /**
     * Time of the first sample outside the time range.
     * If Start Frame is 10 and duration is 5, then endTimeExclusive is 15,
     * even though the last time with data in this range is 14.
     * If Start Frame is 10 and duration is 5.5, then endTimeExclusive is
     * 15.5, even though the last time with data in this range is 15.
     *
     * @return time of the first sample outside the time range
     */
    public native RationalTime endTimeExclusive();

    public native TimeRange durationExtendedBy(RationalTime other);

    /**
     * Construct a new TimeRange that is this one extended by another
     *
     * @param other timeRange by which the duration is extended
     * @return extended TimeRange
     */
    public native TimeRange extendedBy(TimeRange other);

    /**
     * Clamp 'other', according to this.startTime/endTimeExclusive
     *
     * @param other RationalTime to clamp to
     * @return clamped TimeRange
     */
    public native RationalTime clamped(RationalTime other);

    /**
     * Clamp 'other', according to this.startTime/endTimeExclusive
     *
     * @param other TimeRange to clamp to
     * @return clamped TimeRange
     */
    public native TimeRange clamped(TimeRange other);

    /*
     * These relations implement James F. Allen's thirteen basic time interval relations.
     * Detailed background can be found here: https://dl.acm.org/doi/10.1145/182.358434
     * Allen, James F. "Maintaining knowledge about temporal intervals".
     * Communications of the ACM 26(11) pp.832-843, Nov. 1983.
     */

    /*
     * In the relations that follow, epsilon indicates the tolerance,in the sense that if abs(a-b) &lt; epsilon,
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
     * @param other RationalTime to check for
     * @return does this contain other
     */
    public native boolean contains(RationalTime other);

    /**
     * The start of <b>this</b> precedes start of <b>other</b>.
     * The end of <b>this</b> antecedes end of <b>other</b>.
     * [ other ]
     * [      this      ]
     * The converse would be <em>other.contains(this)</em>
     *
     * @param other TimeRange to check for
     * @return does this contain other
     */
    public native boolean contains(TimeRange other);

    /**
     * <b>this</b> contains <b>other</b>.
     * other
     * ↓
     * *
     * [    this    ]
     *
     * @param other RationalTime to check for
     * @return does this overlap other
     */
    public native boolean overlaps(RationalTime other);

    /**
     * The start of <b>this</b> strictly precedes end of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * The end of <b>this</b> strictly antecedes start of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * [ this ]
     * [ other ]
     * The converse would be <em>other.overlaps(this)</em>
     *
     * @param other   TimeRange to check for
     * @param epsilon comparison tolerance
     * @return does this overlap other
     */
    public native boolean overlaps(TimeRange other, double epsilon);

    /**
     * The start of <b>this</b> strictly precedes end of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * The end of <b>this</b> strictly antecedes start of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * [ this ]
     * [ other ]
     * The converse would be <em>other.overlaps(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other TimeRange to check for
     * @return does this overlap other
     */
    public native boolean overlaps(TimeRange other);

    /**
     * The end of <b>this</b> strictly precedes the start of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * [ this ]    [ other ]
     * The converse would be <em>other.before(this)</em>
     *
     * @param other   TimeRange to check for
     * @param epsilon comparison tolerance
     * @return is this before other
     */
    public native boolean before(TimeRange other, double epsilon);

    /**
     * The end of <b>this</b> strictly precedes the start of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * [ this ]    [ other ]
     * The converse would be <em>other.before(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other TimeRange to check for
     * @return is this before other
     */
    public native boolean before(TimeRange other);

    /**
     * The end of <b>this</b> strictly precedes <b>other</b> by a value &gt;= <b>epsilon</b>.
     * other
     * ↓
     * [ this ]    *
     *
     * @param other   RationalTime to check for
     * @param epsilon comparison tolerance
     * @return is this before other
     */
    public native boolean before(RationalTime other, double epsilon);

    /**
     * The end of <b>this</b> strictly precedes <b>other</b> by a value &gt;= <b>epsilon</b>.
     * other
     * ↓
     * [ this ]    *
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other RationalTime to check for
     * @return is this before other
     */
    public native boolean before(RationalTime other);

    /**
     * The end of <b>this</b> strictly equals the start of <b>other</b> and
     * the start of <b>this</b> strictly equals the end of <b>other</b>.
     * [this][other]
     * The converse would be <em>other.meets(this)</em>
     *
     * @param other   TimeRange to check for
     * @param epsilon comparison tolerance
     * @return does this meet other
     */
    public native boolean meets(TimeRange other, double epsilon);

    /**
     * The end of <b>this</b> strictly equals the start of <b>other</b> and
     * the start of <b>this</b> strictly equals the end of <b>other</b>.
     * [this][other]
     * The converse would be <em>other.meets(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other TimeRange to check for
     * @return does this meet other
     */
    public native boolean meets(TimeRange other);

    /**
     * The start of <b>this</b> strictly equals the start of <b>other</b>.
     * The end of <b>this</b> strictly precedes the end of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * [ this ]
     * [    other    ]
     * The converse would be <em>other.begins(this)</em>
     *
     * @param other   TimeRange to check for
     * @param epsilon comparison tolerance
     * @return do the beginnings of both match
     */
    public native boolean begins(TimeRange other, double epsilon);

    /**
     * The start of <b>this</b> strictly equals the start of <b>other</b>.
     * The end of <b>this</b> strictly precedes the end of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * [ this ]
     * [    other    ]
     * The converse would be <em>other.begins(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other TimeRange to check for
     * @return do the beginnings of both match
     */
    public native boolean begins(TimeRange other);

    /**
     * The start of <b>this</b> strictly equals <b>other</b>.
     * other
     * ↓
     * *
     * [ this ]
     *
     * @param other RationalTime to check for
     * @param epsilon comparison tolerance
     * @return does the RationalTime match the beginning of this
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
     * @param other RationalTime to check for
     * @return does the RationalTime match the beginning of this
     */
    public native boolean begins(RationalTime other);

    /**
     * The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * The end of <b>this</b> strictly equals the end of <b>other</b>.
     * [ this ]
     * [     other    ]
     * The converse would be <em>other.finishes(this)</em>
     *
     * @param other   TimeRange to check for
     * @param epsilon comparison tolerance
     * @return do the ends of both match
     */
    public native boolean finishes(TimeRange other, double epsilon);

    /**
     * The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value &gt;= <b>epsilon</b>.
     * The end of <b>this</b> strictly equals the end of <b>other</b>.
     * [ this ]
     * [     other    ]
     * The converse would be <em>other.finishes(this)</em>
     * Default epsilon value of 1/(2 * 192000) will be used
     *
     * @param other TimeRange to check for
     * @return do the ends of both match
     */
    public native boolean finishes(TimeRange other);

    /**
     * The end of <b>this</b> strictly equals <b>other</b>.
     *      other
     *        ↓
     *        *
     * [ this ]
     *
     * @param other   RationalTime to check for
     * @param epsilon comparison tolerance
     * @return does the RationalTime match the end of this
     */
    public native boolean finishes(RationalTime other, double epsilon);

    /**
     * The end of <b>this</b> strictly equals <b>other</b>.
     *      other
     *        ↓
     *        *
     * [ this ]
     *
     * @param other RationalTime to check for
     * @return does the RationalTime match the end of this
     */
    public native boolean finishes(RationalTime other);

    public native boolean equals(TimeRange other);

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof TimeRange))
            return false;
        return this.equals((TimeRange) obj);
    }

    public native boolean notEquals(TimeRange other);

    /**
     * Create a TimeRange from start and end RationalTimes
     *
     * @param startTime start time
     * @param endTime   end time
     * @return TimeRange from start and end RationalTimes
     */
    public native static TimeRange rangeFromStartEndTime(RationalTime startTime, RationalTime endTime);

    @Override
    public String toString() {
        return this.getClass().getCanonicalName() +
                "(" +
                "startTime=" + this.getStartTime() +
                ", duration=" + this.getDuration() +
                ")";
    }
}
