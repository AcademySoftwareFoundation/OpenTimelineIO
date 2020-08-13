package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class TimeTransformTest {

    @Test
    public void testIdentityTransform() {
        RationalTime tStart = new RationalTime(12, 25);
        TimeTransform txForm = new TimeTransform();
        assertTrue(tStart.equals(txForm.appliedTo(tStart)));

        tStart = new RationalTime(12, 25);
        txForm = new TimeTransform.TimeTransformBuilder()
                .setRate(50)
                .build();
        assertEquals(24, txForm.appliedTo(tStart).getValue());
    }

    @Test
    public void testStr() {
        RationalTime tOffset = new RationalTime(10, 25);
        TimeTransform txForm = new TimeTransform.TimeTransformBuilder()
                .setOffset(tOffset)
                .build();
        assertEquals(txForm.toString(),
                "io.opentimeline.opentime.TimeTransform(" +
                        "offset=io.opentimeline.opentime.RationalTime(value=10.0, rate=25.0), " +
                        "scale=1.0, " +
                        "rate=-1.0)");
    }

    @Test
    public void testOffset() {
        RationalTime tStart = new RationalTime(12, 25);
        RationalTime tOffset = new RationalTime(10, 25);
        TimeTransform txForm = new TimeTransform.TimeTransformBuilder()
                .setOffset(tOffset)
                .build();
        assertTrue(tStart.add(tOffset).equals(txForm.appliedTo(tStart)));

        TimeRange tr = new TimeRange(tStart, tStart);
        assertTrue(txForm.appliedTo(tr).equals(new TimeRange(tStart.add(tOffset), tStart)));
    }

    @Test
    public void testScale() {
        RationalTime tStart = new RationalTime(12, 25);
        TimeTransform txForm = new TimeTransform.TimeTransformBuilder()
                .setScale(2)
                .build();
        assertTrue(new RationalTime(24, 25).equals(txForm.appliedTo(tStart)));

        TimeRange tr = new TimeRange(tStart, tStart);
        RationalTime tStartScaled = new RationalTime(24, 25);
        assertTrue(txForm.appliedTo(tr).equals(new TimeRange(tStartScaled, tStartScaled)));
    }

    @Test
    public void testRate() {
        TimeTransform txForm1 = new TimeTransform();
        TimeTransform txForm2 = new TimeTransform.TimeTransformBuilder()
                .setRate(50)
                .build();
        assertEquals(txForm2.getRate(), txForm1.appliedTo(txForm2).getRate());
    }

    @Test
    public void testComparison() {
        RationalTime tStart = new RationalTime(12, 25);
        TimeTransform txForm = new TimeTransform.TimeTransformBuilder()
                .setOffset(tStart)
                .setScale(2)
                .build();
        tStart = new RationalTime(12, 25);
        TimeTransform txForm2 = new TimeTransform.TimeTransformBuilder()
                .setOffset(tStart)
                .setScale(2)
                .build();
        assertTrue(txForm.equals(txForm2));
        assertFalse(txForm.notEquals(txForm2));

        tStart = new RationalTime(23, 25);
        TimeTransform txForm3 = new TimeTransform.TimeTransformBuilder()
                .setOffset(tStart)
                .setScale(2)
                .build();
        assertTrue(txForm.notEquals(txForm3));
        assertFalse(txForm.equals(txForm3));
    }
}
