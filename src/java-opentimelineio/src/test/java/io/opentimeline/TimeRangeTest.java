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
}
