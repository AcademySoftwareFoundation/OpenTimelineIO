//
//  Clip.swift
//  otio_macos
//
//  Created by David Baraff on 1/25/19.
//

import Foundation

public class Clip : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_clip())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
