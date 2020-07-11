package io.opentimeline;

import static org.junit.jupiter.api.Assertions.*;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import org.junit.jupiter.api.Test;

public class TimeRangeTest {
    @Test
    public void testCreate() {
        TimeRange tr = new TimeRange();
        RationalTime blank = new RationalTime();
        assertTrue(tr.getStartTime().equals(blank));
        assertTrue(tr.getDuration().equals(blank));

        TimeRange tr1 = new TimeRange(new RationalTime(10, 48));
        assertEquals(tr1.getStartTime().getRate(), tr1.getDuration().getRate());

        TimeRange tr2 = new TimeRange.TimeRangeBuilder()
                .setDuration(new RationalTime(10, 48))
                .build();
        assertEquals(tr2.getStartTime().getRate(), tr2.getDuration().getRate());
    }

    @Test
    public void testExtendedBy() {
        /* base 25 is just for testing */

        /* range starts at 0 and has duration 0 */
        TimeRange tr = new TimeRange(new RationalTime(0, 25));
        assertTrue(tr.getDuration().equals(new RationalTime()));
    }

    @Test
    public void testEndTime() {
        /* test whole number duration */
        RationalTime rtStart = new RationalTime(1, 24);
        RationalTime rtDur = new RationalTime(5, 24);
        TimeRange tr = new TimeRange(rtStart, rtDur);
        assertTrue(tr.getDuration().equals(rtDur));
        assertTrue(tr.endTimeExclusive().equals(rtStart.add(rtDur)));
        assertTrue(tr.endTimeInclusive().equals(rtStart.add(rtDur).subtract(new RationalTime(1, 24))));

        /* test non-integer duration values */
        rtDur = new RationalTime(5.5, 24);
        tr = new TimeRange(rtStart, rtDur);
        assertTrue(tr.endTimeExclusive().equals(rtStart.add(rtDur)));
        assertTrue(tr.endTimeInclusive().equals(new RationalTime(6, 24)));
    }

    @Test
    public void testCompare() {
        RationalTime startTime1 = new RationalTime(18, 24);
        RationalTime duration1 = new RationalTime(7, 24);
        TimeRange tr1 = new TimeRange(startTime1, duration1);
        RationalTime startTime2 = new RationalTime(18, 24);
        RationalTime duration2 = new RationalTime(14, 48);
        TimeRange tr2 = new TimeRange(startTime2, duration2);
        assertTrue(tr1.equals(tr2));
        assertFalse(tr1.notEquals(tr2));

        RationalTime startTime3 = new RationalTime(20, 24);
        RationalTime duration3 = new RationalTime(3, 24);
        TimeRange tr3 = new TimeRange(startTime3, duration3);
        assertFalse(tr1.equals(tr3));
        assertTrue(tr1.notEquals(tr3));
    }

    @Test
    public void testClamped() {
        RationalTime testPointMin = new RationalTime(-2, 24);
        RationalTime testPointMax = new RationalTime(6, 24);

        TimeRange tr = new TimeRange(new RationalTime(-1, 24), new RationalTime(6, 24));
        TimeRange otherTr = new TimeRange(new RationalTime(-2, 24), new RationalTime(7, 24));

        assertTrue(tr.clamped(testPointMin).equals(tr.getStartTime()));
        assertTrue(tr.clamped(testPointMax).equals(tr.endTimeInclusive()));

        assertTrue(tr.clamped(otherTr).equals(tr));

        assertTrue(tr.clamped(testPointMin).equals(tr.getStartTime()));
        assertTrue(tr.clamped(testPointMax).equals(tr.endTimeInclusive()));
    }

    @Test
    public void testContains() {
        RationalTime tStart = new RationalTime(12, 25);
        RationalTime tDur = new RationalTime(3.3, 25);
        TimeRange tr = new TimeRange(tStart, tDur);

        assertTrue(tr.contains(tStart));
        assertFalse(tr.contains(tStart.add(tDur)));
        assertFalse(tr.contains(tStart.subtract(tDur)));

        assertTrue(tr.contains(tr));

        TimeRange tr2 = new TimeRange(tStart.subtract(tDur), tDur);
        assertFalse(tr.contains(tr2));
        assertFalse(tr2.contains(tr));
    }

    @Test
    public void testOverlapsRationalTime() {
        RationalTime tStart = new RationalTime(12, 25);
        RationalTime tDur = new RationalTime(3, 25);
        TimeRange tr = new TimeRange(tStart, tDur);

        assertTrue(tr.overlaps(new RationalTime(13, 25)));
        assertFalse(tr.overlaps(new RationalTime(1, 25)));
    }

    @Test
    public void testOverlapsTimeRange() {
        RationalTime tStart = new RationalTime(12, 25);
        RationalTime tDur = new RationalTime(3, 25);
        TimeRange tr = new TimeRange(tStart, tDur);

        tStart = new RationalTime(0, 25);
        tDur = new RationalTime(3, 25);
        TimeRange tr_t = new TimeRange(tStart, tDur);

        assertFalse(tr.overlaps(tr_t));

        tStart = new RationalTime(10, 25);
        tDur = new RationalTime(3, 25);
        tr_t = new TimeRange(tStart, tDur);

        assertTrue(tr.overlaps(tr_t));

        tStart = new RationalTime(13, 25);
        tDur = new RationalTime(1, 25);
        tr_t = new TimeRange(tStart, tDur);

        assertTrue(tr.overlaps(tr_t));

        tStart = new RationalTime(2, 25);
        tDur = new RationalTime(30, 25);
        tr_t = new TimeRange(tStart, tDur);

        assertTrue(tr.overlaps(tr_t));

        tStart = new RationalTime(2, 50);
        tDur = new RationalTime(60, 50);
        tr_t = new TimeRange(tStart, tDur);

        assertTrue(tr.overlaps(tr_t));

        tStart = new RationalTime(2, 50);
        tDur = new RationalTime(14, 50);
        tr_t = new TimeRange(tStart, tDur);

        assertFalse(tr.overlaps(tr_t));

        tStart = new RationalTime(-100, 50);
        tDur = new RationalTime(400, 50);
        tr_t = new TimeRange(tStart, tDur);

        assertTrue(tr.overlaps(tr_t));

        tStart = new RationalTime(100, 50);
        tDur = new RationalTime(400, 50);
        tr_t = new TimeRange(tStart, tDur);

        assertFalse(tr.overlaps(tr_t));
    }

    @Test
    public void testBeforeTimeRange() {
        RationalTime tStart = new RationalTime(12, 25);
        RationalTime tDur = new RationalTime(3, 25);
        TimeRange tr = new TimeRange(tStart, tDur);

        tStart = new RationalTime(10, 25);
        tDur = new RationalTime(1.5, 25);
        TimeRange tr_t = new TimeRange(tStart, tDur);
        assertTrue(tr_t.before(tr));
        assertFalse(tr.before(tr_t));

        tDur = new RationalTime(12, 25);
        tr_t = new TimeRange(tStart, tDur);
        assertFalse(tr_t.before(tr));
        assertFalse(tr.before(tr_t));
    }
}
