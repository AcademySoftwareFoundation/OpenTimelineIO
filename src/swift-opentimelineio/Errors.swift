//
//  Errors.swift
//  libotio_macos
//
//  Created by David Baraff on 1/4/19.
//

import Foundation

public struct OpentimeError : Error, CustomStringConvertible {
    // must match opentime/errorStatus.h
    public enum Status: Int {
        case invalidTimecodeRate = 1
        case nonDropframeRate
        case invalidTimecodeString
        case invalidTimeString
        case timecodeRateMismatch
        case negativeValue
    }
    
    public let status: Status
    public let description: String
    
    static func returnOrThrow<T>(work: (inout CxxErrorStruct) -> T) throws -> T {
        var cxxErr = CxxErrorStruct()
        let value = work(&cxxErr)
        
        if cxxErr.statusCode == 0 {
            return value
        }
        
        guard let status = Status(rawValue: Int(cxxErr.statusCode)) else {
            fatalError("botched construction building OpenTimeError: code: \(cxxErr.statusCode)")
        }
        
        let um = Unmanaged<NSString>.fromOpaque(cxxErr.details)
        throw OpentimeError(status: status, description: um.takeRetainedValue() as String)
    }
}

public struct OTIOError : Error, CustomStringConvertible {
    // must match opentimelineio/errorStatus.h
    
    public enum Status: Int {
        case notImplemented = 1
        case unresolvedObjectReference
        case duplicateObjectReference
        case malformedSchema
        case jsonParseError
        case childAlreadyParented
        case fileOpenFailed
        case fileWriteFailed
        case schemaAlreadyRegistered
        case schemaNotRegistered
        case schemaVersionUnsupported
        case keyNotFound
        case illegalIndex
        case typeMismatch
        case internalError
        case notAnItem
        case notAChildOf
        case notAChild
        case notDescendedFrom
        case cannotComputeAvailableRange
        case invalidTimeRange
        case objectWithoutDuration
        case cannotTrimTransition
    }
    
    public let status: Status
    public let description: String
    
    static func returnOrThrow<T>(work: (inout CxxErrorStruct) -> T) throws -> T {
        var cxxErr = CxxErrorStruct()
        let value = work(&cxxErr)
        
        if cxxErr.statusCode == 0 {
            return value
        }
        
        guard let status = Status(rawValue: Int(cxxErr.statusCode)) else {
            fatalError("botched construction building OpenTimeError: code: \(cxxErr.statusCode)")
        }

        let um = Unmanaged<NSString>.fromOpaque(cxxErr.details)
        throw OTIOError(status: status, description: um.takeRetainedValue() as String)
    }
}
