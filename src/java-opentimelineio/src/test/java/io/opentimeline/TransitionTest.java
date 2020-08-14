package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class TransitionTest {

    @Test
    public void testConstructor() {
        AnyDictionary metadata = new AnyDictionary();
        Any any = new Any("bar");
        metadata.put("foo", any);
        Transition transition = new Transition.TransitionBuilder()
                .setName("AtoB")
                .setTransitionType("SMPTE.Dissolve")
                .setMetadata(metadata)
                .build();

        assertEquals(transition.getTransitionType(), "SMPTE.Dissolve");
        assertEquals(transition.getName(), "AtoB");
        assertTrue(transition.getMetadata().equals(metadata));
        try {
            metadata.close();
            any.close();
            transition.close();//gives double free
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        Transition transition = new Transition.TransitionBuilder().build();
        assertEquals(transition.toString(),
                "io.opentimeline.opentimelineio.Transition(" +
                        "name=, " +
                        "transitionType=, " +
                        "inOffset=io.opentimeline.opentime.RationalTime(value=0.0, rate=1.0), " +
                        "outOffset=io.opentimeline.opentime.RationalTime(value=0.0, rate=1.0), " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
        try {
            transition.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testSerialize() {
        AnyDictionary metadata = new AnyDictionary();
        Any any = new Any("bar");
        metadata.put("foo", any);
        Transition transition = new Transition.TransitionBuilder()
                .setName("AtoB")
                .setTransitionType("SMPTE.Dissolve")
                .setMetadata(metadata)
                .build();
        ErrorStatus errorStatus = new ErrorStatus();
        String encoded = transition.toJSONString(errorStatus);
        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(decoded.isEquivalentTo(transition));
        try {
            metadata.close();
            any.close();
            transition.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}
