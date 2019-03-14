//
//  WrapperCache.swift
//  otio_macos
//
//  Created by David Baraff on 1/24/19.
//

import Foundation

internal class WrapperCache<CachedObject: AnyObject> {
    struct WeakHolder {
        weak var cachedObject: CachedObject?
    }
    
    var cxxPtrToCachedObject = [UnsafeMutableRawPointer : WeakHolder]()
    let lock = DispatchQueue(label: "com.pixar.otio.SOWrapperCache-" + String(describing: type(of: CachedObject.self)))
    
    func insert(key: UnsafeMutableRawPointer, value: CachedObject) {
        lock.sync { cxxPtrToCachedObject[key] = WeakHolder(cachedObject: value) }
    }
    
    func remove(key: UnsafeMutableRawPointer) {
        _ = lock.sync { cxxPtrToCachedObject.removeValue(forKey: key) }
    }
    
    func lookup(key: UnsafeMutableRawPointer) -> CachedObject? {
        return lock.sync { cxxPtrToCachedObject[key]?.cachedObject }
    }
    
    func findOrCreate(cxxPtr: UnsafeMutableRawPointer, creationFunction: (UnsafeMutableRawPointer) -> (CachedObject)) -> CachedObject {
        return lookup(key: cxxPtr) ?? creationFunction(cxxPtr)
    }
}
