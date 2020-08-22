//
//  Clip.swift
//  otio_macos
//
//  Created by David Baraff on 1/25/19.
//

import Foundation

public class Clip : Item {
    override public init() {
        super.init(otio_new_clip())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           mediaReference: MediaReference? = nil,
                                           sourceRange: TimeRange? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let sourceRange = sourceRange {
            self.sourceRange = sourceRange
        }
        self.mediaReference = mediaReference
    }
    
    public convenience init(name: String? = nil,
                            mediaReference: MediaReference? = nil,
                            sourceRange: TimeRange? = nil) {
        self.init(name: name, mediaReference: mediaReference, sourceRange: sourceRange,
                  metadata: Metadata.Dictionary.none)
    }

    public var mediaReference: MediaReference? {
        get { return SerializableObject.possiblyFindOrCreate(cxxPtr: clip_media_reference(self)) as? MediaReference }
        set { if let mediaReference = newValue {
                clip_set_media_reference(self, mediaReference)
            }
            else {
                clip_set_media_reference(self, nil)
            }
        }
    }
}
