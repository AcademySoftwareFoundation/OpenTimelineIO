//
//  Transition.swift
//

import Foundation

public class Transition : Composable {
    override public init() {
        super.init(new_transition())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
