//
//  TimeEffect.swift
//

import Foundation

public class TimeEffect : Effect {
    override public init() {
        super.init(new_time_effect())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
