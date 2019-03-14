//
//  Composition.swift
//

import Foundation

public class Composition : Item {
    override public init() {
        super.init(otio_new_composition())
    }

    public convenience init<ST : Sequence>(name: String? = nil,
                                           timeRange: TimeRange? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
    }

    public convenience init(name: String? = nil, timeRange: TimeRange? = nil) {
        self.init(name: name, timeRange: timeRange, metadata: Metadata.Dictionary.none)
    }
    
    lazy var _childrenProperty = { create_composition_children_vector_property(self) }()
    
    public var children: SerializableObject.ImmutableVector<Composable> {
        get {
            return SerializableObject.ImmutableVector<Composable>(_childrenProperty)
        }
    }

    public func removeAllChildren() {
        
    }

    public func set<ST : Sequence>(children: ST) throws where ST.Element == Composable {
    
    }

    public func replace(index: Int, withChild: Composable) throws {
        
    }

    public func insert(index: Int, child: Composable) throws {
        
    }

    public func remove(index: Int) throws {
        
    }

    public func append(child: Composable) throws {
        
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
