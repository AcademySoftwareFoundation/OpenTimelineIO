//
//  ExternalReference.swift
//

import Foundation

public class ExternalReference : MediaReference {
    override public init() {
        super.init(otio_new_external_reference())
    }
    
    public convenience init<ST : Sequence>(targetURL: URL? = nil,
                                           availableRange: TimeRange? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let targetURL = targetURL {
            self.targetURL = targetURL
        }
    }
    
    public convenience init(targetURL: URL? = nil,
                            availableRange: TimeRange? = nil) {
        self.init(targetURL: targetURL, availableRange: availableRange,
                  metadata: Metadata.Dictionary.none)
    }
    
    public var targetURL: URL {
        get { return URL(fileURLWithPath: external_reference_get_target_url(self)) }
        set { external_reference_set_target_url(self, newValue.path) }
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
