//
//  SerializableCollection.swift
//

import Foundation

public class SerializableCollection : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_serializable_collection())
    }
    
    public convenience init<ST : Sequence, CT : Sequence>(name: String? = nil,
                                           children: CT? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element, CT.Element == SerializableObject {
        self.init()
        metadataInit(name, metadata)
        if let children = children {
            self.children.set(contents: children)
        }
    }
    
    public convenience init(name: String? = nil) {
        self.init(name: name, metadata: Metadata.Dictionary.none)
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
    
    lazy var _childrenProperty = { create_serializable_collection_children_vector_property(self) }()

    public var children: SerializableObject.Vector<SerializableObject> {
        get {
            return SerializableObject.Vector<SerializableObject>(_childrenProperty)
        }
        set {
            _childrenProperty.copyContents(newValue.cxxVectorProperty)
        }
    }
}
