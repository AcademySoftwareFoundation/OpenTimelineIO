//
//  TimeTransform.swift
//
//  Created by David Baraff on 1/17/19.
//

public struct TimeTransform : Equatable, CustomStringConvertible {
    public var offset: RationalTime {
        return RationalTime(cxxTimeTransform.offset)
    }
    
    public var scale: Double {
        return cxxTimeTransform.scale
    }

    public var rate: Double {
        return cxxTimeTransform.rate
    }

    public init(offset: RationalTime = RationalTime(), scale: Double = 1, rate: Double = -1) {
        cxxTimeTransform = CxxTimeTransform(offset: offset.cxxRationalTime, scale: scale, rate: rate)
    }
    
    public var description: String {
        return "TimeTransform(\(RationalTime(cxxTimeTransform.offset)), \(cxxTimeTransform.scale), \(cxxTimeTransform.rate))"
    }

    public func applied(to other: TimeRange) -> TimeRange {
        return withUnsafePointer(to: cxxTimeTransform) { pSelf in
            withUnsafePointer(to: other.cxxTimeRange) { pOther in
                TimeRange(time_transform_applied_to_timerange(pSelf, pOther))
            }
        }
    }

    public func applied(to other: TimeTransform) -> TimeTransform {
        return withUnsafePointer(to: cxxTimeTransform) { pSelf in
            withUnsafePointer(to: other.cxxTimeTransform) { pOther in
                TimeTransform(time_transform_applied_to_timetransform(pSelf, pOther))
            }
        }
    }

    public func applied(to other: RationalTime) -> RationalTime {
        return withUnsafePointer(to: cxxTimeTransform) {
            RationalTime(time_transform_applied_to_time($0, other.cxxRationalTime))
        }
    }
    
    static public func == (lhs: TimeTransform, rhs: TimeTransform) -> Bool {
        return withUnsafePointer(to: lhs.cxxTimeTransform) { pLhs in
            withUnsafePointer(to: rhs.cxxTimeTransform) { pRhs in
                time_transform_equals(pLhs, pRhs)
            }
        }
    }

    static public func != (lhs: TimeTransform, rhs: TimeTransform) -> Bool {
        return !(lhs == rhs)
    }
    
    internal init(_ cxxTimeTransform: CxxTimeTransform) {
        self.cxxTimeTransform = cxxTimeTransform
    }

    let cxxTimeTransform: CxxTimeTransform
}
