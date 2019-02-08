//
//  MissingReference.swift
//

import Foundation

public class MissingReference : MediaReference {
    override public init() {
        super.init(new_missing_reference())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
