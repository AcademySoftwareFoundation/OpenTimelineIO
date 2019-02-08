//
//  Composition.swift
//

import Foundation

public class Composition : Item {
    override public init() {
        super.init(new_composition())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
