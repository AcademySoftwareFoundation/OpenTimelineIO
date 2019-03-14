//
//  LinearTimeWarp.swift
//

import Foundation

public class LinearTimeWarp : TimeEffect {
    override public init() {
        super.init(otio_new_linear_time_warp())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
