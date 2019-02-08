//
//  Gap.swift
//

import Foundation

public class Gap : Item {
    override public init() {
        super.init(new_gap())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
