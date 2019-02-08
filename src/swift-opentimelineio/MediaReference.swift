//
//  MediaReference.swift
//

import Foundation

public class MediaReference : SerializableObjectWithMetadata {
    override public init() {
        super.init(new_media_reference())
    }
    
    override internal init(_ cxxRetainer: CxxRetainer) {
        super.init(cxxRetainer)
    }
}
