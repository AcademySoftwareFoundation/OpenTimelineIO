//
//  GeneratorReference.swift
//

import Foundation

public class GeneratorReference : MediaReference {
    override public init() {
        super.init(new_generator_reference())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
