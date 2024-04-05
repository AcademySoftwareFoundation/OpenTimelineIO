// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/rationalTime.h"
#include "opentime/version.h"
#include <algorithm>
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

/**
 * It is possible to construct TimeRange object with a negative duration.
 * However, the logical predicates are written as if duration is positive,
 * and have undefined behavior for negative durations.
 *
 * The duration on a TimeRange indicates a time range that is inclusive of the start time,
 * and exclusive of the end time. All of the predicates are computed accordingly.
 */

/**
 * This default epsilon_s value is used in comparison between floating numbers.
 * It is computed to be twice 192khz, the fastest commonly used audio rate.
 * It can be changed in the future if necessary due to higher sampling rates
 * or some other kind of numeric tolerance detected in the library.
 */
constexpr double DEFAULT_EPSILON_s = 1.0 / (2 * 192000.0);

class TimeRange
{
public:
    explicit constexpr TimeRange() noexcept
        : _start_time{}
        , _duration{}
    {}

    explicit constexpr TimeRange(RationalTime start_time) noexcept
        : _start_time{ start_time }
        , _duration{ RationalTime{ 0, start_time.rate() } }
    {}

    explicit constexpr TimeRange(
        RationalTime start_time,
        RationalTime duration) noexcept
        : _start_time{ start_time }
        , _duration{ duration }
    {}

    TimeRange(TimeRange const&) noexcept = default;

    TimeRange& operator=(TimeRange const&) noexcept = default;

    constexpr RationalTime start_time() const noexcept { return _start_time; }

    constexpr RationalTime duration() const noexcept { return _duration; }

    RationalTime end_time_inclusive() const noexcept
    {
        const RationalTime et = end_time_exclusive();

        if ((et - _start_time.rescaled_to(_duration))._value > 1)
        {
            return _duration._value != std::floor(_duration._value)
                       ? et.floor()
                       : et - RationalTime(1, _duration._rate);
        }
        else
        {
            return _start_time;
        }
    }

    constexpr RationalTime end_time_exclusive() const noexcept
    {
        return _duration + _start_time.rescaled_to(_duration);
    }

    constexpr TimeRange duration_extended_by(RationalTime other) const noexcept
    {
        return TimeRange{ _start_time, _duration + other };
    }

    constexpr TimeRange extended_by(TimeRange other) const noexcept
    {
        const RationalTime new_start_time{
            std::min(_start_time, other._start_time)
        },
            new_end_time{
                std::max(end_time_exclusive(), other.end_time_exclusive())
            };

        return TimeRange{ new_start_time,
                          RationalTime::duration_from_start_end_time(
                              new_start_time,
                              new_end_time) };
    }

    RationalTime clamped(RationalTime other) const noexcept
    {
        return std::min(std::max(other, _start_time), end_time_inclusive());
    }

    constexpr TimeRange clamped(TimeRange other) const noexcept
    {
        const TimeRange    r{ std::max(other._start_time, _start_time),
                           other._duration };
        const RationalTime end{
            std::min(r.end_time_exclusive(), end_time_exclusive())
        };
        return TimeRange{ r._start_time, end - r._start_time };
    }

    /**
     * These relations implement James F. Allen's thirteen basic time interval relations.
     * Detailed background can be found here: https://dl.acm.org/doi/10.1145/182.358434
     * Allen, James F. "Maintaining knowledge about temporal intervals".
     * Communications of the ACM 26(11) pp.832-843, Nov. 1983.
     */

    /**
     * In the relations that follow, epsilon_s indicates the tolerance,in the sense that if abs(a-b) < epsilon_s,
     * we consider a and b to be equal.
     * The time comparison is done in double seconds.
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
    constexpr bool contains(RationalTime other) const noexcept
    {
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
    constexpr bool contains(
        TimeRange other,
        double    epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        const double otherEnd   = other.end_time_exclusive().to_seconds();
        return greater_than(otherStart, thisStart, epsilon_s)
               && lesser_than(otherEnd, thisEnd, epsilon_s);
    }

    /**
     * <b>this</b> contains <b>other</b>.
     *                   other
     *                    ↓
     *                    *
     *              [    this    ]
     * @param other
     */
    constexpr bool overlaps(RationalTime other) const noexcept
    {
        return contains(other);
    }

    /**
     * The start of <b>this</b> strictly precedes end of <b>other</b> by a value >= <b>epsilon_s</b>.
     * The end of <b>this</b> strictly antecedes start of <b>other</b> by a value >= <b>epsilon_s</b>.
     *              [ this ]
     *                  [ other ]
     * The converse would be <em>other.overlaps(this)</em>
     * @param other
     * @param epsilon_s
     */
    constexpr bool overlaps(
        TimeRange other,
        double    epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        const double otherEnd   = other.end_time_exclusive().to_seconds();
        return lesser_than(thisStart, otherStart, epsilon_s)
               && greater_than(thisEnd, otherStart, epsilon_s)
               && greater_than(otherEnd, thisEnd, epsilon_s);
    }

    /**
     * The end of <b>this</b> strictly precedes the start of <b>other</b> by a value >= <b>epsilon_s</b>.
     *              [ this ]    [ other ]
     * The converse would be <em>other.before(this)</em>
     * @param other
     * @param epsilon_s
     */
    constexpr bool
    before(TimeRange other, double epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        return greater_than(otherStart, thisEnd, epsilon_s);
    }

    /**
     * The end of <b>this</b> strictly precedes <b>other</b> by a value >= <b>epsilon_s</b>.
     *                        other
     *                          ↓
     *              [ this ]    *
     * @param other
     * @param epsilon_s
     */
    constexpr bool before(
        RationalTime other,
        double       epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd   = end_time_exclusive().to_seconds();
        const double otherTime = other.to_seconds();
        return lesser_than(thisEnd, otherTime, epsilon_s);
    }

    /**
     * The end of <b>this</b> strictly equals the start of <b>other</b> and
     * the start of <b>this</b> strictly equals the end of <b>other</b>.
     *              [this][other]
     * The converse would be <em>other.meets(this)</em>
     * @param other
     * @param epsilon_s
     */
    constexpr bool
    meets(TimeRange other, double epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        return otherStart - thisEnd <= epsilon_s && otherStart - thisEnd >= 0;
    }

    /**
     * The start of <b>this</b> strictly equals the start of <b>other</b>.
     * The end of <b>this</b> strictly precedes the end of <b>other</b> by a value >= <b>epsilon_s</b>.
     *              [ this ]
     *              [    other    ]
     * The converse would be <em>other.begins(this)</em>
     * @param other
     * @param epsilon_s
     */
    constexpr bool
    begins(TimeRange other, double epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        const double otherEnd   = other.end_time_exclusive().to_seconds();
        return fabs(otherStart - thisStart) <= epsilon_s
               && lesser_than(thisEnd, otherEnd, epsilon_s);
    }

    /**
     * The start of <b>this</b> strictly equals <b>other</b>.
     *            other
     *              ↓
     *              *
     *              [ this ]
     * @param other
     */
    constexpr bool begins(
        RationalTime other,
        double       epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double otherStart = other.to_seconds();
        return fabs(otherStart - thisStart) <= epsilon_s;
    }

    /**
     * The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value >= <b>epsilon_s</b>.
     * The end of <b>this</b> strictly equals the end of <b>other</b>.
     *                      [ this ]
     *              [     other    ]
     * The converse would be <em>other.finishes(this)</em>
     * @param other
     * @param epsilon_s
     */
    constexpr bool finishes(
        TimeRange other,
        double    epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        const double otherEnd   = other.end_time_exclusive().to_seconds();
        return fabs(thisEnd - otherEnd) <= epsilon_s
               && greater_than(thisStart, otherStart, epsilon_s);
    }

    /**
     * The end of <b>this</b> strictly equals <b>other</b>.
     *                   other
     *                     ↓
     *                     *
     *              [ this ]
     * @param other
     * @param epsilon_s
     */
    constexpr bool finishes(
        RationalTime other,
        double       epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd  = end_time_exclusive().to_seconds();
        const double otherEnd = other.to_seconds();
        return fabs(thisEnd - otherEnd) <= epsilon_s;
    }

    /**
     * The start of <b>this</b> precedes or equals the end of <b>other</b> by a value >= <b>epsilon_s</b>.
     * The end of <b>this</b> antecedes or equals the start of <b>other</b> by a value >= <b>epsilon_s</b>.
     *         [    this    ]           OR      [    other    ]
     *              [     other    ]                    [     this    ]
     * The converse would be <em>other.finishes(this)</em>
     * @param other
     * @param epsilon_s
     */
    constexpr bool intersects(
        TimeRange other,
        double    epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        const double otherEnd   = other.end_time_exclusive().to_seconds();
        return lesser_than(thisStart, otherEnd, epsilon_s)
               && greater_than(thisEnd, otherStart, epsilon_s);
    }

    /**
     * The start of <b>lhs</b> strictly equals the start of <b>rhs</b>.
     * The end of <b>lhs</b> strictly equals the end of <b>rhs</b>.
     *              [ lhs ]
     *              [ rhs ]
     * @param lhs
     * @param rhs
     */
    friend constexpr bool operator==(TimeRange lhs, TimeRange rhs) noexcept
    {
        const RationalTime start    = lhs._start_time - rhs._start_time;
        const RationalTime duration = lhs._duration - rhs._duration;
        return fabs(start.to_seconds()) < DEFAULT_EPSILON_s
               && fabs(duration.to_seconds()) < DEFAULT_EPSILON_s;
    }

    /**
     * Converse of <em>equals()</em> operator
     * @param lhs
     * @param rhs
     */
    friend constexpr bool operator!=(TimeRange lhs, TimeRange rhs) noexcept
    {
        return !(lhs == rhs);
    }

    static constexpr TimeRange range_from_start_end_time(
        RationalTime start_time,
        RationalTime end_time_exclusive) noexcept
    {
        return TimeRange{ start_time,
                          RationalTime::duration_from_start_end_time(
                              start_time,
                              end_time_exclusive) };
    }

    static constexpr TimeRange range_from_start_end_time_inclusive(
        RationalTime start_time,
        RationalTime end_time_inclusive) noexcept
    {
        return TimeRange{ start_time,
                          RationalTime::duration_from_start_end_time_inclusive(
                              start_time,
                              end_time_inclusive) };
    }

private:
    RationalTime _start_time, _duration;
    friend class TimeTransform;

    constexpr bool
    greater_than(double lhs, double rhs, double epsilon) const noexcept
    {
        return lhs - rhs >= epsilon;
    }

    constexpr bool
    lesser_than(double lhs, double rhs, double epsilon) const noexcept
    {
        return rhs - lhs >= epsilon;
    }
};

}} // namespace opentime::OPENTIME_VERSION
