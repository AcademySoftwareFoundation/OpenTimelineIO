//
//  SerializableCollection.swift
//

import Foundation

public class SerializableCollection : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_serializable_collection())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
