//
//  MediaReference.swift
//

import Foundation

public class MediaReference : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_media_reference())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
