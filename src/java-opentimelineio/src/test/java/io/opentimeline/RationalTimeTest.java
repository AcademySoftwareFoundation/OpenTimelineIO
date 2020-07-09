package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class RationalTimeTest {
    @Test
    public void testCreate() {
        RationalTime t = new RationalTime();
        assertEquals(t.getValue(), 0);
        assertEquals(t.getRate(), 1);

        t = new RationalTime(30, 1);
        assertEquals(t.getValue(), 30);
        assertEquals(t.getRate(), 1);

        t = new RationalTime.RationalTimeBuilder()
                .setValue(32)
                .build();
        assertEquals(t.getValue(), 32);
        assertEquals(t.getRate(), 1);

        t = new RationalTime.RationalTimeBuilder()
                .setRate(29.97)
                .build();
        assertEquals(t.getValue(), 0);
        assertEquals(t.getRate(), 29.97);
    }
}
