//
//  Metadata.swift
//  otio_macos
//
//  Created by David Baraff on 2/25/19.
//

import Foundation

public protocol MetadataValue {
    var metadataType: Metadata.ValueType { get }
}

public enum Metadata {
    typealias Value = MetadataValue
    
    struct UnknownCxxType: MetadataValue {
        var metadataType: ValueType {
            return .unknown
        }

        let typeName: String
    }
    
    public enum ValueType: Int {
        case none = 0
        case bool
        case int
        case double
        case string
        case serializableObject
        case rationalTime
        case timeRange
        case timeTransform
        case dictionary
        case vector
        case unknown
    }
    
    public class Dictionary : CxxAnyDictionaryMutationStamp, MutableCollection, MetadataValue, ExpressibleByArrayLiteral {
        public typealias Element = Iterator.Element
        static let none = nil as Dictionary?
        
        public var metadataType: ValueType {
            return .dictionary
        }
        
        required public convenience init(arrayLiteral elements: Element...) {
            self.init()
            for element in elements {
                self[element.0] = element.1
            }
        }
        
        public convenience override init() {
            self.init(nil, cxxRetainer: nil)
        }

        public convenience init<ST : Sequence>(contents: ST) where ST.Element == Element {
            self.init(nil, cxxRetainer: nil)
            for (key, value) in contents {
                Metadata.withCxxAny(value) {
                    store(key, value: $0)
                }
            }
        }

        deinit {
            Dictionary.wrapperCache.remove(key: cxxAnyDictionaryPtr())
        }
        
        public func set(contents: Dictionary) {
            setContents(contents, destroyingSrc: false)
        }
        
        public func set<ST : Sequence>(contents: ST) where ST.Element == Element {
            setContents(Dictionary(contents: contents), destroyingSrc: true)
        }
        
        public var startIndex: Index {
            return Index(self)
        }
        
        public var endIndex: Index {
            let index = Index(self)
            index.cxxAnyDictionaryIterator.jumpToEnd()
            return index
        }
        
        public func index(after i: Index) -> Index {
            let nextIndex = Index(self)
            nextIndex.cxxAnyDictionaryIterator.jumpToIndex(after: i.cxxAnyDictionaryIterator)
            return nextIndex
        }
        
        func remove( _ key: String) {
            removeValue(key)
        }

        public func makeIterator() -> Dictionary.Iterator {
            return Iterator(self)
        }

        public subscript(index: Index) -> Element {
            get {
                var cxxAny = CxxAny()
                if let key = index.cxxAnyDictionaryIterator.currentElement(&cxxAny) {
                    return (key, Metadata.cxxAnyToMetadataValue(cxxAny))
                }
                else {
                    fatalError("otio.Metadata.Dictionary[]: invalid index")
                }
            }
            set(newValue) {
                Metadata.withCxxAny(newValue.1) {
                    index.cxxAnyDictionaryIterator.store($0)
                }
            }
        }
        
        public subscript(_ key: String) -> MetadataValue? {
            get {
                var cxxAny = CxxAny()
                return lookup(key, result: &cxxAny) ? Metadata.cxxAnyToMetadataValue(cxxAny) : nil
            }
            set {
                if let value = newValue {
                    withCxxAny(value) {
                        store(key, value: $0)
                    }
                }
                else {
                    removeValue(key)
                }
            }
        }
        
        public subscript<T : MetadataValue>(_ key: String) -> T? {
            get {
                var cxxAny = CxxAny()
                return lookup(key, result: &cxxAny) ? Metadata.cxxAnyToMetadataValue(cxxAny) as? T: nil
            }
            set {
                if let value = newValue {
                    withCxxAny(value) {
                        store(key, value: $0)
                    }
                }
                else {
                    removeValue(key)
                }
            }
        }
        
        public struct Index: Comparable {
            let cxxAnyDictionaryIterator: CxxAnyDictionaryIterator
            
            public init(_ cxxAnyDictionaryMutationStamp : CxxAnyDictionaryMutationStamp) {
                cxxAnyDictionaryIterator = CxxAnyDictionaryIterator(cxxAnyDictionaryMutationStamp)
            }
            
            static public func < (_ lhs: Index, _ rhs: Index) -> Bool {
                return lhs.cxxAnyDictionaryIterator.lessThan(rhs.cxxAnyDictionaryIterator)
            }
            
            static public func == (_ lhs: Index, _ rhs: Index) -> Bool {
                return lhs.cxxAnyDictionaryIterator.equal(rhs.cxxAnyDictionaryIterator)
            }
        }

        public struct Iterator : IteratorProtocol {
            public typealias Element = (String, MetadataValue)
            let cxxAnyDictionaryIterator: CxxAnyDictionaryIterator

            public init(_ cxxAnyDictionaryMutationStamp : CxxAnyDictionaryMutationStamp) {
                cxxAnyDictionaryIterator = CxxAnyDictionaryIterator(cxxAnyDictionaryMutationStamp)
            }
            
            public func next() -> (String, MetadataValue)? {
                var cxxAny = CxxAny()
                if let key = cxxAnyDictionaryIterator.nextElement(&cxxAny) {
                    return (key, cxxAnyToMetadataValue(cxxAny))
                }
                return nil
            }
        }
        
        public func distance(from start: Index, to end: Index) -> Int {
            return Int(start.cxxAnyDictionaryIterator.distance(to: end.cxxAnyDictionaryIterator))
        }
        
        override public var description: String {
            return "[\(map { "\($0.0): \($0.1)" }.joined(separator: ", "))]"
        }
        
        static private let wrapperCache = WrapperCache<Dictionary>()

        static public func wrap(anyDictionaryPtr: UnsafeMutableRawPointer, cxxRetainer: CxxRetainer? = nil) -> Dictionary {
            return wrapperCache.findOrCreate(cxxPtr: anyDictionaryPtr) {
                let d = Dictionary($0, cxxRetainer: cxxRetainer)
                wrapperCache.insert(key: anyDictionaryPtr, value: d)
                return d
            }
        }
    }

    public class Vector : CxxAnyVectorMutationStamp, RangeReplaceableCollection, MetadataValue {
        public typealias Index = Int
        public typealias Element = Iterator.Element

        public var metadataType: ValueType {
            return .vector
        }
        
        required public override init() {
            super.init(nil)
        }
        
        public convenience init(arrayLiteral: Element...) {
            self.init()
            for element in arrayLiteral {
                Metadata.withCxxAny(element) {
                    add(atEnd: $0)
                }
            }
        }
        
        init(_ cxxAnyVectorPtr: UnsafeMutableRawPointer) {
            super.init(cxxAnyVectorPtr)
        }
        
        public convenience init<ST : Sequence>(contents: ST) where ST.Element == Element {
            self.init()
            for value in contents {
                Metadata.withCxxAny(value) {
                    add(atEnd: $0)
                }
            }
        }
        
        public func set(contents: Vector) {
            setContents(contents, destroyingSrc: false)
        }
        
        public func set<ST : Sequence>(contents: ST) where ST.Element == Element {
            setContents(Vector(contents: contents), destroyingSrc: true)
        }
        
        override public var description: String {
            return "[\(map { String(describing: $0) }.joined(separator: ", "))]"
        }

        public func replaceSubrange<C : Collection>(_ subrange: Range<Index>, with newElements: C) where C.Element == Element {
            let tailRange = Range(uncheckedBounds: (subrange.upperBound, endIndex))

            if newElements.count > subrange.count {
                let nAdded = newElements.count - subrange.count
                shrinkOrGrow(Int32(nAdded), grow: true)
                for index in tailRange.reversed() {
                    move(Int32(index), to: Int32(index + nAdded))
                }
            }
            else if newElements.count < subrange.count {
                let nRemoved = subrange.count - newElements.count
                for index in tailRange {
                    move(Int32(index), to: Int32(index - nRemoved))
                }
                shrinkOrGrow(Int32(nRemoved), grow: false)
            }

            var index = subrange.lowerBound
            for value in newElements {
                self[index] = value
                index += 1
            }
        }
        
        public func makeIterator() -> Iterator {
            return Iterator(self)
        }
        
        public var startIndex: Index {
            return 0
        }
        
        public var endIndex: Index {
            return Int(count())
        }
        
        public subscript(index: Index) -> Element {
            get {
                var cxxAny = CxxAny()
                if !lookup(Int32(index), result: &cxxAny) {
                    fatalError("otio.Metadata.Vector[]: index \(index) out of range")
                }
                return Metadata.cxxAnyToMetadataValue(cxxAny)
            }
            set(newValue) {
                Metadata.withCxxAny(newValue) {
                    store(Int32(index), value: $0)
                }
            }
        }
        
        public subscript<T : MetadataValue>(_ index: Int) -> T? {
            get {
                return self[index] as? T
            }
            set {
                if let value = newValue {
                    self[index] = value
                }
            }
        }
        
        public func index(after i: Index) -> Index {
            return i + 1
        }
        
        public func distance(from start: Index, to end: Index) -> Int {
            return end - start
        }
        
        public struct Iterator : IteratorProtocol, Comparable {
            public typealias Element = MetadataValue
            var position: Int32
            let vector: Vector
            
            public init(_ vector: Vector) {
                self.vector = vector
                self.position = 0
            }
            
            public mutating func next() ->  MetadataValue? {
                var cxxAny = CxxAny()
                if vector.lookup(position, result: &cxxAny) {
                    position += 1
                    return Metadata.cxxAnyToMetadataValue(cxxAny)
                }
                else {
                    return nil
                }
            }
            
            public static func < (_ lhs: Iterator, _ rhs: Iterator) -> Bool {
                return lhs.position < rhs.position
            }
            
            public static func == (_ lhs: Iterator, _ rhs: Iterator) -> Bool {
                return lhs.position == rhs.position
            }
        }
        
        deinit {
            Vector.wrapperCache.remove(key: cxxAnyVectorPtr())
        }
        
        static private let wrapperCache = WrapperCache<Vector>()
        
        static public func wrap(anyVectorPtr: UnsafeMutableRawPointer) -> Vector {
            return wrapperCache.findOrCreate(cxxPtr: anyVectorPtr) {
                let v = Vector($0)
                wrapperCache.insert(key: anyVectorPtr, value: v)
                return v
            }
        }
    }

    static func cxxAnyToMetadataValue(_ cxxAny: CxxAny) -> MetadataValue {
        if let valueType = ValueType(rawValue: Int(cxxAny.type_code)) {
            switch valueType {
            case .none:
                return NSNull()
            case .bool:
                return cxxAny.value.b
            case .int:
                return Int(cxxAny.value.i)
            case .double:
                return cxxAny.value.d
            case .string:
                return String(cString: cxxAny.value.s)
            case .rationalTime:
                return RationalTime(cxxAny.value.rt)
            case .timeRange:
                return TimeRange(cxxAny.value.tr)
            case .timeTransform:
                return TimeTransform(cxxAny.value.tt)
            case .serializableObject:
                return SerializableObject.findOrCreate(cxxPtr: cxxAny.value.ptr)
            case .dictionary:
                return Dictionary.wrap(anyDictionaryPtr: cxxAny.value.ptr)
            case .unknown:
                return UnknownCxxType(typeName: String(cString: cxxAny.value.s))
            case .vector:
                return Vector.wrap(anyVectorPtr: cxxAny.value.ptr)
            }
        }
        
        fatalError("Metadata.cxxAnyToMetadataValue.cxxAnyToMetadataValue: invalid integer code \(cxxAny.type_code)")
    }
    
    private static func createCxxAny(_ type: ValueType, _ value: CxxAnyValue) -> CxxAny {
        return CxxAny(type_code: Int32(type.rawValue), value: value)
    }
    
    private static func withCxxAny(_ value: MetadataValue, work: (CxxAny) -> ()) {
        switch value.metadataType {
        case .none:
            work(createCxxAny(.none, .init(i: 0)))
        case .bool:
            work(createCxxAny(.bool, .init(b: value as! Bool)))
        case .int:
            work(createCxxAny(.int, .init(i: Int64(value as! Int))))
        case .double:
            work(createCxxAny(.double, .init(d: value as! Double)))
        case .string:
            let s = value as! String
            s.withCString {
                work(createCxxAny(.string, .init(s: $0)))
            }
        case .rationalTime:
            work(createCxxAny(.rationalTime, .init(rt: (value as! RationalTime).cxxRationalTime)))
        case .timeRange:
            work(createCxxAny(.timeRange, .init(tr: (value as! TimeRange).cxxTimeRange)))
        case .timeTransform:
            work(createCxxAny(.timeTransform, .init(tt: (value as! TimeTransform).cxxTimeTransform)))
        case .dictionary:
            work(createCxxAny(.dictionary, .init(ptr: (value as! Dictionary).cxxAnyDictionaryPtr())))
        case .vector:
            work(createCxxAny(.vector, .init(ptr: (value as! Vector).cxxAnyVectorPtr())))
        case .serializableObject:
            work(createCxxAny(.serializableObject, .init(ptr: (value as! SerializableObject).cxxSerializableObject())))
        case .unknown:
            (value as! UnknownCxxType).typeName.withCString {
                work(createCxxAny(.unknown, .init(s: $0)))
            }
        }
    }
}

extension NSNull : MetadataValue { public var metadataType: Metadata.ValueType { return .none } }
extension Bool : MetadataValue { public var metadataType: Metadata.ValueType { return .bool } }
extension Int : MetadataValue { public var metadataType: Metadata.ValueType { return .int } }
extension Double : MetadataValue { public var metadataType: Metadata.ValueType { return .double } }
extension String : MetadataValue { public var metadataType: Metadata.ValueType { return .string } }
extension SerializableObject : MetadataValue { public var metadataType: Metadata.ValueType { return .serializableObject } }
extension RationalTime : MetadataValue { public var metadataType: Metadata.ValueType { return .rationalTime } }
extension TimeRange : MetadataValue { public var metadataType: Metadata.ValueType { return .timeRange } }
extension TimeTransform : MetadataValue { public var metadataType: Metadata.ValueType { return .timeTransform } }

