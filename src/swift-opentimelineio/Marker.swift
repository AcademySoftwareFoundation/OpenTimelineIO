//
//  Marker.swift
//

import Foundation

public class Marker : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_marker())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
