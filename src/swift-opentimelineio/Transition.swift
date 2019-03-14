//
//  Transition.swift
//

import Foundation

public class Transition : Composable {
    override public init() {
        super.init(otio_new_transition())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
