package io.opentimeline;

import io.opentimeline.opentime.RationalTime;
import io.opentimeline.opentime.TimeRange;
import io.opentimeline.opentime.TimeTransform;
import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class OpenTimeTypeSerializerTest {

    @Test
    public void testSerializeTime() {

        try {
            ErrorStatus errorStatus = new ErrorStatus();

            RationalTime rt = new RationalTime(15, 24);
            Any rtAny = new Any(rt);
            String encoded = Serialization.serializeJSONToString(rtAny, errorStatus);
            Any destination = new Any(new RationalTime());
            assertTrue(Deserialization.deserializeJSONFromString(encoded, destination, errorStatus));
            assertTrue(destination.safelyCastRationalTime().equals(rt));
            destination.close();

            RationalTime rtDur = new RationalTime(10, 20);
            TimeRange tr = new TimeRange(rt, rtDur);
            Any trAny = new Any(tr);
            encoded = Serialization.serializeJSONToString(trAny, errorStatus);
            destination = new Any(new TimeRange());
            assertTrue(Deserialization.deserializeJSONFromString(encoded, destination, errorStatus));
            assertTrue(destination.safelyCastTimeRange().equals(tr));
            destination.close();

            TimeTransform tt = new TimeTransform.TimeTransformBuilder()
                    .setOffset(rt)
                    .setScale(1.5)
                    .build();
            Any ttAny = new Any(tt);
            encoded = Serialization.serializeJSONToString(ttAny, errorStatus);
            destination = new Any(new TimeTransform());
            assertTrue(Deserialization.deserializeJSONFromString(encoded, destination, errorStatus));
            assertTrue(destination.safelyCastTimeTransform().equals(tt));
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

}
