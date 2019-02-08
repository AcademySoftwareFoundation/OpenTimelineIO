//
//  ExternalReference.swift
//

import Foundation

public class ExternalReference : MediaReference {
    override public init() {
        super.init(new_external_reference())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
