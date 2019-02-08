//
//  Effect.swift
//

import Foundation

public class Effect : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_effect())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
