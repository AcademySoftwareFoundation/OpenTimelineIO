//
//  Item.swift
//

import Foundation

public class Item : Composable {
    override public init() {
        super.init(otio_new_item())
    }
    
    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
    
    public convenience init<ST : Sequence>(name: String? = nil,
                                           sourceRange: TimeRange? = nil,
                                           effects: [Effect]? = nil,
                                           markers: [Marker]? = nil,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        if let sourceRange = sourceRange {
            self.sourceRange = sourceRange
        }
        if let markers = markers {
            self.markers.set(contents: markers)
        }
        if let effects = effects {
            self.effects.set(contents: effects)
        }
    }
    
    public convenience init(name: String? = nil,
                            sourceRange: TimeRange? = nil,
                            effects: [Effect]? = nil,
                            markers: [Marker]? = nil) {
        self.init(name: name, sourceRange: sourceRange, effects: effects, markers: markers,
                  metadata: Metadata.Dictionary.none)
    }

    public var sourceRange: TimeRange? {
        get {
            var tr = CxxTimeRange()
            return item_get_source_range(self, &tr) ? TimeRange(tr) : nil
        }
        set {
            if let newValue = newValue {
                item_set_source_range(self, newValue.cxxTimeRange)
            }
            else {
                item_set_source_range_to_null(self)
            }
        }
    }
    
    lazy var _markersProperty = { create_item_markers_vector_property(self) }()
    lazy var _effectsProperty = { create_item_effects_vector_property(self) }()
    
    public var markers: SerializableObject.Vector<Marker> {
        get {
            return SerializableObject.Vector<Marker>(_markersProperty)
        }
        set {
            _markersProperty.copyContents(newValue.cxxVectorProperty)
        }
    }

    public var effects: SerializableObject.Vector<Effect> {
        get {
            return SerializableObject.Vector<Effect>(_effectsProperty)
        }
        set {
            _effectsProperty.copyContents(newValue.cxxVectorProperty)
        }
    }
    
    public func availableRange() throws -> TimeRange {
        return try TimeRange(OTIOError.returnOrThrow { item_available_range(self, &$0) })
    }
    
    public func trimmedRange() throws -> TimeRange {
        return try TimeRange(OTIOError.returnOrThrow { item_trimmed_range(self, &$0) })
    }

    public func visibleRange() throws -> TimeRange {
        return try TimeRange(OTIOError.returnOrThrow { item_visible_range(self, &$0) })
    }
    
    public func trimmedRangeInParent() throws -> TimeRange? {
        var rt = CxxTimeRange()
        return (try OTIOError.returnOrThrow { item_trimmed_range_in_parent(self, &rt, &$0) }) ? TimeRange(rt) : nil
    }
    
    public func rangeInParent() throws -> TimeRange {
        return try TimeRange(OTIOError.returnOrThrow { item_range_in_parent(self, &$0) })
    }
    
    public func transformed(time: RationalTime, toItem: Item) throws -> RationalTime {
        return try RationalTime(OTIOError.returnOrThrow { item_transformed_time(self, time.cxxRationalTime, toItem, &$0) })
    }
    
    public func transformed(timeRange: TimeRange, toItem: Item) throws -> TimeRange {
        return try TimeRange(OTIOError.returnOrThrow { item_transformed_time_range(self, timeRange.cxxTimeRange, toItem, &$0) })
    }
}
