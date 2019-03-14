//
//  Gap.swift
//

import Foundation

public class Gap : Item {
    override public init() {
        super.init(otio_new_gap())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
