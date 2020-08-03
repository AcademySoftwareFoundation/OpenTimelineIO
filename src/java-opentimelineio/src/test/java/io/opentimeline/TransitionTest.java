package io.opentimeline;

import io.opentimeline.opentimelineio.Any;
import io.opentimeline.opentimelineio.AnyDictionary;
import io.opentimeline.opentimelineio.Transition;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class TransitionTest {

    @Test
    public void testConstructor(){

        AnyDictionary metadata = new AnyDictionary();
        Any any = new Any("bar");
        System.out.println(any.getAnyTypeClass());
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

}
