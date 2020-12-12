//
//  Effect.swift
//

import Foundation

public class Effect : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_effect())
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
    
    public var effectName: String {
        get { return effect_get_name(self) }
        set { effect_set_name(self, newValue) }
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
