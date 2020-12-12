//
//  Stack.swift
//

import Foundation

public class Stack : Composition {
    override public init() {
        super.init(otio_new_stack())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           sourceRange: TimeRange? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        self.sourceRange = sourceRange
    }
    
    public convenience init(name: String? = nil, sourceRange: TimeRange? = nil) {
        self.init(name: name, sourceRange: sourceRange, metadata: Metadata.Dictionary.none)
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
