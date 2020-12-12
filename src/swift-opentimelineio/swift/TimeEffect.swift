//
//  TimeEffect.swift
//

import Foundation

public class TimeEffect : Effect {
    override public init() {
        super.init(otio_new_time_effect())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           effectName: String? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let effectName = effectName {
            self.effectName = effectName
        }
    }
    
    public convenience init(name: String? = nil, effectName: String? = nil) {
        self.init(name: name, effectName: effectName, metadata: Metadata.Dictionary.none)
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
