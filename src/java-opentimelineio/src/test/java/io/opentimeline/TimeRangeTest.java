//package io.opentimeline;
//
//import static org.junit.jupiter.api.Assertions.*;
//
//import io.opentimeline.opentime.ErrorStatus;
//import io.opentimeline.opentime.IsDropFrameRate;
//import io.opentimeline.opentime.RationalTime;
//import io.opentimeline.opentime.TimeRange;
//import org.junit.jupiter.api.Test;
//
//public class TimeRangeTest {
//    @Test
//    public void testCreate() {
//        TimeRange tr = new TimeRange();
//        RationalTime blank = new RationalTime();
//        assertTrue(tr.getStartTime().equals(blank));
//        assertTrue(tr.getDuration().equals(blank));
//
//        TimeRange tr1 = new TimeRange(new RationalTime(10, 48));
//        assertEquals(tr1.getStartTime().getRate(), tr1.getDuration().getRate());
//
//        TimeRange tr2 = new TimeRange.TimeRangeBuilder()
//                .setDuration(new RationalTime(10, 48))
//                .build();
//        assertEquals(tr2.getStartTime().getRate(), tr2.getDuration().getRate());
//    }
//
//    @Test
//    public void testExtendedBy() {
//        /* base 25 is just for testing */
//
//        /* range starts at 0 and has duration 0 */
//        TimeRange tr = new TimeRange(new RationalTime(0, 25));
//        assertTrue(tr.getDuration().equals(new RationalTime()));
//    }
//
//    @Test
//    public void testEndTime() {
//        /* test whole number duration */
//        RationalTime rtStart = new RationalTime(1, 24);
//        RationalTime rtDur = new RationalTime(5, 24);
//        TimeRange tr = new TimeRange(rtStart, rtDur);
//        assertTrue(tr.getDuration().equals(rtDur));
//        assertTrue(tr.endTimeExclusive().equals(rtStart.add(rtDur)));
//        assertTrue(tr.endTimeInclusive().equals(rtStart.add(rtDur).subtract(new RationalTime(1, 24))));
//
//        /* test non-integer duration values */
//        rtDur = new RationalTime(5.5, 24);
//        tr = new TimeRange(rtStart, rtDur);
//        assertTrue(tr.endTimeExclusive().equals(rtStart.add(rtDur)));
//        assertTrue(tr.endTimeInclusive().equals(new RationalTime(6, 24)));
//    }
//
//    @Test
//    public void testCompare() {
//        RationalTime startTime1 = new RationalTime(18, 24);
//        RationalTime duration1 = new RationalTime(7, 24);
//        TimeRange tr1 = new TimeRange(startTime1, duration1);
//        RationalTime startTime2 = new RationalTime(18, 24);
//        RationalTime duration2 = new RationalTime(14, 48);
//        TimeRange tr2 = new TimeRange(startTime2, duration2);
//        assertTrue(tr1.equals(tr2));
//        assertFalse(tr1.notEquals(tr2));
//
//        RationalTime startTime3 = new RationalTime(20, 24);
//        RationalTime duration3 = new RationalTime(3, 24);
//        TimeRange tr3 = new TimeRange(startTime3, duration3);
//        assertFalse(tr1.equals(tr3));
//        assertTrue(tr1.notEquals(tr3));
//    }
//
//    @Test
//    public void testClamped() {
//        RationalTime testPointMin = new RationalTime(-2, 24);
//        RationalTime testPointMax = new RationalTime(6, 24);
//
//        TimeRange tr = new TimeRange(new RationalTime(-1, 24), new RationalTime(6, 24));
//        TimeRange otherTr = new TimeRange(new RationalTime(-2, 24), new RationalTime(7, 24));
//
//        assertTrue(tr.clamped(testPointMin).equals(tr.getStartTime()));
//        assertTrue(tr.clamped(testPointMax).equals(tr.endTimeInclusive()));
//
//        assertTrue(tr.clamped(otherTr).equals(tr));
//
//        assertTrue(tr.clamped(testPointMin).equals(tr.getStartTime()));
//        assertTrue(tr.clamped(testPointMax).equals(tr.endTimeInclusive()));
//    }
//
//    @Test
//    public void testContains() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3.3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.contains(tStart));
//        assertFalse(tr.contains(tStart.add(tDur)));
//        assertFalse(tr.contains(tStart.subtract(tDur)));
//
//        assertTrue(tr.contains(tr));
//
//        TimeRange tr2 = new TimeRange(tStart.subtract(tDur), tDur);
//        assertFalse(tr.contains(tr2));
//        assertFalse(tr2.contains(tr));
//    }
//
//    @Test
//    public void testOverlapsRationalTime() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.overlaps(new RationalTime(13, 25)));
//        assertFalse(tr.overlaps(new RationalTime(1, 25)));
//    }
//
//    @Test
//    public void testOverlapsTimeRange() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        tStart = new RationalTime(0, 25);
//        tDur = new RationalTime(3, 25);
//        TimeRange tr_t = new TimeRange(tStart, tDur);
//
//        assertFalse(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(10, 25);
//        tDur = new RationalTime(3, 25);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(13, 25);
//        tDur = new RationalTime(1, 25);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(2, 25);
//        tDur = new RationalTime(30, 25);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(2, 50);
//        tDur = new RationalTime(60, 50);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(2, 50);
//        tDur = new RationalTime(14, 50);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertFalse(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(-100, 50);
//        tDur = new RationalTime(400, 50);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.overlaps(tr_t));
//
//        tStart = new RationalTime(100, 50);
//        tDur = new RationalTime(400, 50);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertFalse(tr.overlaps(tr_t));
//    }
//
//    @Test
//    public void testBeforeTimeRange() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        tStart = new RationalTime(10, 25);
//        tDur = new RationalTime(1.5, 25);
//        TimeRange tr_t = new TimeRange(tStart, tDur);
//        assertTrue(tr_t.before(tr));
//        assertFalse(tr.before(tr_t));
//
//        tDur = new RationalTime(12, 25);
//        tr_t = new TimeRange(tStart, tDur);
//        assertFalse(tr_t.before(tr));
//        assertFalse(tr.before(tr_t));
//    }
//
//    @Test
//    public void testBeforeRationalTime() {
//        RationalTime tAfter = new RationalTime(15, 25);
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        assertFalse(tr.before(tAfter));
//        assertFalse(tr.before(tStart));
//
//        tDur = new RationalTime(1.99, 25);
//        tr = new TimeRange(tStart, tDur);
//        assertTrue(tr.before(tAfter));
//    }
//
//    @Test
//    public void testMeets() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//        tStart = new RationalTime(15, 25);
//        TimeRange tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.meets(tr_t));
//        assertFalse(tr_t.meets(tr));
//
//        tStart = new RationalTime(14.99, 25);
//        tDur = new RationalTime(0, 25);
//        tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr_t.meets(tr_t));
//    }
//
//    @Test
//    public void testBeginsTimeRange() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//        tDur = new RationalTime(5, 25);
//        TimeRange tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.begins(tr_t));
//        assertFalse(tr_t.begins(tr));
//        assertFalse(tr.begins(tr));
//
//        tDur = new RationalTime(0, 25);
//        tr = new TimeRange(tStart, tDur);
//        assertTrue(tr.begins(tr_t));
//        assertFalse(tr.begins(tr));
//
//        tStart = new RationalTime(30, 25);
//        tr_t = new TimeRange(tStart, tDur);
//        assertFalse(tr.begins(tr_t));
//
//        tStart = new RationalTime(13, 25);
//        tr_t = new TimeRange(tStart, tDur);
//        tDur = new RationalTime(3, 25);
//        tStart = new RationalTime(12, 25);
//        tr = new TimeRange(tStart, tDur);
//        assertFalse(tr_t.begins(tr));
//    }
//
//    @Test
//    public void testBeginsRationalTime() {
//        RationalTime tEnd = new RationalTime(15, 25);
//        RationalTime tBefore = new RationalTime(11.9, 25);
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.begins(tStart));
//        assertFalse(tr.begins(tEnd));
//        assertFalse(tr.begins(tBefore));
//    }
//
//    @Test
//    public void testFinishesTimeRange() {
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//        tStart = new RationalTime(13, 25);
//        tDur = new RationalTime(2, 25);
//        TimeRange tr_t = new TimeRange(tStart, tDur);
//
//        assertTrue(tr_t.finishes(tr));
//        assertFalse(tr.finishes(tr_t));
//        assertFalse(tr.finishes(tr));
//
//        tDur = new RationalTime(1, 25);
//        tr_t = new TimeRange(tStart, tDur);
//        assertFalse(tr_t.finishes(tr));
//
//        tStart = new RationalTime(30, 25);
//        tr_t = new TimeRange(tStart, tDur);
//        assertFalse(tr_t.finishes(tr));
//
//        tStart = new RationalTime(15, 25);
//        tDur = new RationalTime(0, 25);
//        tr_t = new TimeRange(tStart, tDur);
//        assertTrue(tr_t.finishes(tr));
//    }
//
//    @Test
//    public void testFinishesRationalTime() {
//        RationalTime tAfter = new RationalTime(16, 25);
//        RationalTime tEnd = new RationalTime(15, 25);
//        RationalTime tStart = new RationalTime(12, 25);
//        RationalTime tDur = new RationalTime(3, 25);
//        TimeRange tr = new TimeRange(tStart, tDur);
//
//        assertTrue(tr.finishes(tEnd));
//        assertFalse(tr.finishes(tStart));
//        assertFalse(tr.finishes(tAfter));
//    }
//
//    @Test
//    public void testRangeFromStartEndTime() {
//        RationalTime tStart = new RationalTime(0, 25);
//        RationalTime tEnd = new RationalTime(12, 25);
//
//        TimeRange tr = TimeRange.rangeFromStartEndTime(tStart, tEnd);
//
//        assertTrue(tr.getStartTime().equals(tStart));
//        assertTrue(tr.getDuration().equals(tEnd));
//
//        assertTrue(tr.endTimeExclusive().equals(tEnd));
//        assertTrue(tr.endTimeInclusive().equals(tEnd.subtract(new RationalTime(1, 25))));
//
//        assertTrue(tr.equals(TimeRange.rangeFromStartEndTime(tr.getStartTime(), tr.endTimeExclusive())));
//    }
//
//    @Test
//    public void testAdjacentTimeRanges() {
//        double d1 = 0.3;
//        double d2 = 0.4;
//
//        TimeRange r1 = new TimeRange(new RationalTime(0, 1), new RationalTime(d1, 1));
//        TimeRange r2 = new TimeRange(r1.endTimeExclusive(), new RationalTime(d2, 1));
//        TimeRange full = new TimeRange(new RationalTime(0, 1), new RationalTime(d1 + d2, 1));
//
//        assertFalse(r1.overlaps(r2));
//        assertTrue(r1.extendedBy(r2).equals(full));
//    }
//
//    @Test
//    public void testDistantTimeRanges() {
//        double start = 0.1;
//        double d1 = 0.3;
//        double gap = 1.7;
//        double d2 = 0.4;
//        TimeRange r1 = new TimeRange(new RationalTime(start, 1), new RationalTime(d1, 1));
//        TimeRange r2 = new TimeRange(new RationalTime(start + gap + d1, 1), new RationalTime(d2, 1));
//        TimeRange full = new TimeRange(new RationalTime(start, 1), new RationalTime(d1 + gap + d2, 1));
//        assertFalse(r1.overlaps(r2));
//        assertTrue(full.equals(r1.extendedBy(r2)));
//        assertTrue(full.equals(r2.extendedBy(r1)));
//    }
//
//    @Test
//    public void testToTimecodeMixedRates() {
//        String timecode = "00:06:56:17";
//        ErrorStatus errorStatus = new ErrorStatus();
//        RationalTime t = RationalTime.fromTimecode(timecode, 24, errorStatus);
//
//        assertEquals(timecode, t.toTimecode(errorStatus));
//        assertEquals(timecode, t.toTimecode(24, IsDropFrameRate.InferFromRate, errorStatus));
//        assertNotEquals(timecode, t.toTimecode(12, IsDropFrameRate.InferFromRate, errorStatus));
//
//        RationalTime time1 = new RationalTime(24, 24);
//        RationalTime time2 = new RationalTime(1, 1);
//        assertEquals(time1.toTimecode(24, IsDropFrameRate.InferFromRate, errorStatus), time2.toTimecode(24, IsDropFrameRate.InferFromRate, errorStatus));
//    }
//
//    @Test
//    public void testToFramesMixedRates() {
//        int frame = 100;
//        RationalTime t = RationalTime.fromFrames(frame, 24);
//        assertEquals(frame, t.toFrames());
//        assertEquals(frame, t.toFrames(24));
//        assertNotEquals(frame, t.toFrames(12));
//    }
//}
