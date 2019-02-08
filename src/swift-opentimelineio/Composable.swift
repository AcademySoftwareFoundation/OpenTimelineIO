//
//  Composable.swift
//

import Foundation

public class Composable : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_composable())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
