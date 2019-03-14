//
//  GeneratorReference.swift
//

import Foundation

public class GeneratorReference : MediaReference {
    override public init() {
        super.init(otio_new_generator_reference())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
