//
//  Transition.swift
//

import Foundation

public class Transition : Composable {
    override public init() {
        super.init(otio_new_transition())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           transitionType: String? = nil,
                                           inOffset: RationalTime? = nil,
                                           outOffset: RationalTime? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        
        if let transitionType = transitionType {
            self.transitionType = transitionType
        }
        if let inOffset = inOffset {
            self.inOffset = inOffset
        }
        if let outOffset = outOffset {
            self.outOffset = outOffset
        }
    }
    
    public convenience init(name: String? = nil,
                            transitionType: String? = nil,
                            inOffset: RationalTime? = nil,
                            outOffset: RationalTime? = nil) {
        self.init(name: name, transitionType: transitionType, inOffset: inOffset,
                  outOffset: outOffset, metadata: Metadata.Dictionary.none)
    }

    public var transitionType: String {
        get { return transition_get_transition_type(self) }
        set { transition_set_transition_type(self, newValue) }
    }

    public var inOffset: RationalTime {
        get { return RationalTime(transition_get_in_offset(self)) }
        set { transition_set_in_offset(self, newValue.cxxRationalTime) }
    }

    public var outOffset: RationalTime {
        get { return RationalTime(transition_get_out_offset(self)) }
        set { transition_set_out_offset(self, newValue.cxxRationalTime) }
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
