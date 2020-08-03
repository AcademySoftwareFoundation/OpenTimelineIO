package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class TransitionTest {

    @Test
    public void testConstructor(){

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
    }

    @Test
    public void testSerialize(){
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
        SerializableObject decoded = SerializableObject.fromJSONString(encoded,errorStatus);
        assertTrue(decoded.isEquivalentTo(transition));
    }

}
