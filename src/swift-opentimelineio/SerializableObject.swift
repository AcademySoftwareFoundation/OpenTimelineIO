//
//  SerializableObject.swift
//
//  Created by David Baraff on 1/17/19.
//

typealias CxxSerializableObjectPtr = UnsafeMutableRawPointer

public class SerializableObject: CxxRetainer {
    // MARK: - public API
    
    override public var description: String {
        let addr1 = ObjectIdentifier(self).hashValue
        let addr2 = Int(bitPattern: cxxSerializableObject())
        return "\(String(describing: type(of: self))) <swift: 0x\(String(format: "%x", addr1)), C++: \(String(format: "%p", addr2))>"
    }
    
    override public init() {
        super.init()
        setCxxSerializableObject(otio_new_serializable_object())
        SerializableObject.wrapperCache.insert(key: cxxSerializableObject(), value: self)
    }

    public func toJSON(url: URL, indent: Int = 4) throws {
        return try toJSON(filename: url.path, indent: indent)
    }

    public func toJSON(filename: String, indent: Int = 4) throws {
        return try OTIOError.returnOrThrow { serializable_object_to_json_file(self, filename, Int32(indent), &$0) }
    }

    public func toJSON(indent: Int = 4) throws -> String {
        return try OTIOError.returnOrThrow { serializable_object_to_json_string(self, Int32(indent), &$0) }
    }
    
    static public func fromJSON(url: URL) throws -> SerializableObject {
        return try fromJSON(filename: url.path)
    }
    
    static public func fromJSON(filename: String) throws -> SerializableObject {
        let cxxPtr = try OTIOError.returnOrThrow { serializable_object_from_json_file(filename, &$0) }
        return SerializableObject.wrapperCreator.create(cxxPtr: cxxPtr)
    }

    static public func fromJSON(string: String) throws -> SerializableObject {
        let cxxPtr = try OTIOError.returnOrThrow { serializable_object_from_json_string(string, &$0) }
        return SerializableObject.wrapperCreator.create(cxxPtr: cxxPtr)
    }

    public func isEquivalent(to other: SerializableObject) -> Bool {
        return serializable_object_is_equivalent_to(self, other)
    }
    
    public func clone() throws -> SerializableObject {
        let cxxPtr = try OTIOError.returnOrThrow { serializable_object_clone(self, &$0) }
        return SerializableObject.wrapperCreator.create(cxxPtr: cxxPtr)
    }
    
    public final var isUnknownSchema: Bool {
        return serializable_object_is_unknown_schema(self)
    }
    
    public final var schemaName:  String {
        return serializable_object_schema_name(self)
    }

    public final var schemaVersion: Int {
        return Int(serializable_object_schema_version(self))
    }

    // MARK: - private API
    static private let wrapperCache = WrapperCache<SerializableObject>()
    static private let wrapperCreator = WrapperCreator()
    
    init(_ cxxPtr: CxxSerializableObjectPtr) {
        super.init()
        setCxxSerializableObject(cxxPtr)
        SerializableObject.wrapperCache.insert(key: cxxSerializableObject(), value: self)
    }
    
    deinit {
        SerializableObject.wrapperCache.remove(key: cxxSerializableObject())
    }
    
    // let cxxRetainer: CxxRetainer
    
    internal class WrapperCreator {
        var creationFunctions = [String : (CxxSerializableObjectPtr) -> SerializableObject]()
        
        init() {
            creationFunctions["Clip"] = { Clip($0) }
            creationFunctions["Composable"] = { Composable($0) }
            creationFunctions["Composition"] = { Composition($0) }
            creationFunctions["Effect"] = { Effect($0) }
            creationFunctions["ExternalReference"] = { ExternalReference($0) }
            creationFunctions["FreezeFrame"] = { FreezeFrame($0) }
            creationFunctions["Gap"] = { Gap($0) }
            creationFunctions["GeneratorReference"] = { GeneratorReference($0) }
            creationFunctions["Item"] = { Item($0) }
            creationFunctions["LinearTimeWarp"] = { LinearTimeWarp($0) }
            creationFunctions["Marker"] = { Marker($0) }
            creationFunctions["MediaReference"] = { MediaReference($0) }
            creationFunctions["MissingReference"] = { MissingReference($0) }
            creationFunctions["SerializableCollection"] = { SerializableCollection($0) }
            creationFunctions["SerializableObject"] = { SerializableObject($0) }
            creationFunctions["SerializableObjectWithMetadata"] = { SerializableObjectWithMetadata($0) }
            creationFunctions["Stack"] = { Stack($0) }
            creationFunctions["TimeEffect"] = { TimeEffect($0) }
            creationFunctions["Timeline"] = { Timeline($0) }
            creationFunctions["Track"] = { Track($0) }
            creationFunctions["Transition"] = { Transition($0) }
            creationFunctions["UnknownSchema"] = { UnknownSchema($0) }
        }
        
        func create(cxxPtr: UnsafeMutableRawPointer) -> SerializableObject {
            let schemaName = serializable_object_schema_name_from_ptr(cxxPtr)
            guard let creationFunc = creationFunctions[schemaName] else {
                fatalError("No function registered to create Swift wrapper for schema-name \(schemaName)")
            }
            return creationFunc(cxxPtr)
        }
    }
    
    static func findOrCreate(cxxPtr: UnsafeMutableRawPointer) -> SerializableObject {
        return SerializableObject.wrapperCache.findOrCreate(cxxPtr: cxxPtr,
                                                            creationFunction: SerializableObject.wrapperCreator.create)
    }

    static func possiblyFindOrCreate(cxxPtr: UnsafeMutableRawPointer?) -> SerializableObject? {
        guard let cxxPtr = cxxPtr else  {
            return nil
        }

        return findOrCreate(cxxPtr: cxxPtr)
    }
    
    public struct ImmutableVector<SOType : SerializableObject> : Collection, CustomStringConvertible  {
        public typealias Index = Int
        public typealias Element = Iterator.Element
        
        let cxxVectorProperty: CxxVectorProperty
        let propertyRetainer: CxxRetainer?
        
        public init(_ cxxVectorProperty: CxxVectorProperty) {
            self.cxxVectorProperty = cxxVectorProperty
            self.propertyRetainer = cxxVectorProperty.cxxRetainer
        }
        
        public init() {
            cxxVectorProperty = CxxVectorProperty()
            propertyRetainer = nil
            
            switch ObjectIdentifier(SOType.self) {
            case ObjectIdentifier(Marker.self):
                serializable_object_new_marker_vector(cxxVectorProperty)
            case ObjectIdentifier(Effect.self):
                serializable_object_new_effect_vector(cxxVectorProperty)
            case ObjectIdentifier(SerializableObject.self):
                serializable_object_new_serializable_object_vector(cxxVectorProperty)
            default:
                fatalError("Unhandled type \(SOType.self) creating SerializableObject.Vector<>")
            }
        }
        
        public init<ST : Sequence>(contents: ST) where ST.Element == Element {
            self.init()
            for value in contents {
                cxxVectorProperty.add(atEnd: value.cxxSerializableObject())
            }
        }
        
        public func makeIterator() -> Iterator {
            return Iterator(self)
        }
        
        public var startIndex: Index {
            return 0
        }
        
        public var endIndex: Index {
            return Int(cxxVectorProperty.count())
        }
        
        public var description: String {
            return "[\(map { String(describing: $0) }.joined(separator: ", "))]"
        }
        
        public subscript(index: Index) -> Element {
            get {
                guard let cxxPtr = cxxVectorProperty.cxxSerializableObject(at: Int32(index)) else {
                    fatalError("otio.SerializableObject.Vector[]: index \(index) out of range")
                }
                return SerializableObject.findOrCreate(cxxPtr: cxxPtr) as! Element
            }
        }
        
        public func index(after i: Index) -> Index {
            return i + 1
        }
        
        public func distance(from start: Index, to end: Index) -> Int {
            return end - start
        }
        
        public struct Iterator : IteratorProtocol, Comparable {
            public typealias Element = SOType
            var position: Int32
            let vector: ImmutableVector
            
            public init(_ vector: ImmutableVector) {
                self.vector = vector
                self.position = 0
            }
            
            public mutating func next() ->  Element? {
                if let cxxPtr = vector.cxxVectorProperty.cxxSerializableObject(at: position) {
                    position += 1
                    return (SerializableObject.findOrCreate(cxxPtr: cxxPtr) as! SOType)
                }
                return nil
            }
            
            public static func < (_ lhs: Iterator, _ rhs: Iterator) -> Bool {
                return lhs.position < rhs.position
            }
            
            public static func == (_ lhs: Iterator, _ rhs: Iterator) -> Bool {
                return lhs.position == rhs.position
            }
        }
    }

    public struct Vector<SOType : SerializableObject> : RangeReplaceableCollection, CustomStringConvertible {
        public typealias Index = Int
        public typealias Element = Iterator.Element
        
        let cxxVectorProperty: CxxVectorProperty
        let propertyRetainer: CxxRetainer?
        
        public init(_ cxxVectorProperty: CxxVectorProperty) {
            self.cxxVectorProperty = cxxVectorProperty
            self.propertyRetainer = cxxVectorProperty.cxxRetainer
        }
        
        public init() {
            cxxVectorProperty = CxxVectorProperty()
            propertyRetainer = nil
            
            switch ObjectIdentifier(SOType.self) {
            case ObjectIdentifier(Marker.self):
                serializable_object_new_marker_vector(cxxVectorProperty)
            case ObjectIdentifier(Effect.self):
                serializable_object_new_effect_vector(cxxVectorProperty)
            case ObjectIdentifier(SerializableObject.self):
                serializable_object_new_serializable_object_vector(cxxVectorProperty)
            default:
                fatalError("Unhandled type \(SOType.self) creating SerializableObject.Vector<>")
            }
        }
        
        public init<ST : Sequence>(contents: ST) where ST.Element == Element {
            self.init()
            for value in contents {
                cxxVectorProperty.add(atEnd: value.cxxSerializableObject())
            }
        }
    
        public mutating func set(contents: Vector) {
            cxxVectorProperty.copyContents(contents.cxxVectorProperty)
        }
        
        public mutating func set<ST : Sequence>(contents: ST) where ST.Element == Element {
            cxxVectorProperty.clear()
            for value in contents {
                cxxVectorProperty.add(atEnd: value.cxxSerializableObject())
            }
        }

        public func makeIterator() -> Iterator {
            return Iterator(self)
        }
        
        public var startIndex: Index {
            return 0
        }
        
        public var endIndex: Index {
            return Int(cxxVectorProperty.count())
        }
        
        public var description: String {
            return "[\(map { String(describing: $0) }.joined(separator: ", "))]"
        }
    
        public mutating func replaceSubrange<C : Collection>(_ subrange: Range<Index>, with newElements: C) where C.Element == Element {
            let tailRange = Range(uncheckedBounds: (subrange.upperBound, endIndex))
            
            if newElements.count > subrange.count {
                let nAdded = newElements.count - subrange.count
                cxxVectorProperty.shrinkOrGrow(Int32(nAdded), grow: true)
                for index in tailRange.reversed() {
                    cxxVectorProperty.move(Int32(index), to: Int32(index + nAdded))
                }
            }
            else if newElements.count < subrange.count {
                let nRemoved = subrange.count - newElements.count
                for index in tailRange {
                    cxxVectorProperty.move(Int32(index), to: Int32(index - nRemoved))
                }
                cxxVectorProperty.shrinkOrGrow(Int32(nRemoved), grow: false)
            }
            
            var index = subrange.lowerBound
            for value in newElements {
                self[index] = value
                index += 1
            }
        }
        
        public mutating func removeAll(keepingCapacity keepCapacity: Bool = false) {
            cxxVectorProperty.clear()
        }
            
        public subscript(index: Index) -> Element {
            get {
                guard let cxxPtr = cxxVectorProperty.cxxSerializableObject(at: Int32(index)) else {
                    fatalError("otio.SerializableObject.Vector[]: index \(index) out of range")
                }
                return SerializableObject.findOrCreate(cxxPtr: cxxPtr) as! Element
            }
            set(newValue) {
                cxxVectorProperty.store(Int32(index), value: newValue.cxxSerializableObject())
            }
        }

        public func index(after i: Index) -> Index {
            return i + 1
        }
        
        public func distance(from start: Index, to end: Index) -> Int {
            return end - start
        }
        
        public struct Iterator : IteratorProtocol, Comparable {
            public typealias Element = SOType
            var position: Int32
            let vector: Vector
            
            public init(_ vector: Vector) {
                self.vector = vector
                self.position = 0
            }
            
            public mutating func next() ->  Element? {
                if let cxxPtr = vector.cxxVectorProperty.cxxSerializableObject(at: position) {
                    position += 1
                    return (SerializableObject.findOrCreate(cxxPtr: cxxPtr) as! SOType)
                }
                return nil
            }
            
            public static func < (_ lhs: Iterator, _ rhs: Iterator) -> Bool {
                return lhs.position < rhs.position
            }
            
            public static func == (_ lhs: Iterator, _ rhs: Iterator) -> Bool {
                return lhs.position == rhs.position
            }
        }
    }
}
