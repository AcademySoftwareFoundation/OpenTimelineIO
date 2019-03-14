//
//  Stack.swift
//

import Foundation

public class Stack : Composition {
    override public init() {
        super.init(otio_new_stack())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
