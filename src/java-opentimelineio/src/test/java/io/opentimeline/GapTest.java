package io.opentimeline;

import io.opentimeline.opentimelineio.ErrorStatus;
import io.opentimeline.opentimelineio.Gap;
import io.opentimeline.opentimelineio.SerializableObject;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class GapTest {

    @Test
    public void testSerialize() {
        Gap gap = new Gap.GapBuilder().build();
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = gap.toJSONString(errorStatus);
        Gap decoded = (Gap) SerializableObject.fromJSONString(encoded, errorStatus);
        assertEquals(gap, decoded);
        try {
            gap.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        Gap gap = new Gap.GapBuilder().build();
        assertEquals(gap.toString(),
                "io.opentimeline.opentimelineio.Gap(" +
                        "name=, " +
                        "sourceRange=io.opentimeline.opentime.TimeRange(" +
                        "startTime=io.opentimeline.opentime.RationalTime(value=0.0, rate=1.0), " +
                        "duration=io.opentimeline.opentime.RationalTime(value=0.0, rate=1.0)), " +
                        "effects=[], " +
                        "markers=[], " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
        try {
            gap.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
