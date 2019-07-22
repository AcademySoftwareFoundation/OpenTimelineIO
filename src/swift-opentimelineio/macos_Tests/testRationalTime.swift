//
//  macos_Tests.swift
//  macos_Tests
//
//  Created by David Baraff on 1/10/19.
//

import XCTest
@testable import otio

class testRationalTime: XCTestCase {
    func testCreate() {
        let tVal = 30.2
        let t = RationalTime(value: tVal)
        XCTAssertEqual(t.value, tVal)
        
        let t2 = RationalTime()
        XCTAssertEqual(t2.value, 0)
        XCTAssertEqual(t2.rate, 1)
    }
    
    func testEquality() {
        let t1 = RationalTime(value: 30.2)
        XCTAssertEqual(t1, t1)
        let t2 = RationalTime(value: 30.2)
        XCTAssertEqual(t1, t2)
    }
    
    func testInequality() {
        let t1 = RationalTime(value: 30.2)
        XCTAssertEqual(t1, t1)
        let t2 = RationalTime(value: 33.2)
        XCTAssertNotEqual(t1, t2)
        
        let t3 = RationalTime(value: 30.2)
        XCTAssertFalse(t1 != t3)
    }

    func testComparison() {
        let t1 = RationalTime(value: 15.2)
        var t2 = RationalTime(value: 15.6)
        XCTAssert(t1 < t2)
        XCTAssert(t1 <= t2)
        XCTAssertFalse(t1 > t2)
        XCTAssertFalse(t1 >= t2)
        
        // Ensure the equality case of the comparisons works correctly
        let t3 = RationalTime(value: 30.4, rate: 2)
        XCTAssert(t1 <= t3)
        XCTAssert(t1 >= t3)
        XCTAssert(t3 <= t1)
        XCTAssert(t3 >= t1)
        
        // test implicit base conversion
        t2 = RationalTime(value: 15.6, rate: 48)
        XCTAssert(t1 > t2)
        XCTAssert(t1 >= t2)
        XCTAssertFalse(t1 < t2)
        XCTAssertFalse(t1 <= t2)
    }
    
    func testBaseConversion() {
        // from a number
        var t = RationalTime(value: 10, rate: 24)
        XCTAssertEqual(t.rate, 24)
        
        t = t.rescaled(to: 48)
        XCTAssertEqual(t.rate, 48)
     
        // from another RationalTime
        t = RationalTime(value: 10, rate: 24)
        let t2 = RationalTime(value: 20, rate: 48)
        t = t.rescaled(to: t2)
        XCTAssertEqual(t.rate, t2.rate)
    }
    
    func testTimecodeConvert() {
        XCTAssertThrowsError(try RationalTime.from(timecode: "abc", rate: 24))
        
        let timecode = "00:06:56:17"
        let t = try! RationalTime.from(timecode: timecode, rate: 24)
        XCTAssertEqual(timecode, try! t.toTimecode())
    }
    
    func testTimecode24() {
        var timecode = "00:00:01:00"
        var t = RationalTime(value: 24, rate: 24)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 24))
        
        timecode = "00:01:00:00"
        t = RationalTime(value: 24 * 60, rate: 24)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 24))
     
        timecode = "01:00:00:00"
        t = RationalTime(value: 24 * 60 * 60, rate: 24)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 24))
     
        timecode = "24:00:00:00"
        t = RationalTime(value: 24 * 60 * 60 * 24, rate: 24)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 24))
     
        timecode = "23:59:59:23"
        t = RationalTime(value: 24 * 60 * 60 * 24 - 1, rate: 24)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 24))
    }
    
    func testPlusEquals() {
        var sum1 = RationalTime()
        var sum2 = RationalTime()
     
        for i in 0...10 {
            let incr = RationalTime(value: Double(i+1), rate: 24)
            sum1 += incr
            sum2 = sum2 + incr
        }
     
        XCTAssertEqual(sum1, sum2)
    }
    
    func testTimeTimecodeZero() {
        let t = RationalTime()
        let timecode = "00:00:00:00"
        XCTAssertEqual(timecode, try! t.toTimecode(rate: 24))
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 24))
    }
    
     func testLongRunningTimecode24() {
        let finalFrameNumber = 24 * 60 * 60 * 24 - 1
        let finalTime = RationalTime.from(frame: finalFrameNumber, rate: 24)
        let f2 = RationalTime.from(frame: Double(finalFrameNumber), rate: 24)
        XCTAssertEqual(finalTime, f2)
        XCTAssertEqual(try! finalTime.toTimecode(rate: 24), "23:59:59:23")

        let stepTime = RationalTime(value: 1, rate: 24)
        var cumulativeTime = RationalTime(value: 0, rate: 24)
        for _ in 0..<finalFrameNumber {
            cumulativeTime += stepTime
        }
        XCTAssertEqual(cumulativeTime, finalTime)
    
        var fnum = 1113
        while fnum < finalFrameNumber {
            defer { fnum += 1113 }
            let rt = RationalTime.from(frame: fnum, rate: 24)
            let tc = try! rt.toTimecode()
            let rt2 = try! RationalTime.from(timecode: tc, rate: 24)
            XCTAssertEqual(rt, rt2)
            XCTAssertEqual(tc, try! rt2.toTimecode())
        }
    }
    
    func testTimecode23976FPS() {
        // This should behave exactly like 24 fps
        var timecode = "00:00:01:00"
        var t = RationalTime(value: 24, rate: 23.976)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 23.976))
     
        timecode = "00:01:00:00"
        t = RationalTime(value: 24 * 60, rate: 23.976)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 23.976))

        timecode = "01:00:00:00"
        t = RationalTime(value: 24 * 60 * 60, rate: 23.976)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 23.976))
     
        timecode = "24:00:00:00"
        t = RationalTime(value: 24 * 60 * 60 * 24, rate: 23.976)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 23.976))
     
        timecode = "23:59:59:23"
        t = RationalTime(value: 24 * 60 * 60 * 24 - 1, rate: 23.976)
        XCTAssertEqual(t, try! RationalTime.from(timecode: timecode, rate: 23.976))
    }
 
    func testConvertingNegativeValuesToTimecode() {
        let t = RationalTime(value: -1, rate: 25)
        try XCTAssertThrowsError(t.toTimecode(rate: 25))
    }
    
    func testFaultyFormattedTimecode2997() {
        // Test if "faulty" passed ":" in tc gets converted to ";"
        let refColonValues = [
            (10789, "00:05:59:29", "00:05:59;29"),
            (10790, "00:06:00:02", "00:06:00;02"),
            (17981, "00:09:59:29", "00:09:59;29"),
            (17982, "00:10:00:00", "00:10:00;00"),
            (17983, "00:10:00:01", "00:10:00;01"),
            (17984, "00:10:00:02", "00:10:00;02")
        ]
     
        for (value, colon_tc, tc) in refColonValues {
            let t = RationalTime(value: Double(value), rate: 29.97)
            XCTAssertEqual(tc, try t.toTimecode(rate: 29.97))
            let to_tc = try! t.toTimecode(rate: 29.97)
            XCTAssertNotEqual(colon_tc, to_tc)
            let t1 = try! RationalTime.from(timecode: tc, rate: 29.97)
            XCTAssertEqual(t, t1)
        }
    }
    
    func testFaultyFormattedTimecode24() {
        try XCTAssertThrowsError(RationalTime.from(timecode: "01:00:13;23", rate: 24))
    }

    func testInvalidToTimecode() {
        let t = RationalTime(value: 100, rate: 29.98)
     
        try XCTAssertThrowsError(t.toTimecode(rate: 29.98))
        try XCTAssertThrowsError(t.toTimecode())
    }
     
    func testTimeString24() {
        var time_string = "00:00:00.041667"
        var t = RationalTime(value: 1.0, rate: 24)
        var timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "00:00:01"
        t = RationalTime(value: 24, rate: 24)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "00:01:00"
        t = RationalTime(value: 24 * 60, rate: 24)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "01:00:00"
        t = RationalTime(value: 24 * 60 * 60, rate: 24)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "24:00:00"
        t = RationalTime(value: 24 * 60 * 60 * 24, rate: 24)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        
        time_string = "23:59:59.958333"
        t = RationalTime(value: 24 * 60 * 60 * 24 - 1, rate: 24)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
    }
    
    func testTimeString25() {
        var time_string = "00:00:01"
        var t = RationalTime(value: 25, rate: 25)
        var timeObj = try! RationalTime.from(timestring: time_string, rate: 25)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "00:01:00"
        t = RationalTime(value: 25*60, rate: 25)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 25)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "01:00:00"
        t = RationalTime(value: 25*60*60, rate: 25)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 25)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "24:00:00"
        t = RationalTime(value: 25*60*60*24, rate: 25)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 25)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
        
        time_string = "23:59:59.92"
        t = RationalTime(value: 25*60*60*24 - 2, rate: 25)
        timeObj = try! RationalTime.from(timestring: time_string, rate: 25)
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
    }
    
    func testTimeStringZero() {
        let t = RationalTime()
        let time_string = "00:00:00.0"
        let timeObj = try! RationalTime.from(timestring: time_string, rate: 24)
        XCTAssertEqual(time_string, t.toTimestring())
        XCTAssert(t.almostEqual(timeObj, delta: 0.001))
    }
    
    func testLongRunningTimeString24() {
        let final_frame_number = 24 * 60 * 60 * 24 - 1
        let final_time = RationalTime.from(frame: Double(final_frame_number), rate: 24)
        XCTAssertEqual(final_time.toTimestring(), "23:59:59.958333")
        
        let step_time = RationalTime(value: 1, rate: 24)
        var cumTime = RationalTime(value: 0, rate: 24)
        for _ in 0..<final_frame_number {
            cumTime += step_time
        }
        XCTAssert(cumTime.almostEqual(final_time, delta: 0.001))
        
        var fnum = 1113
        while fnum < final_frame_number {
            defer {fnum += 1113}
            let rt = RationalTime.from(frame: fnum, rate: 24)
            let tc = rt.toTimestring()
            let rt2 = try! RationalTime.from(timestring: tc, rate: 24)
            XCTAssertEqual(rt, rt2)
            XCTAssertEqual(tc, rt2.toTimestring())
        }
    }
    
    func testTimeString23976fps() {
        // This list is rewritten from conversion into seconds of
        // test_timecode_23976_fps
        let ref_values_23976 = [
            (1025, "00:00:01.708333"),
            (179900, "00:04:59.833333"),
            (180000, "00:05:00.0"),
            (360000, "00:10:00.0"),
            (720000, "00:20:00.0"),
            (1079300, "00:29:58.833333"),
            (1080000, "00:30:00.0"),
            (1080150, "00:30:00.25"),
            (1440000, "00:40:00.0"),
            (1800000, "00:50:00.0"),
            (1978750, "00:54:57.916666"),
            (1980000, "00:55:00.0"),
            (46700, "00:01:17.833333"),
            (225950, "00:06:16.583333"),
            (436400, "00:12:07.333333"),
            (703350, "00:19:32.25") ]

        for (value, ts) in ref_values_23976 {
            let t = RationalTime(value: Double(value), rate: 600)
            XCTAssertEqual(ts, t.toTimestring())
        }
    }
    
    func testSeconds() {
        let s1 = 1834
        let t1 = RationalTime.from(seconds: Double(s1))
        XCTAssertEqual(t1.value, 1834)
        XCTAssertEqual(t1.rate, 1)
        let t1_as_seconds = t1.toSeconds()
        XCTAssertEqual(Double(t1_as_seconds), Double(s1))
        XCTAssertEqual(t1.value / t1.rate, Double(s1))
     
        let s2 = 248474.345
        let t2 = RationalTime.from(seconds: Double(s2))
        XCTAssertEqual(t2.value, s2)
        XCTAssertEqual(t2.rate, 1.0, accuracy: 0.001)
        let t2_as_seconds = t2.toSeconds()
        XCTAssertEqual(s2, t2_as_seconds)
        XCTAssertEqual(t2.value / t2.rate, s2, accuracy: 0.001)
     
        let v3 = 3459
        let r3 = 24
        let s3 = Double(3459) / Double(24)
        let t3 = RationalTime(value: Double(v3), rate: Double(r3))
        let t4 = RationalTime.from(seconds: Double(s3))
        XCTAssertEqual(t3.toSeconds(), s3)
        XCTAssertEqual(t4.toSeconds(), s3)
    }
    
    func testDuration() {
        var start_time = RationalTime.from(frame: 100, rate: 24)
        var end = RationalTime.from(frame: 200, rate: 24)
        var duration = RationalTime.durationFrom(startTime: start_time, endTime: end)
        XCTAssertEqual(duration, RationalTime.from(frame: 100, rate: 24))

        start_time = RationalTime.from(frame: 0, rate: 1)
        end = RationalTime.from(frame: 200, rate: 24)
        duration = RationalTime.durationFrom(startTime: start_time, endTime: end)
        XCTAssertEqual(duration, RationalTime.from(frame: 200, rate: 24))
    }

    func testMath() {
        var a = RationalTime.from(frame: 100, rate: 24)
        let gap = RationalTime.from(frame: 50, rate: 24)
        let b = RationalTime.from(frame: 150, rate: 24)
        XCTAssertEqual(b - a, gap)
        XCTAssertEqual(a + gap, b)
        XCTAssertEqual(b - gap, a)
     
        a += gap
        XCTAssertEqual(a, b)
     
        a = RationalTime.from(frame: 100, rate: 24)
        let step = RationalTime.from(frame: 1, rate: 24)
        for _ in 0..<50 {
            a += step
        }
        XCTAssertEqual(a, RationalTime.from(frame: 150, rate: 24))
    }
    
    func testMathWithDifferentScales() {
        let a = RationalTime.from(frame: 100, rate: 24)
        let gap = RationalTime.from(frame: 100, rate: 48)
        let b = RationalTime.from(frame: 75, rate: 12)
        
        XCTAssertEqual(b - a, gap.rescaled(to: 24))
        XCTAssertEqual(a + gap, b.rescaled(to: 48))
        
        var gap2 = gap
        gap2 += a
        XCTAssertEqual(gap2, a + gap)
        XCTAssertEqual(b - gap, a.rescaled(to: 48))
    }
    
    func testDurationFromStartEndTime() {
        let tend = RationalTime(value: 12, rate: 25)
        let tdur = RationalTime.durationFrom(startTime: RationalTime(value: 0, rate: 25), endTime: tend)
        XCTAssertEqual(tend, tdur)
    }
    
    func testSubtractWithDifferentRates() {
        let t1 = RationalTime(value: 12, rate: 10)
        let t2 = RationalTime(value: 12, rate: 5)
        XCTAssertEqual((t1 - t2).value, -12)
    }
    
    func testToTimecodeMixedRates() {
        let  timecode = "00:06:56:17"
        let t = try! RationalTime.from(timecode: timecode, rate: 24)
        XCTAssertEqual(timecode, try! t.toTimecode())
        XCTAssertEqual(timecode, try! t.toTimecode(rate: 24))
        XCTAssertNotEqual(timecode, try! t.toTimecode(rate: 12))
    }
    
    func testToFramesMixed() {
        let frame = 100
        let t = RationalTime.from(frame: frame, rate: 24)
        XCTAssertEqual(frame, t.toFrames())
        XCTAssertEqual(frame, t.toFrames(rate: 24))
        XCTAssertNotEqual(frame, t.toFrames(rate: 12))
    }

}
