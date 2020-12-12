//
//  SerializableObjectWithMetadata.swift
//  otio_macos
//
//  Created by David Baraff on 1/24/19.
//

import Foundation

public class SerializableObjectWithMetadata : SerializableObject {
    override public init() {
        super.init(otio_new_serializable_object_with_metadata())
    }

    public convenience init<ST : Sequence>(name: String? = nil, metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
    }

    public convenience init(name: String? = nil) {
        self.init(name: name, metadata: Metadata.Dictionary.none)
    }

    internal func metadataInit<ST : Sequence>(_ name: String? = nil, _ metadata: ST?) where ST.Element == Metadata.Dictionary.Element {
        if let name = name {
            self.name = name
        }
        if metadata != nil {
            if let metadata = metadata as? Metadata.Dictionary {
                self.metadata.set(contents: metadata)
            }
            else if let metadata = metadata {
                self.metadata.set(contents: metadata)
            }
        }
    }
    
    override public var description: String {
        let addr = ObjectIdentifier(self).hashValue
        let addr2 = Int(bitPattern: cxxSerializableObject())
        return "\(String(describing: type(of: self))) named '\(name)' <swift: 0x\(String(format: "%x", addr)), C++: \(String(format: "%p", addr2))>"
    }
    
    public var name: String {
        get { return serializable_object_with_metadata_name(self) }
        set { serializable_object_with_metadata_set_name(self, newValue) }
    }
    
    public var metadata: Metadata.Dictionary {
        get { return Metadata.Dictionary.wrap(anyDictionaryPtr: serializable_object_with_metadata_metadata(self), cxxRetainer: self) }
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
