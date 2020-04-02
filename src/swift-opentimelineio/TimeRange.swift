//
//  TimeRange.swift
//
//  Created by David Baraff on 1/15/19.
//

public struct TimeRange: CustomStringConvertible, Equatable {
    public var startTime: RationalTime { return RationalTime(cxxTimeRange.start_time) }
    public var duration: RationalTime { return RationalTime(cxxTimeRange.duration) }
    
    public var description: String {
        return "TimeRange(\(startTime), \(duration))"
    }
    
    public init() {
         cxxTimeRange = CxxTimeRange(start_time: RationalTime().cxxRationalTime, duration: RationalTime().cxxRationalTime)
    }
    
    public init(startTime t0: RationalTime) {
        cxxTimeRange = CxxTimeRange(start_time: t0.cxxRationalTime, duration: RationalTime(value: 0, rate: t0.rate).cxxRationalTime)
    }
    
    public init(startTime t0: RationalTime, duration d: RationalTime) {
        cxxTimeRange = CxxTimeRange(start_time: t0.cxxRationalTime, duration: d.cxxRationalTime)
    }
    
    public func endTimeInclusive() -> RationalTime {
        return withUnsafePointer(to: self.cxxTimeRange) {
            RationalTime(time_range_end_time_inclusive($0))
        }
    }
    
    public func endTimeExclusive() -> RationalTime {
        return withUnsafePointer(to: self.cxxTimeRange) {
            RationalTime(time_range_end_time_exclusive($0))
        }
    }
    
    public func durationExtended(by other: RationalTime) -> TimeRange {
        return withUnsafePointer(to: self.cxxTimeRange) {
            TimeRange(time_range_duration_extended_by($0, other.cxxRationalTime))
        }
    }
    
    public func extended(by other: TimeRange) -> TimeRange {
        return withUnsafePointer(to: self.cxxTimeRange) { pSelf in
            withUnsafePointer(to: other.cxxTimeRange) { pOther in
                TimeRange(time_range_extended_by(pSelf, pOther))
            }
        }
    }

    public func clamped(_ other: RationalTime) -> RationalTime {
        return withUnsafePointer(to: self.cxxTimeRange) {
            RationalTime(time_range_clamped_time($0, other.cxxRationalTime))
        }
    }

    public func clamped(_ other: TimeRange) -> TimeRange {
        return withUnsafePointer(to: self.cxxTimeRange) { pSelf in
            withUnsafePointer(to: other.cxxTimeRange) { pOther in
                TimeRange(time_range_clamped_range(pSelf, pOther))
            }
        }
    }

    public func contains(_ other: RationalTime) -> Bool {
        return withUnsafePointer(to: self.cxxTimeRange) {
            time_range_contains_time($0, other.cxxRationalTime)
        }
    }

    public func contains(_ other: TimeRange) -> Bool {
        return withUnsafePointer(to: self.cxxTimeRange) { pSelf in
            withUnsafePointer(to: other.cxxTimeRange) { pOther in
                time_range_contains_range(pSelf, pOther)
            }
        }
    }

    public func overlaps(_ other: RationalTime) -> Bool {
        return withUnsafePointer(to: self.cxxTimeRange) {
            time_range_overlaps_time($0, other.cxxRationalTime)
        }
    }

    public func overlaps(_ other: TimeRange) -> Bool {
        return withUnsafePointer(to: self.cxxTimeRange) { pSelf in
            withUnsafePointer(to: other.cxxTimeRange) { pOther in
                time_range_overlaps_range(pSelf, pOther)
            }
        }
    }

    static public func == (_ lhs: TimeRange, _ rhs: TimeRange) -> Bool {
        return withUnsafePointer(to: lhs.cxxTimeRange) { pLhs in
            withUnsafePointer(to: rhs.cxxTimeRange) { pRhs in
                time_range_equals(pLhs, pRhs)
            }
        }
    }
    
    static public func != (_ lhs: TimeRange, _ rhs: TimeRange) -> Bool {
        return !(lhs == rhs)
    }
    
    static public func rangeFrom(startTime: RationalTime, endTimeExclusive: RationalTime) -> TimeRange {
        return TimeRange(time_range_range_from_start_end_time(startTime.cxxRationalTime, endTimeExclusive.cxxRationalTime))
    }
    
    internal init(_ cxxTimeRange: CxxTimeRange) {
        self.cxxTimeRange = cxxTimeRange
    }
    
    let cxxTimeRange: CxxTimeRange
}
