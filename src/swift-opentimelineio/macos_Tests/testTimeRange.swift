//
//  testTimeRange.swift
//  macos_Tests
//
//  Created by David Baraff on 1/15/19.
//

import XCTest
@testable import otio

class testRange: XCTestCase {
    func testCreate() {
        let tr = TimeRange()
        let blank = RationalTime()
        XCTAssertEqual(tr.startTime, blank)
        XCTAssertEqual(tr.duration, blank)

        let tr2 = TimeRange(startTime: RationalTime(value: 0, rate: 25))
        XCTAssertEqual(tr2.duration, RationalTime())
    }

    func testEndTime() {
        let rt_start = RationalTime(value: 1, rate: 24)
        var rt_dur = RationalTime(value: 5, rate: 24)
        var tr = TimeRange(startTime: rt_start, duration: rt_dur)
        XCTAssertEqual(tr.duration, rt_dur)
        XCTAssertEqual(tr.endTimeExclusive(), rt_start + rt_dur)
        XCTAssertEqual(tr.endTimeInclusive(), rt_start + rt_dur - RationalTime(value: 1, rate: 24))

        rt_dur = RationalTime(value: 5.5, rate: 24)
        tr = TimeRange(startTime: rt_start, duration: rt_dur)
        XCTAssertEqual(tr.endTimeExclusive(), rt_start + rt_dur)
        XCTAssertEqual(tr.endTimeInclusive(), RationalTime(value: 6, rate: 24))
    }

    func testCompare() {
        let start_time1 = RationalTime(value: 18, rate: 24)
        let duration1 = RationalTime(value: 7, rate: 24)
        let tr1 = TimeRange(startTime: start_time1, duration: duration1)
        
        let start_time2 = RationalTime(value: 18, rate: 24)
        let duration2 = RationalTime(value: 14, rate: 48)
        let tr2 = TimeRange(startTime: start_time2, duration: duration2)
        XCTAssertEqual(tr1, tr2)
        XCTAssertFalse(tr1 != tr2)
     
        let start_time3 = RationalTime(value: 20, rate: 24)
        let duration3 = RationalTime(value: 3, rate: 24)
        let tr3 = TimeRange(startTime: start_time3, duration: duration3)
        XCTAssertNotEqual(tr1, tr3)
        XCTAssertFalse(tr1 == tr3)
    }
     
    func testClamped() {
        let test_point_min = RationalTime(value: -2, rate: 24)
        let test_point_max = RationalTime(value: 6, rate: 24)
     
        let tr = TimeRange(startTime: RationalTime(value: -1, rate: 24),
                           duration:  RationalTime(value: 6, rate: 24))
     
        let other_tr = TimeRange(startTime:  RationalTime(value: -2, rate: 24),
                             duration: RationalTime(value: 7, rate: 24))
     
        
        XCTAssertEqual(tr.clamped(test_point_min), tr.startTime)
        XCTAssertEqual(tr.clamped(test_point_max), tr.endTimeInclusive())
        XCTAssertEqual(tr.clamped(other_tr), tr)
     
        XCTAssertEqual(tr.clamped(test_point_min),tr.startTime)
        XCTAssertEqual(tr.clamped(test_point_max), tr.endTimeInclusive())
     
        XCTAssertEqual(tr.clamped(other_tr), tr)
    }
    
    func testContains() {
        let tstart = RationalTime(value: 12, rate: 25)
        let tdur = RationalTime(value: 3.3, rate: 25)
        let tr = TimeRange(startTime: tstart, duration: tdur)
     
        XCTAssert(tr.contains(tstart))
        XCTAssertFalse(tr.contains(tstart + tdur))
        XCTAssertFalse(tr.contains(tstart - tdur))
        XCTAssert(tr.contains(tr))
     
        let tr_2 = TimeRange(startTime: tstart - tdur, duration: tdur)
        XCTAssertFalse(tr.contains(tr_2))
        XCTAssertFalse(tr_2.contains(tr))
    }
    
    func testOverlapsRationalTime() {
        let tstart = RationalTime(value: 12, rate: 25)
        let tdur = RationalTime(value: 3, rate: 25)
        let tr = TimeRange(startTime: tstart, duration: tdur)
     
        XCTAssert(tr.overlaps(RationalTime(value: 13, rate: 25)))
        XCTAssertFalse(tr.overlaps(RationalTime(value: 1, rate: 25)))
    }
    
    func testOverlapsTimerange() {
        var tstart = RationalTime(value: 12, rate: 25)
        var tdur = RationalTime(value: 3, rate: 25)
        let tr = TimeRange(startTime: tstart, duration: tdur)
        
        tstart = RationalTime(value: 0, rate: 25)
        tdur = RationalTime(value: 3, rate: 25)
        var tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssertFalse(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: 10, rate: 25)
        tdur = RationalTime(value: 3, rate: 25)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssert(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: 13, rate: 25)
        tdur = RationalTime(value: 1, rate: 25)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssert(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: 2, rate: 25)
        tdur = RationalTime(value: 30, rate: 25)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssert(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: 2, rate: 50)
        tdur = RationalTime(value: 60, rate: 50)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssert(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: 2, rate: 50)
        tdur = RationalTime(value: 14, rate: 50)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssertFalse(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: -100, rate: 50)
        tdur = RationalTime(value: 400, rate: 50)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssert(tr.overlaps(tr_t))
        
        tstart = RationalTime(value: 100, rate: 50)
        tdur = RationalTime(value: 400, rate: 50)
        tr_t = TimeRange(startTime: tstart, duration: tdur)
        
        XCTAssertFalse(tr.overlaps(tr_t))
    }
    
    func testRangeFromStartEndTime() {
        let tstart = RationalTime(value: 0, rate: 25)
        let tend = RationalTime(value: 12, rate: 25)
        
        let tr = TimeRange.rangeFrom(startTime: tstart, endTimeExclusive: tend)
        XCTAssertEqual(tr.startTime, tstart)
        XCTAssertEqual(tr.duration, tend)
        
        XCTAssertEqual(tr.endTimeExclusive(), tend)
        XCTAssertEqual(tr.endTimeInclusive(), tend - RationalTime(value: 1, rate: 25))
        
        XCTAssertEqual(tr, TimeRange.rangeFrom(startTime: tr.startTime, endTimeExclusive: tr.endTimeExclusive()))
    }

    func testAdjacentTimeRanges() {
        let d1 = 0.3
        let d2 = 0.4
        let r1 = TimeRange(startTime:  RationalTime(value: 0, rate: 1), duration:  RationalTime(value: d1, rate: 1))

        let r2 = TimeRange(startTime: r1.endTimeExclusive(), duration: RationalTime(value: d2, rate: 1))
        let full = TimeRange(startTime: RationalTime(value: 0, rate: 1),
                             duration:  RationalTime(value: d1 + d2, rate: 1))
        XCTAssertFalse(r1.overlaps(r2))
        XCTAssertEqual(r1.extended(by: r2), full)
    }

    
    func testDistantTimeranges() {
        let start = 0.1
        let d1 = 0.3
        let gap = 1.7
        let d2 = 0.4
        let r1 = TimeRange(startTime: RationalTime(value: start, rate: 1),
                           duration: RationalTime(value: d1, rate: 1))
        let r2 = TimeRange(startTime:  RationalTime(value: start + gap + d1, rate: 1),
                           duration:  RationalTime(value: d2, rate: 1))

        let full = TimeRange(startTime: RationalTime(value: start, rate: 1), duration:  RationalTime(value: d1 + gap + d2, rate: 1))

        XCTAssertFalse(r1.overlaps(r2))
        XCTAssertEqual(full, r1.extended(by: r2))
        XCTAssertEqual(full, r2.extended(by: r1))
    }

}
