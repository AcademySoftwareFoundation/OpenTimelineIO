//
//  Timeline.swift
//

import Foundation

public class Timeline : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_timeline())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
