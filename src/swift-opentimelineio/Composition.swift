//
//  Composition.swift
//

import Foundation

public class Composition : Item {
    override public init() {
        super.init(otio_new_composition())
    }

    public convenience init<ST : Sequence>(name: String? = nil,
                                           sourceRange: TimeRange? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        self.sourceRange = sourceRange
    }

    public convenience init(name: String? = nil, sourceRange: TimeRange? = nil) {
        self.init(name: name, sourceRange: sourceRange, metadata: Metadata.Dictionary.none)
    }
    
    lazy var _childrenProperty = { create_composition_children_vector_property(self) }()
    
    public var children: SerializableObject.ImmutableVector<Composable> {
        get {
            return SerializableObject.ImmutableVector<Composable>(_childrenProperty)
        }
    }

    public var compositionKind: String {
        get { return composition_composition_kind(self) }
    }
    
    public func isParent(of child: Composable) -> Bool {
        return composition_is_parent_of(self, child)
    }
    
    public func hasChild(_ child: Composable) -> Bool {
        return composition_has_child(self, child)
    }
    
    public func handlesOfChild(_ child: Composable) throws -> (RationalTime?, RationalTime?) {
        var rt1 = CxxRationalTime()
        var rt2 = CxxRationalTime()
        var hasLeft = false
        var hasRight = false
        try OTIOError.returnOrThrow { composition_handles_of_child(self, child, &rt1, &rt2, &hasLeft, &hasRight, &$0) }

        return (hasLeft ? RationalTime(rt1) : nil,
                hasRight ? RationalTime(rt2) : nil)
        
    }
    
    public func rangeOfChild(index: Int) throws -> TimeRange {
        return TimeRange(try OTIOError.returnOrThrow { composition_range_of_child_at_index(self, Int32(index), &$0) })
    }

    public func rangeOfChild(_ child: Composable) throws -> TimeRange {
        return TimeRange(try OTIOError.returnOrThrow { composition_range_of_child(self, child, &$0) })
    }

    public func trimmedRangeOfChild(_ child: Composable) throws -> TimeRange? {
        var cxxTimeRange = CxxTimeRange()
        let rangeExists = try OTIOError.returnOrThrow { composition_trimmed_range_of_child(self, child, &cxxTimeRange, &$0) }
        return rangeExists ? TimeRange(cxxTimeRange) : nil
    }

    public func trimmedRangeOfChild(index: Int) throws -> TimeRange {
        return TimeRange(try OTIOError.returnOrThrow { composition_trimmed_range_of_child_at_index(self, Int32(index), &$0) })
    }

    public func trimChildRange(_ range: TimeRange) -> TimeRange? {
        var cxxTimeRange = CxxTimeRange()
        return composition_trim_child_range(self, range.cxxTimeRange, &cxxTimeRange) ? TimeRange(cxxTimeRange) : nil
    }
    
    public func rangeOfAllChildren() throws -> [Composable : TimeRange] {
        let mresult = try OTIOError.returnOrThrow { composition_range_of_all_children(self, &$0) }
        var result = [Composable : TimeRange]()
        for (key, value) in mresult {
            if let keyValue = key as? NSValue,
                let cxxPointer = keyValue.pointerValue,
                let valueValue = value as? NSValue {
                
                var cxxTimeRange = CxxTimeRange()
                valueValue.getValue(&cxxTimeRange, size: MemoryLayout<CxxTimeRange>.size)
                result[SerializableObject.findOrCreate(cxxPtr: cxxPointer) as! Composable] = TimeRange(cxxTimeRange)
            }
        }
        
        return result
    }
    
    public func removeAllChildren() {
        composition_remove_all_children(self)
    }

    public func set<ST : Sequence>(children: ST) throws where ST.Element == Composable {
        removeAllChildren()
        for c in children {
            try append(child: c)
        }
    }

    public func replace(index: Int, withChild child: Composable) throws {
        try OTIOError.returnOrThrow { composition_replace_child(self, Int32(index), child, &$0) }
    }

    public func insert(index: Int, child: Composable) throws {
        try OTIOError.returnOrThrow { composition_insert_child(self, Int32(index), child, &$0) }
    }

    public func remove(index: Int) throws {
        try OTIOError.returnOrThrow { composition_remove_child(self, Int32(index), &$0) }
    }

    public func append(child: Composable) throws {
        try OTIOError.returnOrThrow { composition_append_child(self, child, &$0) }
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
