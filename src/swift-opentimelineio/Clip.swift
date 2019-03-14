//
//  Clip.swift
//  otio_macos
//
//  Created by David Baraff on 1/25/19.
//

import Foundation

public class Clip : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_clip())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
