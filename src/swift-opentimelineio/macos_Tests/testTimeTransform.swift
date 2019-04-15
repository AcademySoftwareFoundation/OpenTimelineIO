//
//  testTimeTransform.swift
//  macos_Tests
//
//  Created by David Baraff on 1/17/19.
//

import XCTest
@testable import otio

class testTransform: XCTestCase {
    func testIdentityTransform() {
        var tstart = RationalTime(value: 12, rate: 25)
        var txform = TimeTransform()
        XCTAssertEqual(tstart, txform.applied(to: tstart))
 
        tstart = RationalTime(value: 12, rate: 25)
        txform = TimeTransform(rate: 50)
        XCTAssertEqual(24, txform.applied(to: tstart).value)
    }
 
    func testOffset() {
        let tstart = RationalTime(value: 12, rate: 25)
        let toffset = RationalTime(value: 10, rate: 25)
        let txform = TimeTransform(offset: toffset)
        XCTAssertEqual(tstart + toffset, txform.applied(to: tstart))
 
        let tr = TimeRange(startTime: tstart, duration: tstart)
        XCTAssertEqual(txform.applied(to: tr), TimeRange(startTime: tstart + toffset, duration: tstart))
    }

    func testScale() {
        let tstart = RationalTime(value: 12, rate: 25)
        let txform = TimeTransform(scale: 2)
        XCTAssertEqual(RationalTime(value: 24, rate: 25), txform.applied(to: tstart))
 
        let tr = TimeRange(startTime: tstart, duration: tstart)
        let tstart_scaled = RationalTime(value: 24, rate: 25)
        XCTAssertEqual(txform.applied(to: tr), TimeRange(startTime: tstart_scaled, duration: tstart_scaled))
    }

    func testRate() {
        let txform1 = TimeTransform()
        let txform2 = TimeTransform(rate: 50)
        XCTAssertEqual(txform2.rate, txform1.applied(to: txform2).rate)
    }
 
    func testComparison() {
        var tstart = RationalTime(value: 12, rate: 25)
        let txform = TimeTransform(offset: tstart, scale: 2)
        let txform2 = TimeTransform(offset: tstart, scale: 2)
        XCTAssertEqual(txform, txform2)
        XCTAssertFalse(txform != txform2)
     
        tstart = RationalTime(value: 23, rate: 25)
        let txform3 = TimeTransform(offset: tstart, scale: 2)
        XCTAssertNotEqual(txform, txform3)
        XCTAssertFalse(txform == txform3)
    }
}

