//
//  testSO.swift
//  macos_Tests
//
//  Created by David Baraff on 1/17/19.
//

import XCTest
@testable import otio

func outerCode() {
}

var keepMe: SerializableObject?

class testSO: XCTestCase {
    func inner1() {
        let so = SerializableObjectWithMetadata()
        so.name = "Hello!"
        print(so.toJson())
        
        let soSpecial = so.specialObject()
        print("Got back the special object", soSpecial)
        
        let soSpecial2 = so.specialObject()
        print("Got back the special object again", soSpecial2)
        
        print("Are these the same? ", soSpecial === soSpecial2)
    }
    
    func test1() {
        print("Cache size (1): ", SerializableObject.cacheSize())
        inner1()
        print("Cache size (2): ", SerializableObject.cacheSize())
        inner1()
        print("Cache size (3): ", SerializableObject.cacheSize())
    }
}

