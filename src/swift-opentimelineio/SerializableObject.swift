//
//  SerializableObject.swift
//
//  Created by David Baraff on 1/17/19.
//
public class SerializableObject {
    struct WeakSO {
        weak var serializableObject: SerializableObject?
    }
    
    static var wrapperCache = [UnsafeMutableRawPointer : WeakSO]()

    init(_ cxxRetainer: CxxRetainer) {
        self.cxxRetainer = cxxRetainer
        addToCache()
    }
    
    func myID() -> Int {
        return ObjectIdentifier(self).hashValue
    }
    
    var interiorObject: UnsafeMutableRawPointer {
        return cxxRetainer.cxxSerializableObject()
    }
    
    func addToCache() {
        print("Adding Wrapper at ", String(format: "%x", myID()))
        SerializableObject.wrapperCache[interiorObject] = WeakSO(serializableObject: self)
    }
    
    public final func schemaName() -> String {
        return serializable_object_schema_name(cxxRetainer)
    }
    
    public final func toJson() -> String {
        return serializable_object_to_json(cxxRetainer)
    }
    
    public init() {
        cxxRetainer = new_serializable_object()
        addToCache()
    }

    deinit {
        print("Removing Wrapper at", String(format: "%x", myID()))
        SerializableObject.wrapperCache.removeValue(forKey: interiorObject)
    }
    
    public func specialObject() -> SerializableObject {
        let soPtr = serializable_object_special_object();
        if let weakSO = SerializableObject.wrapperCache[soPtr],
            let so = weakSO.serializableObject {
            return so
        }
        else {
            return SerializableObjectWithMetadata(existing: soPtr)
        }
    }
    
    static public func cacheSize() -> Int {
        return wrapperCache.count
    }
    
    let cxxRetainer: CxxRetainer
}

public class SerializableObjectWithMetadata : SerializableObject {
    override public init() {
        super.init(new_serializable_object_with_metadata(nil))
    }
    
    public init(existing: UnsafeMutableRawPointer) {
        super.init(new_serializable_object_with_metadata(existing))
    }

    var name: String {
        get { return serializable_object_with_metadata_name(cxxRetainer) }
        set { serializable_object_with_metadata_set_name(cxxRetainer, newValue) }
    }
    
}
