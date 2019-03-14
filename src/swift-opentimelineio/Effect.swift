//
//  Effect.swift
//

import Foundation

public class Effect : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_effect())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
