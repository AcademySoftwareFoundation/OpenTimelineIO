//
//  Composable.swift
//

import Foundation

public class Composable : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_composable())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil, metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
    }

    public convenience init(name: String? = nil) {
        self.init(name: name, metadata: Metadata.Dictionary.none)
    }

    public var parent: SerializableObjectWithMetadata? {
        return SerializableObject.possiblyFindOrCreate(cxxPtr: composable_parent(self)) as? SerializableObjectWithMetadata
    }

    public var visible: Bool {
        return composable_visible(self)
    }

    public var overlapping: Bool {
        return composable_overlapping(self)
    }

    public func duration() throws -> RationalTime {
        return try OTIOError.returnOrThrow { RationalTime(composable_duration(self, &$0)) }
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
