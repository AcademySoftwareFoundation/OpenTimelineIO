//
//  TimeEffect.swift
//

import Foundation

public class TimeEffect : Effect {
    override public init() {
        super.init(otio_new_time_effect())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
