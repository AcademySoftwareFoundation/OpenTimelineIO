//
//  LinearTimeWarp.swift
//

import Foundation

public class LinearTimeWarp : TimeEffect {
    override public init() {
        super.init(otio_new_linear_time_warp())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           effectName: String? = nil,
                                           timeScalar: Double = 1,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let effectName = effectName {
            self.effectName = effectName
        }
        self.timeScalar = timeScalar
    }
    
    public convenience init(name: String? = nil, effectName: String? = nil,timeScalar: Double = 1) {
        self.init(name: name, effectName: effectName, timeScalar: timeScalar, metadata: Metadata.Dictionary.none)
    }
    
    public var timeScalar: Double {
        get { return linear_time_warp_get_time_scalar(self) }
        set { linear_time_warp_set_time_scalar(self, newValue) }
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
