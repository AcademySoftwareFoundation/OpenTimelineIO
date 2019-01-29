//
//  WrapperCache.swift
//  otio_macos
//
//  Created by David Baraff on 1/24/19.
//

import Foundation

internal class WrapperCache {
    struct WeakHolder {
        weak var serializableObject: SerializableObject?
    }
    
    var creationFunctions = [String : (CxxRetainer) -> SerializableObject]()
    var cxxPtrToSO = [UnsafeMutableRawPointer : WeakHolder]()
    let lock = DispatchQueue(label: "com.pixar.otio.SOWrapperCache")
    
    init() {
        creationFunctions["SerializableObject"] = { SerializableObject($0) }
        creationFunctions["SerializableObjectWithMetadata"] = { SerializableObjectWithMetadata($0) }
    }
    
    func insert(key: CxxRetainer, wrapper: SerializableObject) {
        lock.sync { cxxPtrToSO[key.cxxSerializableObject()] = WeakHolder(serializableObject: wrapper) }
    }
    
    func remove(key: CxxRetainer) {
        _ = lock.sync { cxxPtrToSO.removeValue(forKey: key.cxxSerializableObject()) }
    }
    
    func lookup(cxxPtr: UnsafeMutableRawPointer) -> SerializableObject? {
        return lock.sync { cxxPtrToSO[cxxPtr]?.serializableObject }
    }
    
    func findOrCreate(cxxPtr: UnsafeMutableRawPointer) -> SerializableObject {
        if let so = lookup(cxxPtr: cxxPtr) {
            return so
        }
        
        let cxxRetainer = CxxRetainer(cxxPtr)
        let schemaName = serializable_object_schema_name(cxxRetainer)
        guard let creationFunc = creationFunctions[schemaName] else {
            fatalError("No function registered to create Swift wrapper for schema-name \(schemaName)")
        }
        
        let so = creationFunc(cxxRetainer)
        insert(key: cxxRetainer, wrapper: so)
        return so

    }
}
