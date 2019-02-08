//
//  LinearTimeWarp.swift
//

import Foundation

public class LinearTimeWarp : TimeEffect {
    override public init() {
        super.init(new_linear_time_warp())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
