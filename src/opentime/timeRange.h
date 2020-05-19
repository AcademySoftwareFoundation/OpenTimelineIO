#pragma once

#include "opentime/version.h"
#include "opentime/rationalTime.h"
#include <algorithm>
#include <string>

namespace opentime {
    namespace OPENTIME_VERSION {

/**
 * It is possible to construct TimeRange object with a negative duration.
 * However, the logical predicates are written as if duration is positive,
 * and have undefined behavior for negative durations.
 *
 * The duration on a TimeRange indicates a time range that is inclusive of the start time,
 * and exclusive of the end time. All of the predicates are computed accordingly.
 */

/**
 * This default epsilon value is used in comparison between floating numbers.
 * It is computed to be twice 192khz, the fastest commonly used audio rate.
 * It can be changed in the future if necessary due to higher sampling rates
 * or some other kind of numeric tolerance detected in the library.
 */
constexpr double DEFAULT_EPSILON_s = 1.0 / (2 * 192000.0);

class TimeRange {
public:
    explicit TimeRange() : _start_time{}, _duration{} {}

    explicit TimeRange(RationalTime start_time)
            : _start_time{start_time}, _duration{RationalTime{0, start_time.rate()}} {}

    explicit TimeRange(RationalTime start_time, RationalTime duration)
            : _start_time{start_time}, _duration{duration} {}

    TimeRange(TimeRange const &) = default;

    TimeRange &operator=(TimeRange const &) = default;

    RationalTime const &start_time() const {
        return _start_time;
    }

    RationalTime const &duration() const {
        return _duration;
    }

    RationalTime end_time_inclusive() const {
        RationalTime et = end_time_exclusive();

        if ((et - _start_time.rescaled_to(_duration))._value > 1) {
            return _duration._value != floor(_duration._value) ? et._floor() :
                   et - RationalTime(1, _duration._rate);
        } else {
            return _start_time;
        }
    }

    RationalTime end_time_exclusive() const {
        return _duration + _start_time.rescaled_to(_duration);
    }

    TimeRange duration_extended_by(RationalTime other) const {
        return TimeRange{_start_time, _duration + other};
    }

    TimeRange extended_by(TimeRange other) const {
        RationalTime new_start_time{std::min(_start_time, other._start_time)},
                new_end_time{std::max(end_time_exclusive(), other.end_time_exclusive())};

        return TimeRange{new_start_time,
                         RationalTime::duration_from_start_end_time(new_start_time, new_end_time)};
    }

    RationalTime clamped(RationalTime other) const {
        return std::min(std::max(other, _start_time), end_time_inclusive());
    }

    TimeRange clamped(TimeRange other) const {
        TimeRange r{std::max(other._start_time, _start_time), other._duration};
        RationalTime end{std::min(r.end_time_exclusive(), end_time_exclusive())};
        return TimeRange{r._start_time, end - r._start_time};
    }

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
     *                    other
     *                      ↓
     *                      *
     *              [      this      ]
     * @param other
     */
    bool contains(RationalTime other) const {
        return _start_time <= other && other < end_time_exclusive();
    }

    /**
     * The start of <b>this</b> precedes start of <b>other</b>.
     * The end of <b>this</b> antecedes end of <b>other</b>.
     *                   [ other ]
     *              [      this      ]
     * The converse would be <em>other.contains(this)</em>
     * @param other
     */
    bool contains(TimeRange other) const {
        return _start_time <= other._start_time && end_time_exclusive() >= other.end_time_exclusive();
    }

    /**
     * <b>this</b> contains <b>other</b>.
     *                   other
     *                    ↓
     *                    *
     *              [    this    ]
     * @param other
     */
    bool overlaps(RationalTime other) const {
        return contains(other);
    }

    /**
     * The start of <b>this</b> strictly precedes end of <b>other</b> by a value >= <b>epsilon</b>.
     * The end of <b>this</b> strictly antecedes start of <b>other</b> by a value >= <b>epsilon</b>.
     *              [ this ]
     *                  [ other ]
     * The converse would be <em>other.overlaps(this)</em>
     * @param other
     * @param epsilon
     */
    bool overlaps(TimeRange other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisStart = _start_time.to_seconds();
        double thisEnd = end_time_exclusive().to_seconds();
        double otherStart = other._start_time.to_seconds();
        double otherEnd = other.end_time_exclusive().to_seconds();
        return (otherEnd - thisStart >= epsilon) &&
               (thisEnd - otherStart >= epsilon);
    }

    /**
     * The end of <b>this</b> strictly precedes the start of <b>other</b> by a value >= <b>epsilon</b>.
     *              [ this ]    [ other ]
     * The converse would be <em>other.before(this)</em>
     * @param other
     * @param epsilon
     */
    bool before(TimeRange other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisEnd = end_time_exclusive().to_seconds();
        double otherStart = other._start_time.to_seconds();
        return otherStart - thisEnd >= epsilon;
    }

    /**
     * The end of <b>this</b> strictly precedes <b>other</b> by a value >= <b>epsilon</b>.
     *                        other
     *                          ↓
     *              [ this ]    *
     * @param other
     * @param epsilon
     */
    bool before(RationalTime other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisEnd = end_time_exclusive().to_seconds();
        double otherTime = other.to_seconds();
        return otherTime - thisEnd >= epsilon;
    }

    /**
     * The end of <b>this</b> strictly equals the start of <b>other</b> and
     * the start of <b>this</b> strictly equals the end of <b>other</b>.
     *              [this][other]
     * The converse would be <em>other.meets(this)</em>
     * @param other
     * @param epsilon
     */
    bool meets(TimeRange other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisEnd = end_time_exclusive().to_seconds();
        double otherStart = other._start_time.to_seconds();
        return otherStart - thisEnd <= epsilon && otherStart - thisEnd >= 0;
    }

    /**
     * The start of <b>this</b> strictly equals the start of <b>other</b>.
     * The end of <b>this</b> strictly precedes the end of <b>other</b> by a value >= <b>epsilon</b>.
     *              [ this ]
     *              [    other    ]
     * The converse would be <em>other.begins(this)</em>
     * @param other
     * @param epsilon
     */
    bool begins(TimeRange other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisStart = _start_time.to_seconds();
        double thisEnd = end_time_exclusive().to_seconds();
        double otherStart = other._start_time.to_seconds();
        double otherEnd = other.end_time_exclusive().to_seconds();
        return fabs(otherStart - thisStart) <= epsilon && otherEnd - thisEnd >= epsilon;
    }

    /**
     * The start of <b>this</b> strictly equals <b>other</b>.
     *            other
     *              ↓
     *              *
     *              [ this ]
     * @param other
     */
    bool begins(RationalTime other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisStart = _start_time.to_seconds();
        double otherStart = other.to_seconds();
        return fabs(otherStart - thisStart) <= epsilon;
    }

    /**
     * The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value >= <b>epsilon</b>.
     * The end of <b>this</b> strictly equals the end of <b>other</b>.
     *                      [ this ]
     *              [     other    ]
     * The converse would be <em>other.finishes(this)</em>
     * @param other
     * @param epsilon
     */
    bool finishes(TimeRange other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisStart = _start_time.to_seconds();
        double thisEnd = end_time_exclusive().to_seconds();
        double otherStart = other._start_time.to_seconds();
        double otherEnd = other.end_time_exclusive().to_seconds();
        return fabs(thisEnd - otherEnd) <= epsilon && thisStart - otherStart >= epsilon;
    }

    /**
     * The end of <b>this</b> strictly equals <b>other</b>.
     *                   other
     *                     ↓
     *                     *
     *              [ this ]
     * @param other
     * @param epsilon
     */
    bool finishes(RationalTime other, double epsilon = DEFAULT_EPSILON_s) const {
        double thisEnd = end_time_exclusive().to_seconds();
        double otherEnd = other.to_seconds();
        return fabs(thisEnd - otherEnd) <= epsilon;
    }


    /**
     * The start of <b>lhs</b> strictly equals the start of <b>rhs</b>.
     * The end of <b>lhs</b> strictly equals the end of <b>rhs</b>.
     *              [ lhs ]
     *              [ rhs ]
     * @param lhs
     * @param rhs
     */
    friend bool operator==(TimeRange lhs, TimeRange rhs) {
        RationalTime start = lhs._start_time - rhs._start_time;
        RationalTime duration = lhs._duration - rhs._duration;
        return fabs(start.to_seconds()) < DEFAULT_EPSILON_s &&
               fabs(duration.to_seconds()) < DEFAULT_EPSILON_s;
    }

    /**
     * Converse of <em>equals()</em> operator
     * @param lhs
     * @param rhs
     */
    friend bool operator!=(TimeRange lhs, TimeRange rhs) {
        return !(lhs == rhs);
    }

    static TimeRange range_from_start_end_time(RationalTime start_time, RationalTime end_time_exclusive) {
        return TimeRange{start_time,
                         RationalTime::duration_from_start_end_time(start_time, end_time_exclusive)};
    }

private:
    RationalTime _start_time, _duration;
    friend class TimeTransform;
};

} }

