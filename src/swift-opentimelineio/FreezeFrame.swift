//
//  FreezeFrame.swift
//

import Foundation

public class FreezeFrame : LinearTimeWarp {
    override public init() {
        super.init(otio_new_freeze_frame())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
