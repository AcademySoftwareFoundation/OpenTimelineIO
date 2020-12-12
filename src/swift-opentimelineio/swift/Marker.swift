//
//  Marker.swift
//

import Foundation

public class Marker : SerializableObjectWithMetadata {
    override public init() {
        super.init(otio_new_marker())
    }

    public enum Color: String {
        case pink = "PINK"
        case red = "RED"
        case orange = "ORANGE"
        case yellow = "YELLOW"
        case green = "GREEN"
        case cyan = "CYAN"
        case blue = "BLUE"
        case purple = "PURPLE"
        case magenta = "MAGENTA"
        case black = "BLACK"
        case white = "WHITE"
    }

    public convenience init<ST : Sequence>(name: String? = nil,
                                           markedRange: TimeRange? = nil,
                                           color: String = Color.green.rawValue,
                                           metadata: ST? = nil) where ST.Element == Metadata.Dictionary.Element {
        self.init()
        metadataInit(name, metadata)
        self.color = color
        if let markedRange = markedRange {
            self.markedRange = markedRange
        }
    }
    
    public convenience init(name: String? = nil,
                            markedRange: TimeRange? = nil,
                            color: String = Color.green.rawValue) {
        self.init(name: name, markedRange: markedRange, color: color,
                  metadata: nil as Metadata.Dictionary?)
    }

    public var color: String {
        get { return marker_get_color(self) }
        set { marker_set_color(self, newValue) }
    }

    public var markedRange: TimeRange {
        get { return TimeRange(marker_get_marked_range(self)) }
        set { marker_set_marked_range(self, newValue.cxxTimeRange) }
    }

    override internal init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init(cxxPtr)
    }
}
