//
//  SerializableObject.swift
//
//  Created by David Baraff on 1/17/19.
//

public class SerializableObject: CustomStringConvertible {
    // MARK: - public API
    
    public var description: String {
        let addr = ObjectIdentifier(self).hashValue
        let addr2 = cxxPtr.hashValue
        return "\(String(describing: type(of: self))) <swift: 0x\(String(format: "%x", addr)), C++: 0x\(String(format: "%x", addr2)))"
    }
    
    public init() {
        cxxRetainer = new_serializable_object()
        SerializableObject.wrapperCache.insert(key: cxxRetainer, wrapper: self)
    }

    public func toJSON(filename: String, indent: Int = 4) throws {
        return try OTIOError.returnOrThrow { serializable_object_to_json_file(cxxRetainer, filename, Int32(indent), &$0) }
    }
    
    public func toJSON(indent: Int = 4) throws -> String {
        return try OTIOError.returnOrThrow { serializable_object_to_json_string(cxxRetainer, Int32(indent), &$0) }
    }
    
    static public func fromJSON(filename: String) throws -> SerializableObject {
        let cxxPtr = try OTIOError.returnOrThrow { serializable_object_from_json_file(filename, &$0) }
        return wrapperCache.findOrCreate(cxxPtr: cxxPtr)
    }

    static public func fromJSON(string: String) throws -> SerializableObject {
        let cxxPtr = try OTIOError.returnOrThrow { serializable_object_from_json_string(string, &$0) }
        return wrapperCache.findOrCreate(cxxPtr: cxxPtr)
    }

    public func isEquivalent(to other: SerializableObject) -> Bool {
        return serializable_object_is_equivalent_to(cxxRetainer, other.cxxRetainer)
    }
    
    public func clone() throws -> SerializableObject {
        let cxxPtr = try OTIOError.returnOrThrow { serializable_object_clone(cxxRetainer, &$0) }
        return SerializableObject.wrapperCache.findOrCreate(cxxPtr: cxxPtr)
    }
    
    final var isUnknownSchema: Bool {
        return serializable_object_is_unknown_schema(cxxRetainer)
    }
    
    public final func schemaName() -> String {
        return serializable_object_schema_name(cxxRetainer)
    }

    public final func schemaVersion() -> Int {
        return Int(serializable_object_schema_version(cxxRetainer))
    }


    // MARK: - private API
    static let wrapperCache = WrapperCache()
    
    init(_ cxxRetainer: CxxRetainer) {
        self.cxxRetainer = cxxRetainer
        SerializableObject.wrapperCache.insert(key: cxxRetainer, wrapper: self)
    }
    
    deinit {
        SerializableObject.wrapperCache.remove(key: cxxRetainer)
    }
    
    private var cxxPtr: UnsafeMutableRawPointer {
        return cxxRetainer.cxxSerializableObject()
    }
    
    let cxxRetainer: CxxRetainer
}
