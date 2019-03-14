//
//  testSO.swift
//  macos_Tests
//
//  Created by David Baraff on 1/17/19.
//

import XCTest
@testable import otio

class testSO: XCTestCase {
    func otioFilePath(_ filename: String) -> String {
        let bundle = Bundle(for: type(of: self))
        let path = bundle.path(forResource: filename, ofType: "")!
        return path
    }
    
    func uniqueTmpFileName(_ basename: String) -> URL {
        let r = UUID().uuidString
        let tmpFile = FileManager.default.temporaryDirectory.appendingPathComponent("otio-tmp-xctest-\(r).otio")
        return tmpFile
    }

    func test_SerializableObject() {
        let so0 = SerializableObject()
        XCTAssert(so0.schemaName == "SerializableObject")
        XCTAssert(so0.schemaVersion == 1)
        
        let so1 = try! SerializableObject.fromJSON(filename: otioFilePath("so1.otio"))
        XCTAssert(so0.isEquivalent(to: so1))
        
        let clip1 = Clip()
        clip1.name = "my-clip-1"
        
        let clip1String = try! clip1.toJSON()
        let clip2 = try! SerializableObject.fromJSON(string: clip1String)
        
        XCTAssertNotNil(clip2 as? Clip)
        XCTAssertNil(clip2 as? Gap)
        XCTAssert(clip1.isEquivalent(to: clip2))
        
        let tmpFile = uniqueTmpFileName("t1")
        try! clip2.toJSON(url: tmpFile)
        XCTAssert(clip2.isEquivalent(to: try! SerializableObject.fromJSON(url: tmpFile)))
        try! FileManager.default.removeItem(at: tmpFile)
        
        XCTAssert(!so0.isUnknownSchema)
        XCTAssert(!clip2.isUnknownSchema)
    }

    func test_UnknownSchema() {
        let so = try! SerializableObject.fromJSON(filename: otioFilePath("unknown1.otio"))
        XCTAssert(so.isUnknownSchema)
        let uso = so as! UnknownSchema
        XCTAssert(uso.originalSchemaVersion == 3 && uso.originalSchemaName == "BogusName")
    }
    
    func test_SerializableObjectWithMetadata() {
        let sowm = SerializableObjectWithMetadata()
        let clip = Clip()
        sowm.metadata["anInt"] = 1
        sowm.metadata["aString"] = "foo"
        sowm.metadata["aVector"] = Metadata.Vector(arrayLiteral: 3, "abc", clip)
        sowm.name = "sowm"
        
        let sowm2 = try! sowm.clone() as! SerializableObjectWithMetadata
        XCTAssert(sowm2.isEquivalent(to: sowm))
        
        let sowm3 = SerializableObjectWithMetadata(name: sowm.name, metadata: sowm.metadata)
        let sowm4 = SerializableObjectWithMetadata(name: sowm3.name, metadata: sowm3.metadata.map { $0 })
        XCTAssert(sowm3.isEquivalent(to: sowm4))
    }

    func test_Composable() {
        let c = Composable()
        c.name = "composable"
        c.metadata["abc"] = 8
        
        let c2 = try! c.clone() as! Composable
        XCTAssert(c2.name == "composable")
        XCTAssert(c2.metadata["abc"] == 8)
        XCTAssert(c2.visible)
        XCTAssert(!c2.overlapping)
        XCTAssertNil(c2.parent)
    }
    
    func test_Marker() {
        let tr = TimeRange(startTime: RationalTime(value: 1, rate: 2),
                           duration: RationalTime(value: 4, rate: 30))
        let m = Marker(name: "marker", markedRange: tr, color: Marker.Color.pink.rawValue)
        m.metadata["abc"] = 9
        
        let m2 = try! m.clone() as! Marker
        XCTAssert(m2.name == "marker")
        XCTAssert(m2.metadata["abc"] == 9)
        XCTAssert(m2.markedRange == tr)
        XCTAssert(m2.color == Marker.Color.pink.rawValue)
        XCTAssert(Marker().color == Marker.Color.green.rawValue)
    }
    
    func test_SerializableCollection() {
        let m1 = Marker(name: "marker1")
        let c1 = Clip(name: "clip1")
        let sc = SerializableCollection(name: "sc", children: [m1, c1], metadata: [])
        sc.metadata["abc"] = 10
        
        let sc2 = try! sc.clone() as! SerializableCollection
        XCTAssert(sc2.name == "sc")
        XCTAssert(sc2.metadata["abc"] == 10)
        XCTAssert(sc2.children.count == 2)
        XCTAssert(sc2.children[0].isEquivalent(to: m1))
        XCTAssert(sc2.children[1].isEquivalent(to: c1))
        sc2.children.append(Clip())
        XCTAssert(sc2.children.count == 3 && (sc2.children[2] as? Clip) != nil)
    }

    func assertErrorType(_ status: OTIOError.Status, expr: () throws -> ()) {
        do {
            try expr()
            XCTFail("Expected to throw OTIO error of type \(status)")
        }
        catch let error as OTIOError {
            if error.status != status {
                XCTFail("Expected error status \(status), got \(error.status) instead")
            }
        }
        catch {
            XCTFail("Expected to throw OTIO Error: throw \(error) instead")
        }
    }

    func test_item() {
        let item = Item(name: "item1")
        item.metadata["abc"] = 11
        
        let item2 = Item(name: item.name, metadata: item.metadata)
        let item3 = Item()
        XCTAssert(item2.isEquivalent(to: item))
        XCTAssert(!item2.isEquivalent(to: item3))
        
        XCTAssert(item.visible)
        XCTAssert(!item.overlapping)

        assertErrorType(.notImplemented) { try _ = item.duration() }
        assertErrorType(.notImplemented) { try _ = item.availableRange() }
        assertErrorType(.notImplemented) { try _ = item.trimmedRange() }
        assertErrorType(.notImplemented) { try _ = item.visibleRange() }
        assertErrorType(.notAChild) { try _ = item.rangeInParent() }
        
        let tr = TimeRange(startTime: RationalTime(value: 10, rate: 12), duration: RationalTime(value: 14, rate: 24))
        XCTAssert(try item.transformed(time: tr.startTime, toItem: item) == tr.startTime)
        XCTAssert(try item.transformed(timeRange: tr, toItem: item) == tr)
    }

    func testD0() {
        var v = Metadata.Vector()
        for i in 0..<10 {
            v.append(i)
        }

        v.replaceSubrange(Range(uncheckedBounds: (0, 0)), with: ["alpha", "beta", "gamma", "delta", "epsilon"])
        print(v)

//        for (i, value) in v.enumerated() {
//            print("[\(i)]: \(value)")
//        }
    }
    
    func testI1() {
        let m0 = Marker()
        let m1 = Marker()
        let mnew = Marker()
        mnew.name = "new marker"
        m0.name = "marker0"
        m1.name = "marker1"

        var item:Item? = Item()
        print("Item: ", item!)
        var itemMarkers = item!.markers

        item = Item()
        print("New item is ", item)
        
        itemMarkers.append(contentsOf: [m0, m1])
        print(itemMarkers)
        
        itemMarkers = SerializableObject.Vector<Marker>()
        
        print("Here")
        
        /*
        var mtmp = SerializableObject.Vector<Marker>()
        mtmp.set(contents: [m0, m1, mnew])
        item.markers = mtmp
        
        print(try! item.toJSON())
        print(item.markers)
        item.markers.set(contents: [m0, m1])
        print("now item markers is ", item.markers)
        
        let item2 = Item()
        print("Item2 markers: ", item2.markers)
        
        item2.markers = item.markers
        print("And now, item2.markers is ", item2.markers)

        var itemMarkers = item.markers
        itemMarkers.removeAll()
        
        print("And now item.markers is ", item.markers)
        
        let item2a = item2
        item2a.markers = item2.markers
        
        // item.markers.append(Marker())
        // item.markers.append(Marker())
        
        item.metadata["abc"] = 1
        item.metadata["xyz"] = item
        item.metadata.remove("abc")

        /*
        let a1 = item.markers
        let b1 = item.markers
        let c1 = item.markers
         */
        
        print("Marker count: ", item.markers.count)
        item.markers.append(mnew)

        var mm = item.markers
        print("mm count: ", mm.count)
        mm.append(mnew)

        print("Marker len is ", item.markers.count)
        print("mm count: ", mm.count)
        print("Markers: ", item.markers)
         */
    }

    func testI2() {
        let sc = try! SerializableObject.fromJSON(filename: "/home/deb/sr2.otio") as! SerializableCollection
        for c in sc.children {
            print("Got child: ", c)
        }
    }

    func testU1() {
        let so = try! SerializableObject.fromJSON(filename: "/home/deb/x1.otio")
        if let uso = so as? UnknownSchema {
            print("original schema is ", uso.originalSchemaName, uso.originalSchemaVersion)
        }
    }

    func testD2() {
        let xx = SerializableObjectWithMetadata()
        let md = xx.metadata
        md["a1"] = 1
        md["a2"] = 2
        md["a3"] = 3
        md["a4"] = 4
        md["a5"] = 5
        
        print(xx.metadata)
        
        for (key, value) in xx.metadata {
            if let v: Int = value as? Int {
                if v >= 3 {
                    print("Nuking key", key)
                    xx.metadata.remove(key)
                }
            }
            print(key, value)
        }
        print("------------")

        let md2 = Metadata.Dictionary(arrayLiteral: ("integer", 123), ("Double", 3.14159), ("Bool", true))
            
        xx.metadata["keys"] = Metadata.Vector(contents: md.map { $0.0 })
        xx.metadata["this_is_cool"] = Metadata.Vector(arrayLiteral: 1, 3, "alpha")
        let mv = Metadata.Vector(arrayLiteral: 1, 3, "alpha", md)
        xx.metadata["this_is_really_cool"] = Metadata.Vector(mv.compactMap { ($0 as? Int) == nil ? $0 : nil })
        
        var c = xx.metadata["this_is_really_cool"] as! Metadata.Vector
        c.append(45678)
        
        let d = (xx.metadata["this_is_really_cool"] as? Metadata.Vector)?.description
        // c1.append(12345)

//        xx.metadata["legal?"] = (3, 4)
        
        print(try! xx.toJSON())
    }
    
    func testD1() {
        let xx = Clip()
        
        if let a: Int = xx.metadata["abc"] {
            print("Yes, abc is: ", a)
        }
        xx.metadata["abc"] = 3.2498
        xx.metadata["nested_copy"] = xx.metadata["nested"]
        
        if let b: Double = xx.metadata["abc"] {
            print("[2] Yes, abc is now: ", b)
        }
        
        if let r1: RationalTime = (xx.metadata["nested"] as? Metadata.Dictionary)?["r1"] {
            print("Got r1: ", r1)
        }
        do {
            try print(xx.toJSON())
        }
        catch {
            print("OOPS: ", error)
        }
        
        print(xx.metadata)
    }
}

