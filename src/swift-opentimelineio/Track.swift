//
//  Stack.swift
//

import Foundation

public class Track : Composition {
    override public init() {
        super.init(otio_new_track())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
