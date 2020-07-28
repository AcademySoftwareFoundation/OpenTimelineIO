//package io.opentimeline;
//
//import io.opentimeline.opentimelineio.*;
//import org.junit.jupiter.api.Test;
//
//import static org.junit.jupiter.api.Assertions.*;
//
//public class EffectTest {
//
//    @Test
//    public void testConstructor() {
//        AnyDictionary metadata = new AnyDictionary();
//        metadata.put("foo", new Any("bar"));
//        Effect effect = new Effect.EffectBuilder()
//                .setName("blur it")
//                .setEffectName("blur")
//                .setMetadata(metadata)
//                .build();
//        Any effectAny = new Any(effect);
//        ErrorStatus errorStatus = new ErrorStatus();
//        String encoded = Serialization.serializeJSONToString(effectAny, errorStatus);
//        SerializableObject decoded = SerializableObject.fromJSONString(encoded, errorStatus);
//        Effect decodedEffect = new Effect(decoded);
////        assertTrue(effect.isEquivalentTo(decoded)); // running this gives bad_alloc on line 28
//        assertEquals(decodedEffect.getName(), "blur it");
//        assertEquals(decodedEffect.getEffectName(), "blur");
//        assertEquals(decodedEffect.getMetadata().get("foo").safelyCastString(), "bar");
//    }
//
//    @Test
//    public void testEq() {
//        AnyDictionary metadata = new AnyDictionary();
//        metadata.put("foo", new Any("bar"));
//        Effect effect = new Effect.EffectBuilder()
//                .setName("blur it")
//                .setEffectName("blur")
//                .setMetadata(metadata)
//                .build();
//        Effect effect2 = new Effect.EffectBuilder()
//                .setName("blur it")
//                .setEffectName("blur")
//                .setMetadata(metadata)
//                .build();
//        assertTrue(effect.isEquivalentTo(effect2));
//    }
//}
