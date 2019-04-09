//
//  Stack.swift
//

import Foundation

public class Track : Composition {
    override public init() {
        super.init(otio_new_track())
    }

    public enum Kind : String {
        case video = "Video"
        case audion = "Audio"
    }
    
    public enum NeighborGapPolicy: Int {
        case never = 0
        case aroundTransitions = 1
    }

    public convenience init<ST : Sequence>(name: String? = nil,
                                           sourceRange: TimeRange? = nil,
                                           kind: Kind = .video,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        self.sourceRange = sourceRange
        self.kind = kind.rawValue
    }
    
    public convenience init(name: String? = nil, sourceRange: TimeRange? = nil, kind: Kind = .video) {
        self.init(name: name, sourceRange: sourceRange, kind: kind, metadata: Metadata.Dictionary.none)
    }

    public var kind: String {
        get { return track_get_kind(self) }
        set { track_set_kind(self, newValue) }
    }
    
    public func neighbors(of composable: Composable, insertGap: NeighborGapPolicy = .never) throws -> (Composable?, Composable?) {
        var cxxPtr1: UnsafeMutableRawPointer?
        var cxxPtr2: UnsafeMutableRawPointer?
        try OTIOError.returnOrThrow { track_neighbors_of(self, composable, Int32(insertGap.rawValue), &cxxPtr1, &cxxPtr2, &$0) }
        return (SerializableObject.possiblyFindOrCreate(cxxPtr: cxxPtr1) as? Composable,
                SerializableObject.possiblyFindOrCreate(cxxPtr: cxxPtr2) as? Composable)
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
