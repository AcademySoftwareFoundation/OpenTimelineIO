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
