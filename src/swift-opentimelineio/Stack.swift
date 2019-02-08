//
//  Stack.swift
//

import Foundation

public class Stack : Composition {
    override public init() {
        super.init(new_stack())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
