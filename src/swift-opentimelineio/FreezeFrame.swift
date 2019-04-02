//
//  FreezeFrame.swift
//

import Foundation

public class FreezeFrame : LinearTimeWarp {
    override public init() {
        super.init(otio_new_freeze_frame())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
    }
    
    public convenience init(name: String? = nil, effectName: String? = nil) {
        self.init(name: name, metadata: Metadata.Dictionary.none)
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
