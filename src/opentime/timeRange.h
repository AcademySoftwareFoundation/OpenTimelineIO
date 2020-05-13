#pragma once

#include "opentime/version.h"
#include "opentime/rationalTime.h"
#include <algorithm>
#include <string>

namespace opentime {
    namespace OPENTIME_VERSION {

/**It is possible to construct TimeRange object with a negative duration.
 * However, the logical predicates are written as if duration is positive,
 * and have undefined behavior for negative durations.
 */

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
             * Detailed background can be found here: https://www.ics.uci.edu/~alspaugh/cls/shr/allen.html
             */

            /**contains(other)
             * params: RationalTime other
             * The start of self precedes other.
             * other precedes the end of self.
             */
            bool contains(RationalTime other) const {
                return _start_time <= other && other < end_time_exclusive();
            }

            /**contains(other)
             * params: TimeRange other
             * The start of self precedes start of other.
             * The end of self antecedes end of other.
             * The converse would be other.contains(self)
             */
            bool contains(TimeRange other) const {
                return _start_time <= other._start_time && end_time_exclusive() >= other.end_time_exclusive();
            }

            /**overlaps(other)
             * params: RationalTime other
             * self contains other
             */
            bool overlaps(RationalTime other) const {
                return contains(other);
            }

            /**overlaps(other)
             * params: TimeRange other
             * The start of self strictly precedes end of other.
             * The end of self strictly antecedes start of other.
             * The converse would be other.overlaps(self)
             */
            bool overlaps(TimeRange other, double epsilon = defaultEpsilon) const {
                double selfStart = _start_time.value() / _start_time.rate();
                double selfEnd = end_time_exclusive().value() / end_time_exclusive().rate();
                double otherStart = other._start_time.value() / other._start_time.rate();
                double otherEnd = other.end_time_exclusive().value() / other.end_time_exclusive().rate();
//                return (otherEnd - selfEnd >= epsilon) &&
//                       (otherStart - selfStart >= epsilon) &&
//                        (selfEnd - otherStart >= epsilon);
//                return _start_time < other.end_time_exclusive() && other._start_time < end_time_exclusive();
                return (otherEnd - selfStart >= epsilon) &&
                       (selfEnd - otherStart >= epsilon);
            }

            /**before(other)
             * params: TimeRange other
             * The end of self strictly precedes the start of other.
             * The converse would be other.before(self)
             */
            bool before(TimeRange other, double epsilon = defaultEpsilon) const {
                return (other._start_time.value() / other._start_time.rate() -
                        end_time_exclusive().value() / end_time_exclusive().rate()) >= epsilon;
//                return _start_time < other._start_time && end_time_exclusive() <= other._start_time;
            }

            /**before(other)
             * params: RationalTime other
             * The end of self strictly precedes other.
             */
            bool before(RationalTime other, double epsilon = defaultEpsilon) const {
//                return end_time_exclusive() < other;
                return other.value() / other.rate() - end_time_exclusive().value() / end_time_exclusive().rate() >=
                       epsilon;
            }

            /**meets(other)
             * params: TimeRange other
             * The end of self strictly equals the start of other or
             * the start of self strictly equals the end of other.
             * The converse would be other.meets(self)
             */
            bool meets(TimeRange other, double epsilon) const {
                return other._start_time.value() / other._start_time.rate() -
                       end_time_exclusive().value() / end_time_exclusive().rate() <= epsilon;
//                return end_time_exclusive() == other._start_time || _start_time == other.end_time_exclusive();
            }

            /**begins(other)
             * params: TimeRange other
             * The start of self strictly equals the start of other.
             * The end of self strictly precedes the end of other.
             * The converse would be other.begins(self)
             */
            bool begins(TimeRange other, double epsilon = defaultEpsilon) const {
                double selfStart = _start_time.value() / _start_time.rate();
                double selfEnd = end_time_exclusive().value() / end_time_exclusive().rate();
                double otherStart = other._start_time.value() / other._start_time.rate();
                double otherEnd = other.end_time_exclusive().value() / other.end_time_exclusive().rate();
                return fabs(otherStart - selfStart) <= epsilon && otherEnd - selfEnd >= epsilon;
//                return _start_time == other._start_time && end_time_exclusive() < other.end_time_exclusive();
            }

            /**begins(other)
             * params: RationalTime other
             * The start of self strictly equals other.
             */
            bool begins(RationalTime other, double epsilon = defaultEpsilon) const {
                double selfStart = _start_time.value() / _start_time.rate();
                double otherStart = other.value() / other.rate();
                return fabs(otherStart - selfStart) <= epsilon;
            }

            /**finishes(other)
             * params: TimeRange other
             * The start of self strictly antecedes the start of other.
             * The end of self strictly equals the end of other.
             * The converse would be other.finishes(self)
             */
            bool finishes(TimeRange other, double epsilon = defaultEpsilon) const {
                double selfStart = _start_time.value() / _start_time.rate();
                double selfEnd = end_time_exclusive().value() / end_time_exclusive().rate();
                double otherStart = other._start_time.value() / other._start_time.rate();
                double otherEnd = other.end_time_exclusive().value() / other.end_time_exclusive().rate();
//                return end_time_exclusive() == other.end_time_exclusive() && _start_time > other._start_time;
                return fabs(selfEnd - otherEnd) <= epsilon && selfStart - otherStart >= epsilon;
            }

            /**finishes(other)
             * params: RationalTime other
             * The end of self strictly equals other.
             */
            bool finishes(RationalTime other, double epsilon = defaultEpsilon) const {
                double selfEnd = end_time_exclusive().value() / end_time_exclusive().rate();
                double otherEnd = other.value() / other.rate();
//                return end_time_exclusive() == other;
                return fabs(selfEnd - otherEnd) <= epsilon;
            }


            /**operator equals()
             * params: TimeRange lhs
             *         TimeRange rhs
             * The start of lhs strictly equals the start of rhs.
             * The end of lhs strictly equals the end of rhs.
             */
            friend bool operator==(TimeRange lhs, TimeRange rhs) {
//                return lhs._start_time == rhs._start_time && lhs._duration == rhs._duration;
//                return RationalTime::absTime(lhs._start_time - rhs._start_time) < defaultEpsilon &&
//                       RationalTime::absTime(lhs._duration - rhs._duration) < defaultEpsilon;
                RationalTime start = RationalTime::absTime(lhs._start_time - rhs._start_time);
                RationalTime duration = RationalTime::absTime(lhs._duration - rhs._duration);
                return start.value() / start.rate() < defaultEpsilon &&
                       duration.value() / duration.rate() < defaultEpsilon;
            }

            /**operator notequals()
             * params: TimeRange lhs
             *         TimeRange rhs
             * Converse of equals() operator
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
            static constexpr double defaultEpsilon = 1.0 / 1001.0;
            friend class TimeTransform;
        };

    }
}
