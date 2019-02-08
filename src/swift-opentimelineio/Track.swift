//
//  Stack.swift
//

import Foundation

public class Track : Composition {
    override public init() {
        super.init(new_track())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
