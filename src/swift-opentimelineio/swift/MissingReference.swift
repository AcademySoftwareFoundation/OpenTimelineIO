//
//  MissingReference.swift
//

import Foundation
import objc_opentimelineio

public class MissingReference : MediaReference {
    override public init() {
        super.init(otio_new_missing_reference())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
