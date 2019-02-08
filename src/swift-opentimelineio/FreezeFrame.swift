//
//  FreezeFrame.swift
//

import Foundation

public class FreezeFrame : LinearTimeWarp {
    override public init() {
        super.init(new_freeze_frame())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
