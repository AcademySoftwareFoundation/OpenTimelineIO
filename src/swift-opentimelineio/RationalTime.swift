//
//  RationalTime.swift
//
//  Created by David Baraff on 1/03/19.
//

// import Foundation

public struct RationalTime: CustomStringConvertible, Equatable {
    public var value: Double { return cxxRationalTime.value }
    public var rate: Double { return cxxRationalTime.rate }
    
    public var description: String {
        return "RationalTime(\(value), \(rate))"
    }
    
    public init(value: Double = 0, rate: Double = 1) {
        cxxRationalTime = CxxRationalTime(value: value, rate: rate)
    }
    
    public func isInvalidTime() -> Bool {
        return rate <= 0
    }
    
    public func rescaled(to newRate: Double) -> RationalTime {
        return withUnsafePointer(to: self.cxxRationalTime) {
            RationalTime(rational_time_rescaled_to($0, newRate));
        }
    }

    public func rescaled(to rt: RationalTime) -> RationalTime {
        return withUnsafePointer(to: self.cxxRationalTime) {
            RationalTime(rational_time_rescaled_to($0, rt.rate));
        }
    }

    public func valueRescaled(to newRate: Double) -> Double {
        return withUnsafePointer(to: cxxRationalTime) {
            rational_time_value_rescaled_to($0, newRate)
        }
    }

    public func valueRescaled(to rt: RationalTime) -> Double {
        return withUnsafePointer(to: cxxRationalTime) {
            rational_time_value_rescaled_to($0, rt.rate)
        }
    }

    public func almostEqual(_ other: RationalTime, delta: Double = 0) -> Bool {
        return rational_time_almost_equal(self.cxxRationalTime, other.cxxRationalTime, delta)
    }

    static public func durationFrom(startTime: RationalTime, endTime: RationalTime) -> RationalTime {
        return RationalTime(rational_time_duration_from_start_end_time(startTime.cxxRationalTime,
                                                                       endTime.cxxRationalTime))
    }
    
    static public func isValidTimecodeRate(_ inRate: Double) -> Bool {
        return rational_time_is_valid_timecode_rate(inRate)
    }
    
    static public func from(frame: Double, rate inRate: Double) -> RationalTime {
        return RationalTime(value: floor(frame), rate: inRate)
    }

    static public func from(frame: Int, rate inRate: Double) -> RationalTime {
        return RationalTime(value: Double(frame), rate: inRate)
    }

    static public func from(seconds: Double) -> RationalTime {
        return RationalTime(value: seconds, rate: 1)
    }
    
    static public func from(timecode: String, rate inRate: Double) throws -> RationalTime {
        return try OpentimeError.returnOrThrow { RationalTime(rational_time_from_timecode(timecode, inRate, &$0)) }
    }
    
    static public func from(timestring: String, rate inRate: Double) throws -> RationalTime {
        return try OpentimeError.returnOrThrow { RationalTime(rational_time_from_timestring(timestring, inRate, &$0)) }
    }
    
    public func toFrames() -> Int {
        return Int(value)
    }
    
    public func toFrames(rate inRate: Double) -> Int {
        return Int(valueRescaled(to: inRate))
    }
    
    public func toSeconds() -> Double {
        return valueRescaled(to: 1)
    }
    
    public func toTimecode(rate inRate: Double) throws -> String {
        return try OpentimeError.returnOrThrow { rational_time_to_timecode(cxxRationalTime, inRate, &$0) }
    }

    public func toTimecode() throws -> String {
        return try OpentimeError.returnOrThrow { rational_time_to_timecode(cxxRationalTime, rate, &$0) }
    }

    public func toTimestring() -> String {
        return rational_time_to_timestring(cxxRationalTime);
    }

    static public func += (lhs: inout RationalTime, rhs: RationalTime) {
        lhs = lhs + rhs
    }

    static public func -= (lhs: inout RationalTime, rhs: RationalTime) {
        lhs = lhs - rhs
    }

    static public prefix func - (lhs: RationalTime) -> RationalTime {
        return RationalTime(value: -lhs.value, rate: -lhs.rate)
    }
    
    static public func + (lhs: RationalTime, rhs: RationalTime) -> RationalTime {
        return RationalTime(rational_time_add(lhs.cxxRationalTime, rhs.cxxRationalTime))
    }

    static public func - (lhs: RationalTime, rhs: RationalTime) -> RationalTime {
        return RationalTime(rational_time_subtract(lhs.cxxRationalTime, rhs.cxxRationalTime))
    }

    static public func > (lhs: RationalTime, rhs: RationalTime) -> Bool {
        return (lhs.value / lhs.rate) > (rhs.value / rhs.rate)
    }

    static public func >= (lhs: RationalTime, rhs: RationalTime) -> Bool {
        return (lhs.value / lhs.rate) >= (rhs.value / rhs.rate)
    }

    static public func < (lhs: RationalTime, rhs: RationalTime) -> Bool {
        return !(lhs >= rhs)
    }

    static public func <= (lhs: RationalTime, rhs: RationalTime) -> Bool {
        return !(lhs > rhs)
    }

    static public func == (lhs: RationalTime, rhs: RationalTime) -> Bool {
        return lhs.valueRescaled(to: rhs.rate) == rhs.value
    }

    static public func != (lhs: RationalTime, rhs: RationalTime) -> Bool {
        return !(lhs == rhs)
    }

    internal init(_ cxxRationalTime: CxxRationalTime) {
        self.cxxRationalTime = cxxRationalTime
    }
    
    internal let cxxRationalTime: CxxRationalTime
}

