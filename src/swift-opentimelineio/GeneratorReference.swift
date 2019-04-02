//
//  GeneratorReference.swift
//

import Foundation

public class GeneratorReference : MediaReference {
    override public init() {
        super.init(otio_new_generator_reference())
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           generatorKind: String? = nil,
                                           availableRange: TimeRange? = nil,
                                           parameters: ST? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let generatorKind = generatorKind {
            self.generatorKind = generatorKind
        }
        
        if let availableRange = availableRange {
            self.availableRange = availableRange
        }

        if parameters != nil {
            if let parameters = parameters as? Metadata.Dictionary {
                self.parameters.set(contents: parameters)
            }
            else if let parameters = parameters {
                self.parameters.set(contents: parameters)
            }
        }
        
    }
    
    public convenience init(name: String? = nil,
                            generatorKind: String? = nil,
                            availableRange: TimeRange? = nil) {
        self.init(name: name, generatorKind: generatorKind, availableRange: availableRange,
                  parameters: Metadata.Dictionary.none,
                  metadata: Metadata.Dictionary.none)
    }

    public var generatorKind: String {
        get { return generator_reference_get_generator_kind(self) }
        set { generator_reference_set_generator_kind(self, newValue) }
    }
    
    public var parameters: Metadata.Dictionary {
        get { return Metadata.Dictionary.wrap(anyDictionaryPtr: generator_reference_parameters(self), cxxRetainer: self) }
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
