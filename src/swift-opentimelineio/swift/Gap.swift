//
//  Gap.swift
//

import Foundation

public class Gap : Item {
    override public init() {
        super.init(otio_new_gap())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           sourceRange: TimeRange? = nil,
                                           effects: [Effect]? = nil,
                                           markers: [Marker]? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let sourceRange = sourceRange {
            self.sourceRange = sourceRange
        }
        if let markers = markers {
            self.markers.set(contents: markers)
        }
        if let effects = effects {
            self.effects.set(contents: effects)
        }
    }
    
    public convenience init(name: String? = nil,
                            sourceRange: TimeRange? = nil,
                            effects: [Effect]? = nil,
                            markers: [Marker]? = nil) {
        self.init(name: name, sourceRange: sourceRange, effects: effects, markers: markers,
                  metadata: Metadata.Dictionary.none)
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
