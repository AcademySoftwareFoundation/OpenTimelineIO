//
//  Errors.swift
//  libotio_macos
//
//  Created by David Baraff on 1/4/19.
//

import Foundation

public struct OpentimeError : Error, CustomStringConvertible {
    public let result: OpentimeResult
    public let description: String
}

struct OpentimeErrorThrower {
    var resultCode: Int = 0
    var details: NSString?
    
    mutating func returnOrThrow<T>(_ value: T) throws -> T {
        guard Int(resultCode) != OpentimeResult.OK.rawValue else {
            return value
        }
        
        guard let result = OpentimeResult(rawValue: Int(resultCode)),
            let description = details else {
                fatalError("botched construction building OpenTimeError: code: \(resultCode), details: \(String(describing: details))")
        }
        throw OpentimeError(result: result, description: description as String)
    }
}
