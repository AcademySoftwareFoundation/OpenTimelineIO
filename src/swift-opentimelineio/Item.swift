//
//  Item.swift
//

import Foundation

public class Item : Composable {
    override public init() {
        super.init(new_item())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
