// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/rationalTime.h"
#include "opentime/version.h"
#include <algorithm>
#include <string>

namespace opentime { namespace OPENTIME_VERSION {

/// @brief This default epsilon_s value is used in comparison between floating numbers.
///
/// It is computed to be twice 192kHz, the fastest commonly used audio rate. That gives
/// a resolution of half a frame at 192kHz. The value can be changed in the future if
/// necessary, due to higher sampling rates or some other kind of numeric tolerance
/// detected in the library.
OPENTIME_EXPORT constexpr double DEFAULT_EPSILON_s = 1.0 / (2 * 192000.0);

/// @brief This class represents a time range defined by a start time and duration.
///
/// It is possible to construct a TimeRange object with a negative duration.
/// However, the logical predicates are written as if duration is positive,
/// and have undefined behavior for negative durations.
///
/// The duration on a TimeRange indicates a time range that is inclusive of the
/// start time, and exclusive of the end time. All of the predicates are
/// computed accordingly.
class OPENTIME_EXPORT TimeRange
{
public:
    /// @brief Construct a new time range with a zero start time and duration.
    constexpr TimeRange() noexcept
        : _start_time{}
        , _duration{}
    {}

    /// @brief Construct a new time range with the given start time and duration of zero.
    explicit constexpr TimeRange(RationalTime start_time) noexcept
        : _start_time{ start_time }
        , _duration{ RationalTime{ 0, start_time.rate() } }
    {}

    /// @brief Construct a new time range with the given start time and duration.
    constexpr TimeRange(
        RationalTime start_time,
        RationalTime duration) noexcept
        : _start_time{ start_time }
        , _duration{ duration }
    {}

    /// @brief Construct a new time range with the given start time, duration, and rate.
    constexpr TimeRange(
        double start_time,
        double duration,
        double rate) noexcept
        : _start_time{ start_time, rate }
        , _duration{ duration, rate }
    {}

    /// @brief Returns true if the time range is invalid.
    ///
    /// The time range is considered invalid if either the start time or
    /// duration is invalid, or if the duration is less than zero.
    bool is_invalid_range() const noexcept
    {
        return _start_time.is_invalid_time() || _duration.is_invalid_time() || _duration.value() < 0.0;
    }

    /// @brief Returns true if the time range is valid.
    ///
    /// The time range is considered valid if both the start time and
    /// duration are valid, and the duration is greater than or equal to
    /// zero.
    bool is_valid_range() const noexcept
    {
        return _start_time.is_valid_time() && _duration.is_valid_time() && _duration.value() >= 0.0;
    }

    /// @brief Returns the start time.
    constexpr RationalTime start_time() const noexcept { return _start_time; }

    /// @brief Returns the duration.
    constexpr RationalTime duration() const noexcept { return _duration; }

    /// @brief Returns the inclusive end time.
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

    /// @brief Returns the exclusive end time.
    constexpr RationalTime end_time_exclusive() const noexcept
    {
        return _duration + _start_time.rescaled_to(_duration);
    }

    /// @brief Extend a time range's duration by the given time. The extended
    /// time range is returned.
    constexpr TimeRange duration_extended_by(RationalTime other) const noexcept
    {
        return TimeRange{ _start_time, _duration + other };
    }

    /// @brief Extend a time range by the given time. The extended time range
    /// is returned.
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

    /// @brief Clamp a time to this time range. The clamped time is returned.
    RationalTime clamped(RationalTime other) const noexcept
    {
        return std::min(std::max(other, _start_time), end_time_inclusive());
    }

    /// @brief Clamp a time range to this time range. The clamped time range
    /// is returned.
    constexpr TimeRange clamped(TimeRange other) const noexcept
    {
        const TimeRange    r{ std::max(other._start_time, _start_time),
                           other._duration };
        const RationalTime end{
            std::min(r.end_time_exclusive(), end_time_exclusive())
        };
        return TimeRange{ r._start_time, end - r._start_time };
    }

    /// @name Time Range Relations
    ///
    /// These relations implement James F. Allen's thirteen basic time interval relations.
    /// Detailed background can be found here: https://dl.acm.org/doi/10.1145/182.358434
    /// Allen, James F. "Maintaining knowledge about temporal intervals".
    /// Communications of the ACM 26(11) pp.832-843, Nov. 1983.
    ///
    /// In the relations that follow, epsilon_s indicates the tolerance, in the sense
    /// that if abs(a-b) < epsilon_s, we consider a and b to be equal. The time
    /// comparison is done in double seconds.
    ///
    ///@{

    /// @brief Returns whether this time range contains the given time.
    ///
    /// The start of <b>this</b> precedes <b>other</b>.
    /// <b>other</b> precedes the end of this.
    /// <pre>
    ///                    other
    ///                      ↓
    ///                      *
    ///              [      this      ]
    /// </pre>
    constexpr bool contains(RationalTime other) const noexcept
    {
        return _start_time <= other && other < end_time_exclusive();
    }

    /// @brief Returns whether this time range contains the given time range.
    ///
    /// The start of <b>this</b> precedes start of <b>other</b>.
    /// The end of <b>this</b> antecedes end of <b>other</b>.
    /// <pre>
    ///                   [ other ]
    ///              [      this      ]
    /// </pre>
    /// The converse would be <em>other.contains(this)</em>
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

    /// @brief Returns whether this time range overlaps the given time.
    ///
    /// <b>this</b> contains <b>other</b>.
    /// <pre>
    ///                   other
    ///                    ↓
    ///                    *
    ///              [    this    ]
    /// </pre>
    constexpr bool overlaps(RationalTime other) const noexcept
    {
        return contains(other);
    }

    /// @brief Returns whether this and the given time range overlap.
    ///
    /// The start of <b>this</b> strictly precedes end of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// The end of <b>this</b> strictly antecedes start of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// <pre>
    ///              [ this ]
    ///                  [ other ]
    /// </pre>
    /// The converse would be <em>other.overlaps(this)</em>
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

    /// @brief Returns whether this time range precedes the given time range.
    ///
    /// The end of <b>this</b> strictly precedes the start of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// <pre>
    ///              [ this ]    [ other ]
    /// </pre>
    /// The converse would be <em>other.before(this)</em>
    constexpr bool
    before(TimeRange other, double epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        return greater_than(otherStart, thisEnd, epsilon_s);
    }

    /// @brief Returns whether this time range precedes the given time.
    ///
    /// The end of <b>this</b> strictly precedes <b>other</b> by a value >= <b>epsilon_s</b>.
    /// <pre>
    ///                        other
    ///                          ↓
    ///              [ this ]    *
    /// </pre>
    constexpr bool before(
        RationalTime other,
        double       epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd   = end_time_exclusive().to_seconds();
        const double otherTime = other.to_seconds();
        return lesser_than(thisEnd, otherTime, epsilon_s);
    }

    /// @brief Returns whether this time range meets the given time range.
    ///
    /// The end of <b>this</b> strictly equals the start of <b>other</b> and
    /// the start of <b>this</b> strictly equals the end of <b>other</b>.
    /// <pre>
    ///              [this][other]
    /// </pre>
    /// The converse would be <em>other.meets(this)</em>
    constexpr bool
    meets(TimeRange other, double epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd    = end_time_exclusive().to_seconds();
        const double otherStart = other._start_time.to_seconds();
        return otherStart - thisEnd <= epsilon_s && otherStart - thisEnd >= 0;
    }

    /// @brief Returns whether this time range begins in the given time range.
    ///
    /// The start of <b>this</b> strictly equals the start of <b>other</b>.
    /// The end of <b>this</b> strictly precedes the end of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// <pre>
    ///              [ this ]
    ///              [    other    ]
    /// </pre>
    /// The converse would be <em>other.begins(this)</em>
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

    /// @brief Returns whether this range begins at the given time.
    ///
    /// The start of <b>this</b> strictly equals <b>other</b>.
    /// <pre>
    ///            other
    ///              ↓
    ///              *
    ///              [ this ]
    /// </pre>
    constexpr bool begins(
        RationalTime other,
        double       epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisStart  = _start_time.to_seconds();
        const double otherStart = other.to_seconds();
        return fabs(otherStart - thisStart) <= epsilon_s;
    }

    /// @brief Returns whether this time range finishes in the given time range.
    ///
    /// The start of <b>this</b> strictly antecedes the start of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// The end of <b>this</b> strictly equals the end of <b>other</b>.
    /// <pre>
    ///                      [ this ]
    ///              [     other    ]
    /// </pre>
    /// The converse would be <em>other.finishes(this)</em>
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

    /// @brief Return whether this time range finishes at the given time.
    ///
    /// The end of <b>this</b> strictly equals <b>other</b>.
    /// <pre>
    ///                   other
    ///                     ↓
    ///                     *
    ///              [ this ]
    /// </pre>
    constexpr bool finishes(
        RationalTime other,
        double       epsilon_s = DEFAULT_EPSILON_s) const noexcept
    {
        const double thisEnd  = end_time_exclusive().to_seconds();
        const double otherEnd = other.to_seconds();
        return fabs(thisEnd - otherEnd) <= epsilon_s;
    }

    /// Return whether this time range intersects the given time range.
    ///
    /// The start of <b>this</b> precedes or equals the end of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// The end of <b>this</b> antecedes or equals the start of <b>other</b> by a value >= <b>epsilon_s</b>.
    /// <pre>
    ///         [    this    ]           OR      [    other    ]
    ///              [     other    ]                    [     this    ]
    /// </pre>
    /// The converse would be <em>other.finishes(this)</em>
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

    ///@}

    /// @brief Returns whether two time ranges are strictly equal.
    ///
    /// The start of <b>lhs</b> strictly equals the start of <b>rhs</b>.
    /// The end of <b>lhs</b> strictly equals the end of <b>rhs</b>.
    /// <pre>
    ///              [ lhs ]
    ///              [ rhs ]
    /// </pre>
    friend constexpr bool operator==(TimeRange lhs, TimeRange rhs) noexcept
    {
        const RationalTime start    = lhs._start_time - rhs._start_time;
        const RationalTime duration = lhs._duration - rhs._duration;
        return fabs(start.to_seconds()) < DEFAULT_EPSILON_s
               && fabs(duration.to_seconds()) < DEFAULT_EPSILON_s;
    }

    /// @brief Returns whether two time ranges are not equal.
    friend constexpr bool operator!=(TimeRange lhs, TimeRange rhs) noexcept
    {
        return !(lhs == rhs);
    }

    /// @brief Create a time range from a start time and exclusive end time.
    static constexpr TimeRange range_from_start_end_time(
        RationalTime start_time,
        RationalTime end_time_exclusive) noexcept
    {
        return TimeRange{ start_time,
                          RationalTime::duration_from_start_end_time(
                              start_time,
                              end_time_exclusive) };
    }

    /// @brief Create a time range from a start time and inclusive end time.
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
