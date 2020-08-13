package io.opentimeline;

import io.opentimeline.opentimelineio.*;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class EffectTest {

    @Test
    public void testConstructor() {
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        Effect effect = new Effect.EffectBuilder()
                .setName("blur it")
                .setEffectName("blur")
                .setMetadata(metadata)
                .build();
        Any effectAny = new Any(effect);
        ErrorStatus errorStatus = new ErrorStatus();
        Serialization serialization = new Serialization();
        String encoded = serialization.serializeJSONToString(effectAny, errorStatus);
        Effect decoded = (Effect) SerializableObject.fromJSONString(encoded, errorStatus);
        assertTrue(effect.isEquivalentTo(decoded));
        assertEquals(decoded.getName(), "blur it");
        assertEquals(decoded.getEffectName(), "blur");
        assertEquals(decoded.getMetadata().get("foo").safelyCastString(), "bar");
        try {
            metadata.close();
            effect.close();
            effectAny.close();
            errorStatus.close();
            decoded.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testStr() {
        Effect effect = new Effect.EffectBuilder().build();
        assertEquals(effect.toString(),
                "io.opentimeline.opentimelineio.Effect(" +
                        "name=, " +
                        "effectName=, " +
                        "metadata=io.opentimeline.opentimelineio.AnyDictionary{})");
        try {
            effect.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Test
    public void testEq() {
        AnyDictionary metadata = new AnyDictionary();
        metadata.put("foo", new Any("bar"));
        Effect effect = new Effect.EffectBuilder()
                .setName("blur it")
                .setEffectName("blur")
                .setMetadata(metadata)
                .build();
        Effect effect2 = new Effect.EffectBuilder()
                .setName("blur it")
                .setEffectName("blur")
                .setMetadata(metadata)
                .build();
        assertTrue(effect.isEquivalentTo(effect2));
        try {
            metadata.close();
            effect.close();
            effect2.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
