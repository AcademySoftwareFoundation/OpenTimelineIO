//
//  ExternalReference.swift
//

import Foundation

public class ExternalReference : MediaReference {
    override public init() {
        super.init(otio_new_external_reference())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
