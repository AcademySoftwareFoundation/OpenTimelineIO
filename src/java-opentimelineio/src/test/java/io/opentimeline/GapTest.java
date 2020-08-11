package io.opentimeline;

import io.opentimeline.opentimelineio.ErrorStatus;
import io.opentimeline.opentimelineio.Gap;
import io.opentimeline.opentimelineio.SerializableObject;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

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

}
