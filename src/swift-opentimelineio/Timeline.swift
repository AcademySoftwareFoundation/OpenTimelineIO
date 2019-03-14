//
//  Timeline.swift
//

import Foundation

public class Timeline : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_timeline())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
