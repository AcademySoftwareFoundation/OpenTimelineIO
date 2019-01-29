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
        let so0 = SerializableObject()
        print("So0 is ", so0)
        
        let so = SerializableObjectWithMetadata()
        print("So is ", so)
        
        so.name = "Hello!"
        do {
            print(try so.toJson())
        } catch {
            print("Failed to serialize:", error)
        }
        
        /*
        let soSpecial = so.specialObject()
        print("Got back the special object", soSpecial)
        
        let soSpecial2 = so.specialObject()
        print("Got back the special object again", soSpecial2)
        
        print("Are these the same? ", soSpecial === soSpecial2)
         */
    }
    
    func test1() {
        inner1()
        inner1()
    }
}

