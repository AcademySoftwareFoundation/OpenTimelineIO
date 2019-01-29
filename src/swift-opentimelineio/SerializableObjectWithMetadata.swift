//
//  SerializableObjectWithMetadata.swift
//  otio_macos
//
//  Created by David Baraff on 1/24/19.
//

import Foundation

public class SerializableObjectWithMetadata : SerializableObject {
    override public init() {
        super.init(new_serializable_object_with_metadata())
    }
    
    public var name: String {
        get { return serializable_object_with_metadata_name(cxxRetainer) }
        set { serializable_object_with_metadata_set_name(cxxRetainer, newValue) }
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
